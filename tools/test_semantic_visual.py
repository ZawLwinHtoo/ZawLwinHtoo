import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import semantic_visual as visual
import update_profile as sync

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ai_banner', ROOT / 'api/ai-banner.py')
endpoint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(endpoint)
DRAWING = '<g fill="#c9ff59"><circle cx="0" cy="0" r="80"/><path d="M0-80Q10-110 30-100" fill="none" stroke="#f4f4e8" stroke-width="5"/></g>'


class SemanticVisualTests(unittest.TestCase):
    def setUp(self):
        visual._cache.clear()

    def test_unknown_nouns_phrases_and_languages_use_the_full_bio(self):
        for bio in ['apple', 'a dancing elephant', 'quietly optimistic', 'stargazing with cats', '新しいことを学ぶ', 'ရှာဖွေလေ့လာခြင်း', 'xqzflorp']:
            profile = {'login': sync.OWNER, 'name': 'Zaw', 'bio': bio}
            with patch.object(endpoint, 'fetch_profile', return_value=profile):
                with patch.object(endpoint, 'generate_visual', return_value=('Original illustration', DRAWING)) as generate:
                    root = ET.fromstring(endpoint.response_for('/api/ai-banner', 'test-token'))
            generate.assert_called_once_with(bio, 'test-token')
            self.assertEqual(root.find('.//s:g[@id="bio-illustration"]', sync.NS).get('data-theme'), 'semantic')
            self.assertEqual(' '.join(n.text for n in root.iter() if n.get('data-bio-line')), bio)

    def test_svg_filter_rejects_active_and_remote_content(self):
        unsafe = [
            '<g><script>doSomething()</script></g>',
            '<g><image href="https://example.com/picture.svg"/></g>',
            '<g><circle r="10" onclick="run()"/></g>',
            '<g><circle r="10" fill="url(https://example.com/x)"/></g>',
            '<g><foreignObject/></g>',
            '<!DOCTYPE g [<!ENTITY x SYSTEM "file:///etc/passwd">]><g>&x;</g>',
            '<g><circle r="nan"/></g>',
            '<g><text>not a drawing</text></g>',
        ]
        for svg in unsafe:
            with self.assertRaises(visual.VisualUnavailable):
                visual.sanitize(svg)
        ET.fromstring(visual.sanitize(DRAWING))

    def test_cached_illustration_is_keyed_by_the_entire_bio(self):
        with patch.object(visual, '_generate', return_value=('Illustration', DRAWING)) as generate:
            visual.generate_visual('apple', 'token')
            visual.generate_visual('apple', 'token')
            visual.generate_visual('apple orchard', 'token')
            self.assertEqual(generate.call_count, 2)

    def test_failed_generation_is_not_cached(self):
        with patch.object(visual, '_generate', side_effect=[visual.VisualUnavailable('customer_verification_required'), ('Apple', DRAWING)]) as generate:
            with self.assertRaises(visual.VisualUnavailable):
                visual.generate_visual('apple', 'token')
            self.assertEqual(visual.generate_visual('apple', 'token')[0], 'Apple')
            self.assertEqual(generate.call_count, 2)

    def test_generated_subject_and_bio_are_xml_escaped(self):
        profile = {'login': sync.OWNER, 'name': 'Zaw', 'bio': 'apples & <oranges>'}
        root = ET.fromstring(sync.render_banner(profile, visual=('Fruit <&> "colors"', DRAWING)))
        self.assertEqual(root.find('.//s:g[@id="bio-illustration"]', sync.NS).get('data-subject'), 'Fruit <&> "colors"')


if __name__ == '__main__':
    unittest.main()
