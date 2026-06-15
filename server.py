"""
MedElite proxy server.
Serves index.html and proxies CMS API calls (which block browser CORS).
Run locally:  python3 server.py
Production:   gunicorn server:app
"""
import urllib.request, urllib.error, urllib.parse, json, ssl, os
from flask import Flask, jsonify, send_file, send_from_directory

# Skip SSL verification for CMS public API endpoints.
# Required locally on macOS (missing CA bundle) and kept for Render (Linux)
# to avoid any CMS certificate chain issues.
_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

CMS = 'https://data.cms.gov/provider-data/api/1/datastore/query'

def cms_get(dataset, ccn):
    url = (f'{CMS}/{dataset}/0'
           f'?conditions%5B0%5D%5Bproperty%5D=cms_certification_number_ccn'
           f'&conditions%5B0%5D%5Bvalue%5D={urllib.parse.quote(ccn)}'
           f'&conditions%5B0%5D%5Boperator%5D=%3D&limit=25')
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
        return json.loads(r.read())

def cms_avg(state_or_nation):
    url = (f'{CMS}/xcdc-v8bm/0'
           f'?conditions%5B0%5D%5Bproperty%5D=state_or_nation'
           f'&conditions%5B0%5D%5Bvalue%5D={urllib.parse.quote(state_or_nation)}'
           f'&conditions%5B0%5D%5Boperator%5D=%3D&limit=1')
    req = urllib.request.Request(url, headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=15, context=_ctx) as r:
        return json.loads(r.read())

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/template.docx')
def template():
    return send_from_directory(BASE_DIR, 'template.docx',
                               mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@app.route('/debug')
def debug():
    files = os.listdir(BASE_DIR)
    return jsonify({'base_dir': BASE_DIR, 'files': files})

@app.route('/api/provider/<ccn>')
def provider(ccn):
    try:
        return jsonify(cms_get('4pq5-n9py', ccn))
    except urllib.error.HTTPError as e:
        return jsonify({'error': f'CMS HTTP {e.code}'}), e.code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/claims/<ccn>')
def claims(ccn):
    try:
        return jsonify(cms_get('ijh5-nb2v', ccn))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/averages/<state>')
def averages(state):
    try:
        return jsonify({'national': cms_avg('NATION'), 'state': cms_avg(state.upper())})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3456))
    print(f'\n  MedElite running at http://localhost:{port}\n')
    app.run(host='0.0.0.0', port=port, debug=False)
