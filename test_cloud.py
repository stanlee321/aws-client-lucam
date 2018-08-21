from typing import Any, Union

from ownLibraries.cloudpipeline import CloudSync

if __name__ == '__main__':
    import os

    # from tqdm import tqdm

    sync = CloudSync()
    counter = 0
    local_counter = -1

    path = os.getenv('HOME') + '/' + '16-13-05/'
    sync(path_to_folder=path)

    #sync.stop()
    """
    while True:
        counter += 1

        time.sleep(1)
        print(counter)

        if counter % 2:
            local_counter += 1

            try:
                folder = os.getenv('HOME') + '/' + '2018-02-16_reporte' + '/' + folders[local_counter] + '/'
                print('folder', folder)
                print('local counter', local_counter)
                sync(path_to_folder=folder)
            except Exception as e:
                print(e)
                print('job done')

        else:
            pass
    """