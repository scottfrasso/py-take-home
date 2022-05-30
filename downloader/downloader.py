import os
import time
import shutil
import requests
import sys
from os import path

from api_client import get_unfinished_archives, update_status

ARCHIVES_FOLDER = os.getenv('ARCHIVES_FOLDER', '/archives')
if not path.exists(ARCHIVES_FOLDER):
    print('ARCHIVES_FOLDER Folder ' + ARCHIVES_FOLDER + ' does not exist')
    sys.exit(-1)


def download_archive(archive):
    # create a directory to put the files in
    dir_name = os.path.join(ARCHIVES_FOLDER, archive['id'])
    print('Creating directory ' + str(dir_name))
    os.mkdir(dir_name, 0o777)

    # download files
    for url in archive['urls']:
        print('Downloading url ' + url)
        file_name = os.path.basename(url)
        response = requests.get(url)
        url_filename = os.path.join(dir_name, file_name)
        print('Writing url ' + url + ' to file ' + url_filename)
        open(url_filename, 'wb').write(response.content)

    # create the zip file
    print('Creating a zip for for archive ID ' + archive['id'])
    output_filename = os.path.join(ARCHIVES_FOLDER, archive['id'])
    shutil.make_archive(output_filename, 'zip', dir_name)

    # set the status as done for this archive
    update_status(archive['id'], 'DONE')


def poll():
    print('Started Polling')
    unfinished_archives = get_unfinished_archives()
    print('Polled and got ' + str(len(unfinished_archives)) + ' Archives to download')

    for archive in unfinished_archives:
        try:
            download_archive(archive)
        except Exception as e:
            print('An error occurred while downloading archive ' + archive['id'])
            print(e)
            update_status(archive['id'], 'ERRORED')

    print('Finished Polling')


if __name__ == '__main__':
    while True:
        poll()
        print('Sleeping until the next time to poll')
        time.sleep(2)
