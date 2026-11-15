"""Lazy, local-files-only real-model backend. No inference on import."""
import collections
import hashlib
import importlib.metadata
import json
import math
import os
import time
from pathlib import Path
from core import HERE, require


def verify_assets(directory):
    directory = Path(directory).resolve(strict=True)
    lock = json.loads((HERE / "model_lock.json").read_text())
    entries = []
    for expected in lock["files"]:
        p = directory / expected["path"]
        require(p.is_file() and not p.is_symlink(), "Missing/nonregular pinned model asset: " + p.name)
        require(p.stat().st_size == expected["bytes"], "Asset size mismatch: " + p.name)
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if "sha256" in expected:
            require(sha == expected["sha256"], "Model asset SHA256 mismatch")
        if "git_blob_sha1" in expected:
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            require(blob == expected["git_blob_sha1"], "Pinned config/tokenizer identity mismatch")
        entries.append({"path": p.name, "bytes": len(raw), "sha256": sha})
    require(sum(x["bytes"] for x in entries) <= lock["total_cap_bytes"], "Model cap exceeded")
    require(not list(directory.glob("*.bin")) and not list(directory.glob("*.pt")), "Alternate weight formats refused")
    return {"model_id": lock["model_id"], "revision": lock["revision"], "files": entries}


class HFBackend:
    def __init__(self, directory, device, settings):
        require(device in ("cpu", "cuda:0"), "Use the declared CPU or single local GPU")
        require(settings == {"precision": "float32", "autocast": False, "tf32": False,
                             "deterministic_algorithms": True, "attention": "eager", "cpu_threads": 2}, "Unexpected settings")
        start = time.perf_counter()
        self.assets = verify_assets(directory)
        self.verification_seconds = time.perf_counter() - start
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
        import torch
        from transformers import AutoModelForMaskedLM, EsmTokenizer
        self.torch = torch
        torch.set_num_threads(2)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.backends.cudnn.benchmark = False
        torch.set_float32_matmul_precision("highest")
        if device.startswith("cuda"):
            require(torch.cuda.is_available(), "CUDA unavailable; do not repair or silently fall back")
            require(torch.cuda.device_count() == 1, "Expected one assigned GPU")
        self.device = device
        self.calls = collections.Counter()
        self.successful_calls = collections.Counter()
        self.examples = collections.Counter()
        self.failed_positions = []
        self.successful_positions = []
        self.pilot_log_softmax_max_error = 0.0
        self.timings = {phase: {"host_to_device_seconds": 0.0, "compute_seconds": 0.0,
                               "device_to_host_seconds": 0.0} for phase in ("scoring", "pilot", "warmup")}
        start = time.perf_counter()
        self.tokenizer = EsmTokenizer.from_pretrained(str(directory), local_files_only=True)
        self.model = AutoModelForMaskedLM.from_pretrained(
            str(directory), local_files_only=True, use_safetensors=True,
            trust_remote_code=False, torch_dtype=torch.float32, attn_implementation="eager")
        self.load_seconds = time.perf_counter() - start
        start = time.perf_counter()
        self.model.to(device)
        self.sync()
        self.model_transfer_seconds = time.perf_counter() - start
        self.model.eval()
        require(not self.model.training and all(not m.training for m in self.model.modules()), "Model must be in evaluation mode")
        require(all(p.dtype == torch.float32 for p in self.model.parameters() if p.is_floating_point()), "Model precision mismatch")
        self.settings = {**settings, "device": device, "model_eval": True,
                         "inference_mode": True, "token_dropout_from_config": self.model.config.token_dropout,
                         "seed": 0, "vocabulary_log_softmax": "full model vocabulary; float32",
                         "cublas_workspace_config": ":4096:8"}
        self.versions = {name: importlib.metadata.version(name) for name in ("torch", "transformers", "safetensors", "tokenizers")}
        self.hardware = {"device": device, "cuda_runtime": torch.version.cuda,
                         "gpu_name": torch.cuda.get_device_name(0) if device.startswith("cuda") else None,
                         "gpu_capability": list(torch.cuda.get_device_capability(0)) if device.startswith("cuda") else None}
        self.loading_memory = self.memory()
        if device.startswith("cuda"):
            torch.cuda.reset_peak_memory_stats()

    def memory(self):
        if not self.device.startswith("cuda"):
            return {"device": self.device, "cuda_memory": None}
        return {"device": self.device,
                "allocated_bytes": self.torch.cuda.memory_allocated(),
                "reserved_bytes": self.torch.cuda.memory_reserved(),
                "peak_allocated_bytes": self.torch.cuda.max_memory_allocated(),
                "peak_reserved_bytes": self.torch.cuda.max_memory_reserved(),
                "scope": "PyTorch allocator, not whole-device utilization"}

    def sync(self):
        if self.device.startswith("cuda"):
            self.torch.cuda.synchronize()

    def predict(self, examples, offsets, observed_ids, phase):
        torch = self.torch
        require(time.perf_counter() < self.deadline, "Approved time limit or research cutoff reached")
        require(phase in self.timings, "Unknown phase")
        require(len(examples) == len(offsets) == len(observed_ids) and examples, "Invalid batch")
        require(len({len(x) for x in examples}) == 1, "Per-sequence batching requires equal lengths")
        start = time.perf_counter()
        ids = torch.tensor(examples, dtype=torch.long, device=self.device)
        attention = ids.ne(self.tokenizer.pad_token_id).long()
        offsets_t = torch.tensor(offsets, dtype=torch.long, device=self.device)
        targets_t = torch.tensor(observed_ids, dtype=torch.long, device=self.device)
        indices = torch.arange(len(examples), device=self.device)
        self.sync()
        self.timings[phase]["host_to_device_seconds"] += time.perf_counter() - start
        start = time.perf_counter()
        with torch.inference_mode():
            self.calls[phase] += 1  # Counts the actual attempted model forward, not examples.
            logits = self.model(input_ids=ids, attention_mask=attention).logits
            require(logits.shape[:2] == ids.shape, "Model output/token dimensions disagree")
            selected = logits[indices, offsets_t, :].float()
            values = torch.log_softmax(selected, dim=-1)[indices, targets_t]
            if phase == "pilot":
                # Same forward, independent float64 logsumexp calculation; no hidden test forward.
                reference = selected.double()[indices, targets_t] - torch.logsumexp(selected.double(), dim=-1)
                error = (values.double() - reference).abs()
                tolerance = self.pilot_tolerances["log_probability_abs"] + self.pilot_tolerances["log_probability_rel"] * torch.maximum(values.double().abs(), reference.abs())
                require(bool(torch.all(error <= tolerance).item()), "Real-model log-softmax/logsumexp cross-check failed")
                self.pilot_log_softmax_max_error = max(self.pilot_log_softmax_max_error, error.max().item())
        self.sync()
        self.timings[phase]["compute_seconds"] += time.perf_counter() - start
        start = time.perf_counter()
        result = values.detach().cpu().tolist()
        self.sync()
        self.timings[phase]["device_to_host_seconds"] += time.perf_counter() - start
        require(time.perf_counter() < self.deadline, "Forward exceeded approved time limit; receipt cannot pass")
        require(all(math.isfinite(v) and v <= 1e-6 for v in result), "Nonfinite/invalid model score")
        self.successful_calls[phase] += 1
        self.examples[phase] += len(examples)
        return result
