import os
import time
import shutil
import requests

from api_client import get_unfinished_archives, update_status

TMP_FOLDER = '/Users/scottfrasso/PycharmProjects/py-take-home/tmp/'


def poll():
    print('Started Polling')
    unfinished_archives = get_unfinished_archives()

    for archive in unfinished_archives:
        # create a directory to put the files in
        dir_name = os.path.join(TMP_FOLDER, archive['id'])
        os.mkdir(dir_name, 0o666)

        # download files
        for url in archive['urls']:
            file_name = os.path.basename(url)
            response = requests.get(url)
            open(file_name, 'wb').write(response.content)

        # create the zip file
        output_filename = TMP_FOLDER + archive['id'] + '.zip'
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
