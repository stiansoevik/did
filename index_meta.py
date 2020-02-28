import datetime
import getpass
import os
import socket
import time

class IndexMeta():
    def __init__(self):
        self.meta = None
        self.index_file = None

    def generate(self, rootdir, description = None):
        self.meta = {
            "version": 0,
            "rootdir": os.path.abspath(rootdir),
            "scan_ts": time.time(),
            "username": getpass.getuser(),
            "hostname": socket.gethostname(),
            "description": description,
        }

    def load(self, meta, index_file_name = None):
        self.index_file = index_file_name
        self.meta = meta

    def dump(self):
        return self.meta

    def __str__(self):
        date = datetime.datetime.fromtimestamp(self.meta["scan_ts"]).strftime("%Y-%m-%d %H:%M:%S")
        string = "{} {}@{}:{}".format(date, self.meta["username"], self.meta["hostname"], self.meta["rootdir"])
        if self.index_file is not None:
            string += " [{}]".format(self.index_file)
        else:
            string += " [scanned now]"
        if self.meta["description"] is not None:
            string += " ({})".format(self.meta["description"])
        return string
