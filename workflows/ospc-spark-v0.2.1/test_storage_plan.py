"""Offline transport fixtures and HOLD checks; never a remote storage benchmark."""
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import yaml
from stage_shared import check_archive,extract_new,members_checked

HERE=Path(__file__).resolve().parent


def fixture(entries):
    data=io.BytesIO()
    with tarfile.open(fileobj=data,mode='w') as archive:
        for name,body,kind in entries:
            info=tarfile.TarInfo(name);info.size=len(body)
            if kind=='symlink':info.type=tarfile.SYMTYPE;info.linkname='../outside';info.size=0
            archive.addfile(info,io.BytesIO(body) if info.isfile() else None)
    data.seek(0);return data


class StoragePlanTests(unittest.TestCase):
    def test_hold_has_only_existing_volume_and_no_ingress_or_gpu(self):
        workflow=yaml.safe_load((HERE/'storage-stage-team15.HOLD.fz').read_text())
        self.assertEqual(workflow['version'],'v4')
        self.assertEqual(workflow['volumes'],{'project':{'use':'team15','name':'lymescope-project'}})
        job=workflow['jobs']['stage-and-verify']
        self.assertNotIn('devices',job['resource'])
        self.assertLess(job['script'].index('exit 78'),job['script'].index('python3 -B'))
        self.assertEqual(job['mounts'],{'/project':'project'})
        self.assertEqual(workflow['files']['stage_shared.py'],(HERE/'stage_shared.py').read_text())
        self.assertEqual(json.loads(workflow['files']['storage-plan.json']),json.loads((HERE/'storage-plan.HOLD.json').read_text()))

    def test_quota_budget_and_existing_scientific_task_plan(self):
        plan=json.loads((HERE/'storage-plan.HOLD.json').read_text())
        self.assertEqual(plan['model']['expanded_bytes'],31387085)
        self.assertEqual(len(plan['model']['file_names']),6)
        self.assertEqual(plan['peak_payload_plus_output_budget_bytes'],109324699)
        self.assertLess(plan['peak_payload_plus_output_budget_bytes'],plan['incremental_reservation_bytes'])
        self.assertEqual(plan['incremental_reservation_bytes'],128*1024**2)
        self.assertIsNone(plan['current_free_quota_bytes'])
        trial=json.loads((HERE/'trial.HOLD.json').read_text())
        self.assertEqual([x['scientific_masks'] for x in trial['tasks'] if x['trial']=='two'],[3156,3149])
        self.assertEqual(trial['batch_size'],8)

    def test_safe_model_fixture_extracts_and_preserves_bytes(self):
        data=fixture([('model.safetensors',b'fixture','file')])
        plan={'package_path':'science','model':{'expanded_bytes':7,'file_names':['model.safetensors']}}
        with tempfile.TemporaryDirectory(prefix='lymescope-storage-fixture-') as tmp:
            archive=Path(tmp)/'input.tar';archive.write_bytes(data.getvalue());dest=Path(tmp)/'new'
            extract_new(archive,dest,'model',plan)
            self.assertEqual((dest/'model.safetensors').read_bytes(),b'fixture')

    def test_traversal_is_rejected_before_extraction(self):
        with tarfile.open(fileobj=fixture([('../outside',b'x','file')])) as archive:
            with self.assertRaisesRegex(ValueError,'Unsafe'):members_checked(archive,'science','science',1,[])

    def test_links_are_rejected(self):
        with tarfile.open(fileobj=fixture([('science/link',b'','symlink')])) as archive:
            with self.assertRaisesRegex(ValueError,'links'):members_checked(archive,'science','science',0,[])

    def test_duplicate_members_are_rejected(self):
        with tarfile.open(fileobj=fixture([('science/a',b'x','file'),('science/a',b'x','file')])) as archive:
            with self.assertRaisesRegex(ValueError,'Duplicate'):members_checked(archive,'science','science',2,[])

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix='lymescope-storage-fixture-') as tmp:
            dest=Path(tmp)/'existing';dest.mkdir();sentinel=dest/'sentinel';sentinel.write_bytes(b'keep')
            with self.assertRaises(FileExistsError):extract_new(Path(tmp)/'unused.tar',dest,'model',{})
            self.assertEqual(sentinel.read_bytes(),b'keep')

    def test_archive_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory(prefix='lymescope-storage-fixture-') as tmp:
            path=Path(tmp)/'input.tar';path.write_bytes(b'corrupt')
            expected={'archive_bytes':7,'archive_sha256':hashlib.sha256(b'correct').hexdigest()}
            with self.assertRaisesRegex(ValueError,'SHA256'):check_archive(path,expected)


if __name__=='__main__':unittest.main(verbosity=2)
