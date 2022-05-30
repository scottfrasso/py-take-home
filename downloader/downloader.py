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

print(ARCHIVES_FOLDER + ' folder exists!')


def poll():
    print('Started Polling')
    unfinished_archives = get_unfinished_archives()

    for archive in unfinished_archives:
        # create a directory to put the files in
        dir_name = os.path.join(ARCHIVES_FOLDER, archive['id'])
        os.mkdir(dir_name, 0o666)

        # download files
        for url in archive['urls']:
            file_name = os.path.basename(url)
            response = requests.get(url)
            open(file_name, 'wb').write(response.content)

        # create the zip file
        output_filename = ARCHIVES_FOLDER + archive['id'] + '.zip'
        shutil.make_archive(output_filename, 'zip', dir_name)
        os.rmdir(dir_name)

        # set the status as done for this archive
        update_status(archive['id'], 'DONE')

    print('Finished Polling')


if __name__ == '__main__':
    while True:
        poll()
        print('Sleeping until the next time to poll')
        time.sleep(2)
