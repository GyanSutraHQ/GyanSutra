import tempfile
import unittest
from pathlib import Path

from generate_mac import key, validate, write_gallery


class PipelineTests(unittest.TestCase):
    def test_requires_documented_commercial_text_rights(self):
        item = dict(locale='sa-IN', kind='verse', text='कर्मण्येवाधिकारस्ते,')
        with self.assertRaises(ValueError):
            validate([item])
        with self.assertRaises(ValueError):
            validate([{**item, 'rights': 'CC-BY-NC', 'rightsNote': 'Found online'}])
        good = {**item, 'rights': 'public-domain', 'rightsNote': 'Ancient Sanskrit verse'}
        self.assertEqual(validate([good]), [good])

    def test_key_matches_browser_serialization(self):
        self.assertEqual(key(dict(locale='sa-IN', kind='verse', text='कर्मण्येवाधिकारस्ते,')),
            '["sa-IN","verse","कर्मण्येवाधिकारस्ते,"]')

    def test_gallery_escapes_text_and_keeps_audio_local(self):
        with tempfile.TemporaryDirectory() as directory:
            write_gallery(Path(directory), {'key': dict(locale='en-IN', label='<script>',
                text='A & B', voice='English (Male)', file='a.wav')})
            page = (Path(directory) / 'listen.html').read_text()
            self.assertNotIn('<script>', page)
            self.assertIn('A &amp; B', page)
            self.assertIn('src="a.wav"', page)


if __name__ == '__main__':
    unittest.main()
