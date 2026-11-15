"""Separate presentation annotation of saved evidence; no model or new alignment."""
import hashlib
import json
import math
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CODE = REPO / "sparkprep/analysis/ospc_masked_v0.2.0"
sys.path.insert(0, str(CODE))
from core import FROZEN, digest, load_panel, position_map, require

_cif = types.ModuleType("frozen_cif")
_path = FROZEN / "source/cif_reader.py"
exec(compile(_path.read_bytes(), str(_path), "exec"), vars(_cif))
_baseline = types.ModuleType("frozen_reference_baseline")
_path = FROZEN / "source/baseline.py"
exec(compile(_path.read_bytes(), str(_path), "exec"), vars(_baseline))
rows = _baseline.cif_rows


def observed_ca(c, chain):
    result = {}
    for r in rows(c, "_atom_site"):
        if (r["label_asym_id"] == chain and r["label_atom_id"] == "CA" and r["group_PDB"] == "ATOM"
                and r["pdbx_PDB_model_num"] == "1" and float(r["occupancy"]) > 0):
            key = int(r["label_seq_id"])
            require(key not in result, "Multiple CA conformers require explicit review")
            result[key] = r
    return result


def assembly_one(c):
    assemblies = rows(c, "_pdbx_struct_assembly")
    assembly = next(r for r in assemblies if r["id"] == "1")
    generators = [r for r in rows(c, "_pdbx_struct_assembly_gen") if r["assembly_id"] == "1"]
    require(len(generators) == 1 and generators[0]["oper_expression"] == "1", "Unsupported assembly operation; no contacts calculated")
    operation = next(r for r in rows(c, "_pdbx_struct_oper_list") if r["id"] == "1")
    for i in range(1, 4):
        require(float(operation[f"vector[{i}]"]) == 0, "Nonidentity assembly translation")
        for j in range(1, 4):
            require(float(operation[f"matrix[{i}][{j}]"]) == int(i == j), "Nonidentity assembly rotation")
    entities = {r["id"]: r["type"] for r in rows(c, "_entity")}
    polymer = {r["id"] for r in rows(c, "_struct_asym") if entities[r["entity_id"]] == "polymer"}
    included = generators[0]["asym_id_list"].split(",")
    chains = [a for a in included if a in polymer]
    require(chains == ["A", "B"] and assembly["oligomeric_count"] == "2", "Unexpected 1GGQ assembly composition")
    return {"selected_assembly": assembly, "generator": generators[0], "operator": operation,
            "polymer_chains": chains, "other_included_asym_ids": [a for a in included if a not in polymer],
            "other_deposited_assemblies": [r for r in assemblies if r["id"] != "1"],
            "selection_note": "Assembly 1 is the deposited author/software dimer containing scored chain A. Assembly 2 is C/D; assembly 3 is software-defined tetramer. Asymmetric-unit chains were not automatically treated as one biological assembly."}


def second_reference(c, sequences, alignment, columns):
    scheme = [r for r in rows(c, "_pdbx_poly_seq_scheme") if r["asym_id"] == "A"]
    construct = "".join(_baseline.THREE.get(r["mon_id"], "X") for r in scheme)
    sequence = sequences["Q44717"]
    matches = [i for i in range(len(sequence)) if sequence.startswith(construct, i)]
    require(matches == [39] and len(construct) == 164, "Second reference construct match is not unique/exact")
    require([int(r["seq_id"]) for r in scheme] == list(range(1, 165)), "Noncontiguous secondary polymer labels")
    atoms = observed_ca(c, "A")
    require(len(atoms) == 164, "Unexpected secondary observed CA count")
    mapping = position_map(alignment["Q44717"])
    out = []
    for index, row in enumerate(scheme):
        label = int(row["seq_id"])
        atom = atoms[label]
        native = 40 + index
        require(_baseline.THREE[row["mon_id"]] == sequence[native-1], "Secondary sequence mismatch")
        require(atom["auth_asym_id"] == row["pdb_strand_id"] == "A" and atom["auth_seq_id"] == row["pdb_seq_num"], "Secondary author numbering mismatch")
        require(row["pdb_seq_num"] == str(native), "Secondary author/native correspondence changed")
        require(atom["label_comp_id"] == row["mon_id"] and _baseline.clean_code(atom["pdbx_PDB_ins_code"]) == _baseline.clean_code(row["pdb_ins_code"]), "Secondary residue/insertion mismatch")
        col = mapping[native]
        out.append({"label_seq_id": label, "auth_residue_number": row["pdb_seq_num"],
                    "insertion_code": _baseline.clean_code(row["pdb_ins_code"]), "aa": sequence[native-1],
                    "panel_sequence_position": native, "alignment_column": col, "has_observed_CA": True,
                    "mapping_status": "observed", "modal_fraction": columns[col-1]["modal_fraction"],
                    "coverage": columns[col-1]["coverage"], "nearest_other_chain_CA_A": None})
    return {"pdb_id": "1G5Z", "panel_accession": "Q44717", "construct_native_start": 40, "construct_native_end": 203,
            "construct_count": 164, "observed_count": 164, "mapping": out,
            "historical_deposited_correspondence": rows(c, "_struct_ref_seq"),
            "correspondence_basis": "Unique exact 164-residue construct match to Q44717 native 40–203; author numbers/insertion codes and atom identities checked independently. Deposited historical O31117 mapping retained; not silently relabeled.",
            "assembly": rows(c, "_pdbx_struct_assembly"), "assembly_generators": rows(c, "_pdbx_struct_assembly_gen"),
            "contact_proxy_status": "NOT CALCULATED for 1G5Z; biological dimer requires symmetry operator 2, not two asymmetric-unit polymer chains."}


