import hashlib
import os

class FileMeta():
    def __init__(self, rootdir = None, filepath = None, meta = None):
        self.matched = False

        if rootdir is not None and filepath is not None and meta is None:
            self.generate(rootdir, filepath)
        elif rootdir is None and filepath is None and meta is not None:
            self.load(meta)
        else:
            raise ValueError

    def __str__(self):
        return self.filepath

    def dump(self):
        return {
            "filepath": self._filepath_list,
            "hash": self.hash,
            "mtime": self.mtime,
            "size": self.size
        }

    def load(self, meta):
        self._filepath_list = meta["filepath"]
        self.filepath = os.sep.join(self._filepath_list)
        self.hash = meta["hash"]
        self.mtime = meta["mtime"]
        self.size = meta["size"]

    # rootdir is where the file is stored relative to pwd, needed to analyze file.
    # filepath is path under rootdir, which should be indexed.
    def generate(self, rootdir, filepath):
        def get_hash(filepath):
            hash = hashlib.sha1()
            with open(filepath, "rb") as f:
                hash.update(f.read())
            return hash.hexdigest()

        full_filepath = os.path.join(rootdir, filepath)

        self.filepath = filepath
        self.hash = get_hash(full_filepath)
        self.mtime = os.path.getmtime(full_filepath)
        self.size = os.path.getsize(full_filepath)
        self._filepath_list = filepath.split(os.sep)

    def is_same_contents(self, did_file):
        return self.hash == did_file.hash

