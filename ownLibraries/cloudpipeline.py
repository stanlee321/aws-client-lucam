import collections
import multiprocessing

# Own lib imports
from .cloudsync.CloudPipeLine import CloudSyncProcess


class CloudSync:
    """
    Creates pipeline for cloud sync
    """

    def __init__(self, metadata=False):
        # Create pipe for connection with Sync process
        self.out_pipe, self.in_pipe = multiprocessing.Pipe(duplex=False)

        self.SyncProcess = CloudSyncProcess(out_pipe=self.out_pipe, metadata=metadata)
        self.SyncProcess.start()

    def stop(self):
        self.SyncProcess.terminate()
        self.SyncProcess.join()

    def __call__(self, path_to_folder='../'):
        self.in_pipe.send(path_to_folder)



if __name__ == '__main__':
    pass
