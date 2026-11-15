"""Local synthetic importer tests. Fixtures are never scientific inputs or exported results."""
import hashlib,importlib.util,json,sys,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("bundle_import",ROOT/"scripts/import_scientific_bundle.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
class ImportChecks(unittest.TestCase):
    def setUp(self):
        # Retain explicitly labeled synthetic fixtures locally; no user data is deleted.
        self.root=Path(tempfile.mkdtemp(prefix="SYNTHETIC-importer-test-",dir=ROOT/"findings"))
        contents={
            "sequences.fasta":b">synthetic_test\nACDEFGHIK\n",
            "metadata.json":json.dumps([{"sequence_id":"synthetic_test","accession":"SYNTHETIC_TEST","source_id":"synthetic"}]).encode(),
            "sources.json":json.dumps({"sources":[{"id":"synthetic","url":"https://example.org/synthetic-test-only","license":"Synthetic unit test fixture; not a real protein dataset","citation":"Synthetic parser test only","retrieved_at":"2026-11-14"}]}).encode()
        }
        roles=["fasta","sequence_metadata","source_manifest"]
        self.manifest={"schema_version":1,"bundle_id":"SYNTHETIC_TEST_ONLY","files":[]}
        for (name,data),role in zip(contents.items(),roles):
            (self.root/name).write_bytes(data)
            self.manifest["files"].append({"path":name,"role":role,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
        self.save_manifest()
    def save_manifest(self):
        (self.root/"bundle_manifest.json").write_text(json.dumps(self.manifest))
    def replace(self,name,data):
        (self.root/name).write_bytes(data)
        row=next(r for r in self.manifest["files"] if r["path"]==name)
        row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest()); self.save_manifest()
    def test_valid_and_missing_reference_explicit(self):
        _,r=mod.validate(self.root)
        self.assertEqual(r["status"],"VALIDATED_LOCAL_ONLY")
        self.assertEqual(r["sequences"]["synthetic_test"]["length"],9)
        self.assertIn("Reference structures missing; no structures fabricated",r["warnings"])
        self.assertFalse(r["scientific_results"])
    def test_hash_corruption(self):
        (self.root/"sequences.fasta").write_bytes(b">synthetic_test\nACDEFGHIL\n")
        with self.assertRaisesRegex(mod.InvalidBundle,"Hash mismatch"): mod.validate(self.root)
    def test_metadata_must_cover_fasta(self):
        self.replace("metadata.json",b"[]")
        with self.assertRaisesRegex(mod.InvalidBundle,"Every sequence"): mod.validate(self.root)
    def test_invalid_residue(self):
        self.replace("sequences.fasta",b">synthetic_test\nACD123\n")
        with self.assertRaisesRegex(mod.InvalidBundle,"Invalid residue"): mod.validate(self.root)
    def test_unlisted_file(self):
        (self.root/"unlisted.txt").write_text("unlisted synthetic fixture")
        with self.assertRaisesRegex(mod.InvalidBundle,"Unlisted"): mod.validate(self.root)
    def test_zip_traversal(self):
        archive=self.root/"malformed.zip"
        with zipfile.ZipFile(archive,"w") as z: z.writestr("../outside.txt","synthetic")
        with self.assertRaises(mod.InvalidBundle): mod.validate(archive)
        self.assertFalse((self.root.parent/"outside.txt").exists())
    def test_windows_paths(self):
        for path in ["C:/outside","folder/../outside","file:stream","CON.txt","a\\b","a//b"]:
            with self.subTest(path=path), self.assertRaises(mod.InvalidBundle): mod.safe_path(path)
    def test_valid_zip(self):
        archive=self.root/"valid.zip"
        with zipfile.ZipFile(archive,"w") as z:
            for name in ["bundle_manifest.json"]+[r["path"] for r in self.manifest["files"]]:
                z.write(self.root/name,name)
        _,r=mod.validate(archive)
        self.assertEqual(r["file_count"],4)
if __name__=="__main__":
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ImportChecks))
    (ROOT/"findings/scientific-importer-tests.json").write_text(json.dumps({"tests":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"synthetic_fixtures_only":True,"scientific_results":False,"remote_actions":0},indent=2)+"\n")
    sys.exit(not result.wasSuccessful())