def build_context():
    sequences, alignment = load_panel()
    saved = json.loads((FROZEN / "viewer_data.json").read_text())
    c = _cif.parse_cif(FROZEN / "inputs/reference_structures/1GGQ.cif")
    assembly = assembly_one(c)  # Must pass before any interchain distance is calculated.
    other = observed_ca(c, "B")
    primary_atoms = observed_ca(c, "A")
    primary = []
    threshold = 8.0  # A declared C-alpha proximity proxy, never solvent accessibility.
    for original in saved["structure_residues"]:
        row = dict(original)
        distance = None
        if row["xyz"] is not None:
            atom = primary_atoms[row["label_seq_id"]]
            require(row["xyz"] == [float(atom[k]) for k in ("Cartn_x", "Cartn_y", "Cartn_z")], "Saved primary coordinates differ from the actual assembly input")
            distance = min(math.dist(row["xyz"], [float(atom[k]) for k in ("Cartn_x", "Cartn_y", "Cartn_z")]) for atom in other.values())
        row["nearest_other_chain_CA_A"] = distance
        row["CA_contact_proxy_within_8A"] = distance <= threshold if distance is not None else None
        primary.append(row)
    records = json.loads((FROZEN / "inputs/source_data/selected_uniprot_records.json").read_text())["results"]
    annotations = {}
    for accession in ("Q07337", "Q44717"):
        record = next(r for r in records if r["primaryAccession"] == accession)
        features = [f for f in record.get("features", []) if f["type"] in ("Signal", "Chain", "Lipidation")]
        signal = [f for f in features if f["type"] == "Signal"]
        chain = [f for f in features if f["type"] == "Chain"]
        require(len(signal) == len(chain) == 1 and signal[0]["location"]["end"]["value"] + 1 == chain[0]["location"]["start"]["value"], "Cleavage annotations unresolved")
        annotations[accession] = {"features": features, "signal_start": signal[0]["location"]["start"]["value"],
                                "signal_end": signal[0]["location"]["end"]["value"], "chain_start": chain[0]["location"]["start"]["value"],
                                "evidence_note": "Annotation-supported predicted processing boundary, not experimentally measured cleavage in this project. No sequence was trimmed or deleted."}
    second = second_reference(_cif.parse_cif(FROZEN / "inputs/reference_structures/1G5Z.cif"), sequences, alignment, saved["columns"])
    fully = [r["alignment_column"] for r in saved["columns"] if r["coverage"] == 1]
    observed = [r["alignment_column"] for r in saved["mapping"] if r["status"] == "observed"]
    common = sorted(set(fully) & set(observed))
    require((len(fully), len(observed), len(common)) == (202, 162, 159), "Eligibility sets differ")
    return {"version": "0.2.0", "kind": "presentation_annotation_of_saved_evidence",
            "model_scoring": "NOT RUN", "frozen_science_modified": False,
            "summary": saved["summary"], "columns": saved["columns"], "original_primary_mapping": saved["mapping"],
            "column_sets": {"fully_covered": fully, "mapped_observed": observed, "intersection": common},
            "alignment_only": [{"column": c, "contributing_sequences": saved["columns"][c-1]["contributing_sequences"],
                                "coverage": saved["columns"][c-1]["coverage"], "mapping_status": saved["mapping"][c-1]["status"]} for c in (154, 173)],
            "annotations": annotations,
            "references": {"1GGQ": {"pdb_id": "1GGQ", "panel_accession": "Q07337", "construct_native_start": 38,
                                      "construct_native_end": 210, "construct_count": 174, "native_construct_count": 173,
                                      "observed_count": 162, "mapping": primary, "assembly": assembly,
                                      "contact_proxy_status": "Minimum observed chain-A to chain-B C-alpha distance in deposited assembly 1; 8 Å threshold. A contact proxy only, not measured solvent or antibody accessibility."}, "1G5Z": second},
            "provenance": {name: digest(FROZEN / name) for name in (
                "viewer_data.json", "aligned.fasta", "inputs/input_sequences.fasta", "inputs/source_data/selected_uniprot_records.json",
                "inputs/reference_structures/1GGQ.cif", "inputs/reference_structures/1G5Z.cif", "source/cif_reader.py", "source/baseline.py")}}


def write_overlay():
    data = build_context()
    from spark_adapter import load_evidence
    data['spark_science'] = load_evidence(data)
    data['model_scoring'] = 'COMPLETED_PERSONAL_SPARK'
    # Only this versioned demo layer is generated; no frozen file is written.
    (HERE / "context.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    embedded = json.dumps(data, ensure_ascii=False, allow_nan=False).replace("<", "\\u003c")
    template = (HERE / "index.template.html").read_text(encoding="utf-8")
    require(template.count("__CONTEXT_JSON__") == 1, "Expected one data slot")
    (HERE / "index.html").write_text(template.replace("__CONTEXT_JSON__", embedded), encoding="utf-8", newline="\n")
    return data


if __name__ == "__main__":
    data = write_overlay()
    print(json.dumps({"overlay": str(HERE / "index.html"), "counts": [len(data["column_sets"][k]) for k in ("fully_covered", "mapped_observed", "intersection")], "secondary_mapping_rows": len(data["references"]["1G5Z"]["mapping"]), "model_scoring": data["model_scoring"]}))
