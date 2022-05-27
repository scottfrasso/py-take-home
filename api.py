import uuid
import json
import os
from pathlib import Path
from flask import Flask, request, abort
from flask import send_from_directory

app = Flask(__name__)

store = {}

NOT_STARTED = 'NOT_STARTED'
STARTED = 'STARTED'
ERRORED = 'ERRORED'
DONE = 'DONE'
STATUSES = (NOT_STARTED, STARTED, ERRORED, DONE)


@app.route('/api/health')
def home():
    return "Alive!"


@app.route('/api/archive/list', methods=['GET'])
def get_unstarted():
    unstarted_archives = [archive for archive in store.values() if archive['status'] == NOT_STARTED]

    return json.dumps(unstarted_archives)


@app.route('/api/archive/create', methods=['POST'])
def create():
    data = request.get_json(force=True)
    id = str(uuid.uuid4())
    data['id'] = id
    data['status'] = 'NOT_STARTED'
    store[id] = data

    return json.dumps({'archive_hash': id})


@app.route('/api/archive/status/<id>', methods=['GET'])
def get_status(id):
    data = store.get(id)
    if not data:
        abort(404)

    status = data['status']

    return json.dumps({'status': status})


@app.route('/api/archive/get/<id>', methods=['GET'])
def index(id):
    data = store.get(id)
    if not data:
        abort(404)

    if data['status'] != DONE:
        abort(400)

    root_dir = os.path.dirname(os.getcwd())
    tmp_dir = os.path.join(root_dir, 'py-take-home', 'tmp')

    filename = id + '.zip'
    filepath = Path(os.path.join(tmp_dir, filename))
    if not filepath.is_file():
        abort(404)

    return send_from_directory(tmp_dir, filename, as_attachment=True)


@app.route('/api/archive/status/<id>/<status>', methods=['PUT'])
def update(id, status):
    data = store.get(id)
    if not data:
        abort(404)

    if status not in STATUSES:
        abort(400)

    data['status'] = status


if __name__ == '__main__':
    app.run(debug=True)
