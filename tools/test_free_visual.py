from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import free_visual as free

DRAWING = '<g fill="#c9ff59"><circle cx="128" cy="128" r="70"/><path d="M128 58Q140 25 160 37" stroke="#f4f4e8" fill="none" stroke-width="5"/></g>'


class FreeVisualTests(unittest.TestCase):
    def test_canvas_is_centered_and_only_safe_geometry_survives(self):
        result = free.normalize_drawing(DRAWING)
        root = ET.fromstring(result)
        self.assertEqual(root.get('transform'), 'translate(-128 -128)')
        with self.assertRaises(free.VisualUnavailable):
            free.normalize_drawing('<g><image href="https://example.com"/></g>')

    def test_full_svg_and_simple_black_white_aliases_are_normalized(self):
        root = ET.fromstring(free.normalize_drawing('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><circle cx="128" cy="128" r="40" fill="white"/></svg>'))
        self.assertEqual(root.find('.//circle').get('fill'), '#f4f4e8')

    def test_art_is_reused_only_for_the_same_bio(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(free, 'CACHE_FILE', Path(directory) / 'bio-art.json'):
                self.assertIsNone(free.cached_visual('apple'))
                visual = ('Apple', free.normalize_drawing(DRAWING))
                free.save_visual('apple', visual)
                self.assertEqual(free.cached_visual('apple'), visual)
                self.assertIsNone(free.cached_visual('Enjoy learning'))


if __name__ == '__main__':
    unittest.main()
