from __future__ import annotations
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from scripts import install_skill as installer
from scripts.figure_media import validate, load_manifest, extract
from scripts.audit_figure_pptx import audit


class ModeInstallationTests(unittest.TestCase):
    def test_installed_modes_are_self_contained_in_link_and_copy(self):
        for mode in ('link', 'copy'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                results = installer.install_targets('path', mode, False, root/'academic-figure-master')
                self.assertEqual(len(results[0]['modes']), 2)
                for name in installer.MODES:
                    target = root/name
                    self.assertIn(f'name: {name}', (target/'SKILL.md').read_text())
                    self.assertTrue((target/'references'/f'{name}.md').is_file())
                    self.assertTrue((target/'references'/'handcrafted-figures.md').is_file())
                    self.assertTrue((target/'scripts'/'figure_media.py').is_file())
                    self.assertTrue((target/'scripts'/'handcrafted.mjs').is_file())
                    self.assertTrue((target/'assets'/'styles'/'handcrafted-paper.json').is_file())
                    self.assertIn(f'${name}', (target/'agents'/'openai.yaml').read_text())
                    if mode == 'copy':
                        self.assertFalse((target/'references').is_symlink())
                        self.assertFalse((target/'SKILL.md').is_symlink())
                if mode == 'link':
                    rerun = installer.install_targets('path', mode, False, root/'academic-figure-master')
                    self.assertTrue(all(r['status']=='already-installed' for r in rerun[0]['modes']))

    def test_alias_conflict_does_not_partially_install(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'teaser').mkdir()
            marker = root/'teaser'/'keep.txt'
            marker.write_text('unrelated existing skill')
            with self.assertRaises(FileExistsError):
                installer.install_targets('path', 'copy', False, root/'academic-figure-master')
            self.assertFalse((root/'academic-figure-master').exists())
            self.assertEqual(marker.read_text(), 'unrelated existing skill')

    def test_force_replaces_symlink_without_deleting_target(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            original = root/'old-repository'
            original.mkdir()
            (original/'keep.txt').write_text('keep')
            link = root/'academic-figure-master'
            link.symlink_to(original, target_is_directory=True)
            installer.install(link, 'copy', True)
            self.assertEqual((original/'keep.txt').read_text(), 'keep')
            self.assertFalse(link.is_symlink())
            self.assertTrue((link/'SKILL.md').is_file())

    def test_main_only_does_not_reserve_short_names(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            installer.install_targets('path', 'copy', False, root/'main', with_modes=False)
            self.assertFalse((root/'teaser').exists())
            self.assertFalse((root/'pipeline').exists())

    def test_refuse_overlapping_repository_directory(self):
        with self.assertRaises(ValueError):
            installer.install(installer.ROOT, 'copy', True)


class MediaContractTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        (self.base/'clip.mp4').write_bytes(b'validation-only fixture')
        record = dict(id='output', kind='video', path='clip.mp4', source='unknown', world='w',
                      case='c', attempt='a', status='unknown', role='output', pair_id='pair', timestamps=[0,1,2])
        self.data = dict(evidence_scope='illustrative', media=[record])

    def tearDown(self):
        self.temporary.cleanup()

    def test_reject_mismatched_attempt_in_paired_examples(self):
        other = copy.deepcopy(self.data['media'][0])
        other.update(id='proxy', role='proxy', attempt='different-attempt')
        self.data['media'].append(other)
        with self.assertRaisesRegex(ValueError, 'mismatched'):
            validate(self.data, self.base)

    def test_reject_unsafe_ids_and_invalid_timestamps(self):
        for mutation in ({'id':'../escape'}, {'timestamps':[2,1]}, {'timestamps':[0,float('nan')]},
                         {'timestamps':[True]}, {'timestamps':[-1]}, {'timestamps':[0,0]}):
            data = copy.deepcopy(self.data)
            data['media'][0].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate(data, self.base)

    def test_known_matching_identity_allows_unknown_review_status(self):
        other = copy.deepcopy(self.data['media'][0])
        other.update(id='proxy', role='proxy')
        self.data['media'].append(other)
        path = self.base/'manifest.json'
        path.write_text(json.dumps(self.data))
        self.assertEqual(len(load_manifest(path)['media']), 2)

    def test_unknown_identity_cannot_be_asserted_as_pair(self):
        self.data['media'][0]['attempt']='unknown'
        with self.assertRaisesRegex(ValueError, 'require known'):
            validate(self.data, self.base)


    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg integration requires ffmpeg and ffprobe')
    def test_extract_preserves_provenance_and_rejects_out_of_range_times(self):
        video = self.base/'clip.mp4'
        subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',
                        'testsrc2=size=64x64:rate=5','-t','2','-c:v','mpeg4',str(video)],
                       check=True, capture_output=True)
        record = self.data['media'][0]
        record['timestamps'] = [0.2, 1.2]
        manifest = self.base/'manifest.json'
        manifest.write_text(json.dumps(self.data))
        out = self.base/'frames'
        result = extract(manifest, out)
        self.assertEqual(len(result['frames']), 2)
        self.assertNotEqual(result['frames'][0]['sha256'], result['frames'][1]['sha256'])
        self.assertEqual(result['frames'][0]['source_sha256'], result['frames'][1]['source_sha256'])
        self.assertTrue((out/'source_frames.json').is_file())
        self.assertEqual(result['evidence_scope'], 'illustrative')
        record['timestamps'] = [3]
        manifest.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, 'outside video duration'):
            extract(manifest, self.base/'invalid')
        self.assertFalse((self.base/'invalid').exists())


class PptxAuditTests(unittest.TestCase):
    def test_flattened_slide_is_not_declared_editable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'figure.pptx'
            xml='<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree><p:pic/></p:spTree></p:cSld></p:sld>'
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('ppt/slides/slide1.xml', xml)
            report=audit(p, 'Comic Sans MS')
            self.assertEqual(report['slides'][0]['pictures'],1)
            self.assertTrue(report['issues'])

    def test_reports_declared_font_and_native_objects(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'figure.pptx'
            xml='''<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:rPr><a:latin typeface="Comic Sans MS"/></a:rPr><a:t>Input</a:t></a:r></a:p></p:txBody></p:sp><p:cxnSp/></p:spTree></p:cSld></p:sld>'''
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('ppt/slides/slide1.xml',xml)
            report=audit(p, 'Comic Sans MS')
            self.assertEqual(report['issues'],[])
            self.assertEqual(report['slides'][0]['native_shapes'],1)
            self.assertEqual(report['slides'][0]['connectors'],1)

if __name__ == '__main__':
    unittest.main()
