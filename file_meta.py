import hashlib
import os

class FileMeta():
    def __init__(self, rootdir = None, filepath = None, meta = None):
        self.matched = False
        self.error = None

        if rootdir is not None and filepath is not None and meta is None:
            self.generate(rootdir, filepath)
        elif rootdir is None and filepath is None and meta is not None:
            self.load(meta)
        else:
            raise ValueError

    def __str__(self):
        return self.filepath

    def dump(self):
        dump = {
            "filepath": self._filepath_list
        }

        if self.error is not None:
            dump["error"] = self.error
        else:
            dump["hash"] = self.hash
            dump["mtime"] = self.mtime
            dump["size"] = self.size

        return dump

    def load(self, meta):
        self._filepath_list = meta["filepath"]
        self.filepath = os.sep.join(self._filepath_list)
        if meta.get("error") is not None:
            self.error = meta["error"]
        else:
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
        self._filepath_list = filepath.split(os.sep)
        try:
            self.hash = get_hash(full_filepath)
            self.mtime = os.path.getmtime(full_filepath)
            self.size = os.path.getsize(full_filepath)
        except IOError as e:
            self.error = repr(e)

    def is_same_contents(self, did_file):
        return self.hash == did_file.hash

