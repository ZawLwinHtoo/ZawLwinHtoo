"""Live GitHub bio image; no writes, tokens, jobs, or user-entered settings."""
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from update_profile import OWNER, render_banner


class PublicProfileParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bio = None
        self.name = ''
        self.reading_name = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-bio-text' in attrs:
            self.bio = attrs['data-bio-text']
        if attrs.get('itemprop') == 'name' and 'p-name' in attrs.get('class', ''):
            self.reading_name = True

    def handle_endtag(self, tag):
        if tag == 'span':
            self.reading_name = False

    def handle_data(self, data):
        if self.reading_name:
            self.name += data


def fetch_profile():
    # Public HTML avoids the small shared anonymous REST API rate limit.
    # Missing markup fails explicitly instead of showing a previous bio as current.
    request = urllib.request.Request(f'https://github.com/{OWNER}', headers={
        'User-Agent': 'ZawLwinHtoo-live-profile-image', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=12) as response:
        document = response.read().decode('utf-8')
    parser = PublicProfileParser()
    parser.feed(document)
    if not parser.name.strip():
        raise ValueError('Public profile name not found')
    # GitHub omits the entire bio element after the user clears their bio.
    return {'login': OWNER, 'name': parser.name.strip(), 'bio': parser.bio or ''}


EXAMPLES = {'hello': 'hi', 'learning': 'Enjoy learning'}


def response_for(path):
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
    mobile = query.get('mobile', ['0'])[0] == '1'
    example = query.get('example', [''])[0]
    if example in EXAMPLES:
        profile = {'login': OWNER, 'name': 'Zaw Lwin Htoo', 'bio': EXAMPLES[example]}
    else:
        profile = fetch_profile()
    return render_banner(profile, mobile).encode('utf-8')


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            body = response_for(self.path)
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
        except Exception as error:
            print(json.dumps({'event': 'profile_image_error', 'type': type(error).__name__}))
            body = b'Profile image temporarily unavailable. Please reload.'
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        self.send_header('CDN-Cache-Control', 'no-store')
        self.send_header('Vercel-CDN-Cache-Control', 'no-store')
        self.send_header('Expires', '0')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        self.end_headers()
