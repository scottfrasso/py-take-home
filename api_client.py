import requests

BASE_URL = 'http://127.0.0.1:5000/api'


def get_unfinished_archives():
    response = requests.get(BASE_URL + '/archive/list/')
    data = response.json()

    return data


def update_status(id, status):
    requests.put(BASE_URL + '/archive/status/' + id + '/' + status)
