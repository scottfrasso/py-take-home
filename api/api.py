import uuid
import json
import os
import sys
from pathlib import Path
from flask import Flask, request, abort
from flask import send_from_directory
from os import path

ARCHIVES_FOLDER = os.getenv('ARCHIVES_FOLDER', '/archives')
if not path.exists(ARCHIVES_FOLDER):
    print('ARCHIVES_FOLDER Folder ' + ARCHIVES_FOLDER + ' does not exist')
    sys.exit(-1)

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

    filename = id + '.zip'
    filepath = Path(os.path.join(ARCHIVES_FOLDER, filename))
    if not filepath.is_file():
        print('File does not exist at ' + str(filepath))
        abort(404)

    return send_from_directory(ARCHIVES_FOLDER, filename, as_attachment=True)


@app.route('/api/archive/status/<id>/<status>', methods=['PUT'])
def update(id, status):
    data = store.get(id)
    if not data:
        abort(404)

    if status not in STATUSES:
        abort(400)

    data['status'] = status

    return json.dumps(data)


if __name__ == '__main__':
    PORT = int(os.getenv('PORT', '5001'))
    HOST = os.getenv('HOST', 'api')

    app.run(debug=True, host=HOST, port=PORT)
