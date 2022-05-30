import requests
import os

BASE_URL = os.getenv('BASE_URL', 'http://api:5001/api')


def get_unfinished_archives():
    print('Trying to get to ' + BASE_URL + '/archive/list')
    response = requests.get(BASE_URL + '/archive/list')
    data = response.json()

    return data


def update_status(id, status):
    requests.put(BASE_URL + '/archive/status/' + id + '/' + status)
