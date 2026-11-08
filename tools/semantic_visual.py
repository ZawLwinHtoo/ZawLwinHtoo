"""Validate locally generated vector geometry before embedding it in the profile."""
import re
import xml.etree.ElementTree as ET

_palette = {'#c9ff59', '#f4f4e8', '#131613', '#293925', '#657b55', 'none'}
_tags = {'g', 'path', 'circle', 'ellipse', 'rect', 'line', 'polyline', 'polygon'}
_numeric = {'x', 'y', 'x1', 'x2', 'y1', 'y2', 'cx', 'cy', 'r', 'rx', 'ry', 'width', 'height', 'stroke-width', 'stroke-miterlimit', 'opacity', 'fill-opacity', 'stroke-opacity'}
_drawing = re.compile(r'^[MmZzLlHhVvCcSsQqTtAa0-9eE+,\.\s-]+$')
_transform = re.compile(r'^(?:(?:translate|scale|rotate|matrix|skewX|skewY)\([-+0-9eE.,\s]+\)\s*)+$')

class VisualUnavailable(RuntimeError):
    def __init__(self, reason, status=None):
        super().__init__(reason)
        self.reason, self.status = reason, status


def sanitize(fragment, palette_only=True):
    if not isinstance(fragment, str) or len(fragment) > (30000 if palette_only else 128000) or '<!' in fragment or '<?' in fragment:
        raise VisualUnavailable('invalid_svg')
    try:
        root = ET.fromstring(fragment)
    except ET.ParseError as error:
        raise VisualUnavailable('invalid_svg') from error
    if root.tag not in ('g', '{http://www.w3.org/2000/svg}g'):
        raise VisualUnavailable('invalid_svg_root')
    nodes = list(root.iter())
    if not 2 <= len(nodes) <= (160 if palette_only else 512):
        raise VisualUnavailable('invalid_svg_size')
    for node in nodes:
        tag = node.tag.removeprefix('{http://www.w3.org/2000/svg}')
        if tag not in _tags or (node.text or '').strip() or (node.tail or '').strip():
            raise VisualUnavailable('unsupported_svg_content')
        node.tag = tag
        for key, value in node.attrib.items():
            if key in _numeric:
                try:
                    number = float(value)
                except ValueError as error:
                    raise VisualUnavailable('invalid_svg_number') from error
                if not -2000 <= number <= 2000:
                    raise VisualUnavailable('invalid_svg_number')
                if key.endswith('opacity') and not 0 <= number <= 1:
                    raise VisualUnavailable('invalid_svg_opacity')
            elif key in ('fill', 'stroke'):
                if value.lower() not in _palette and (palette_only or not re.fullmatch(r'#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?', value)):
                    raise VisualUnavailable('unsupported_svg_paint')
            elif key == 'd':
                if len(value) > (8000 if palette_only else 60000) or not _drawing.fullmatch(value):
                    raise VisualUnavailable('invalid_svg_path')
            elif key == 'points':
                if not re.fullmatch(r'[-+0-9eE.,\s]+', value):
                    raise VisualUnavailable('invalid_svg_points')
            elif key == 'transform':
                if not _transform.fullmatch(value):
                    raise VisualUnavailable('invalid_svg_transform')
            elif key == 'stroke-linecap':
                if value not in ('round', 'butt', 'square'):
                    raise VisualUnavailable('invalid_svg_linecap')
            elif key == 'stroke-linejoin':
                if value not in ('round', 'bevel', 'miter'):
                    raise VisualUnavailable('invalid_svg_linejoin')
            elif key in ('fill-rule', 'clip-rule'):
                if value not in ('evenodd', 'nonzero'):
                    raise VisualUnavailable('invalid_svg_fill_rule')
            else:
                raise VisualUnavailable('unsupported_svg_attribute')
    return ET.tostring(root, encoding='unicode')
