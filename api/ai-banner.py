"""Open-ended bio illustrator. Activation requires verified AI Gateway access."""
from http.server import BaseHTTPRequestHandler
import json
import os
from pathlib import Path
import sys
import urllib.parse

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from banner import fetch_profile
from semantic_visual import generate_visual, VisualUnavailable
from update_profile import clean, render_banner


def response_for(path, token):
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)
    profile = fetch_profile()
    bio = clean(profile.get('bio')) or clean(profile.get('name')) or profile['login']
    visual = generate_visual(bio, token)
    return render_banner(profile, query.get('mobile', ['0'])[0] == '1', visual=visual).encode('utf-8')


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = self.headers.get('x-vercel-oidc-token') or os.environ.get('VERCEL_OIDC_TOKEN')
        try:
            body = response_for(self.path, token)
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml; charset=utf-8')
        except VisualUnavailable as error:
            print(json.dumps({'event': 'bio_art_unavailable', 'reason': error.reason, 'status': error.status}))
            body = json.dumps({'error': 'AI illustration unavailable', 'reason': error.reason}).encode('utf-8')
            self.send_response(503)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
        except Exception as error:
            print(json.dumps({'event': 'bio_art_error', 'type': type(error).__name__}))
            body = b'Profile illustration temporarily unavailable. Please reload.'
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        self.send_header('CDN-Cache-Control', 'no-store')
        self.send_header('Vercel-CDN-Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)
