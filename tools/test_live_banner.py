import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from update_profile import NS

spec = importlib.util.spec_from_file_location('live_banner', Path(__file__).resolve().parents[1] / 'api/banner.py')
live = importlib.util.module_from_spec(spec)
spec.loader.exec_module(live)


class LiveBannerTests(unittest.TestCase):
    def test_consecutive_requests_read_current_bio_without_writing_files(self):
        profiles = [{'login': live.OWNER, 'name': 'Zaw', 'bio': bio} for bio in ['hi', 'Enjoy learning']]
        with patch.object(live, 'fetch_profile', side_effect=profiles) as fetch:
            with patch.object(Path, 'write_text', side_effect=AssertionError('Renderer must not write to disk')):
                first = ET.fromstring(live.response_for('/api/banner'))
                second = ET.fromstring(live.response_for('/api/banner'))
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(first.find('.//s:g[@id="bio-illustration"]', NS).get('data-theme'), 'hello')
        self.assertEqual(second.find('.//s:g[@id="bio-illustration"]', NS).get('data-theme'), 'study')
        self.assertEqual([n.text for n in second.iter() if n.get('data-bio-line')], ['Enjoy', 'learning'])

    def test_learning_and_greeting_work_at_both_sizes(self):
        for example, theme, expected in [('hello', 'hello', 'hi'), ('learning', 'study', 'Enjoy learning')]:
            for mobile in [0, 1]:
                root = ET.fromstring(live.response_for(f'/api/banner?example={example}&mobile={mobile}'))
                self.assertEqual(root.find('.//s:g[@id="bio-illustration"]', NS).get('data-theme'), theme)
                self.assertEqual(' '.join(n.text for n in root.iter() if n.get('data-bio-line')), expected)
                self.assertEqual(root.get('width'), '600' if mobile else '1200')

    def test_public_html_preserves_bio_symbols_and_case(self):
        parser = live.PublicProfileParser()
        parser.feed('<span class="p-name" itemprop="name">Zaw &amp; Htoo</span>'
                    '<div data-bio-text="Enjoy learning &amp; building &lt;things&gt;"></div>')
        self.assertEqual(parser.name, 'Zaw & Htoo')
        self.assertEqual(parser.bio, 'Enjoy learning & building <things>')

    def test_cleared_bio_removes_previous_text_and_uses_name(self):
        profile = {'login': live.OWNER, 'name': 'Zaw', 'bio': ''}
        with patch.object(live, 'fetch_profile', return_value=profile):
            root = ET.fromstring(live.response_for('/api/banner'))
        self.assertEqual(' '.join(n.text for n in root.iter() if n.get('data-bio-line')), 'Zaw')


if __name__ == '__main__':
    unittest.main()
