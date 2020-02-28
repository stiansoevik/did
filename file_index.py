import file_meta
import index_meta
import logging
import json
import os

class FileIndex():
    def __init__(self, name = None):
        self.file_index = {}
        self.hash_index = {}
        self.name = name

        if name is not None:
            self.logger = logging.getLogger("{} [{}]".format(__name__, name))
        else:
            self.logger = logging.getLogger(__name__)

        self.logger.debug("Created new index")

    def __str__(self):
        return str(self.meta)

    def add_file(self, file_meta):
        self.logger.debug("Added {} to index".format(file_meta))
        self.file_index[file_meta.filepath] = file_meta

        if file_meta.hash not in self.hash_index:
            self.hash_index[file_meta.hash] = [file_meta]
        else:
            self.hash_index[file_meta.hash].append(file_meta)

    def get_unmatched_files(self):
        self.logger.debug("Getting {} unmatched files".format(len([f for f in self.file_index.values() if not f.matched])))
        for f in self.file_index.values():
            if not f.matched:
                yield f

    def get_best_name_match(self, did_file):
        match = self.file_index.get(did_file.filepath, None)
        if match is not None and match.matched == False:
            self.logger.debug("Exact name match for {}".format(did_file))
            return match
        else:
            self.logger.debug("No exact name match for {}".format(did_file))
            return None

    # TODO Can FileMeta have match_name([list]) and match_content([list]) instead?
    def get_best_content_match(self, did_file):
        candidates = [c for c in self.hash_index.get(did_file.hash, []) if c.matched == False]
        if len(candidates) == 0:
            self.logger.debug("No content match for {}".format(did_file))
            return None
        elif len(candidates) == 1:
            self.logger.debug("Unique content match for {}".format(did_file))
            return candidates[0]
        else:
            mtime_candidates = [c for c in candidates if c.mtime == did_file.mtime]
            self.logger.debug("Mtime candidates for {}: {}".format(did_file, ", ".join(map(str, mtime_candidates))))
            # TODO This does not seem to match when moving file, fix or remove?
            if len(mtime_candidates) == 1:
                self.logger.debug("Unique mtime match for {}".format(did_file))
                return mtime_candidates[0]
            else:
                # TODO Is best match when file name and end of path matches, or only end of path? (moved vs renamed file)
                match_length = 1
                name_candidates = candidates
                while match_length < len(did_file._filepath_list): # TODO Expose or match in class
                    matching_candidates = [c for c in name_candidates if c._filepath_list[-match_length] == did_file._filepath_list[-match_length]]
                    if len(matching_candidates) > 0:
                        name_candidates = matching_candidates
                        match_length = match_length + 1
                    else:
                        break
                self.logger.debug("Longest name match for {} of {}".format(did_file, ", ".join(map(str, candidates))))
                return name_candidates[0]

    def scan_dir(self, scan_path, message = None):
        self.meta = index_meta.IndexMeta()
        self.meta.generate(scan_path, message) # TODO In initializer?

        scan_path_length = len(os.path.normpath(scan_path)) + 1
        for dirpath, dirnames, filenames in os.walk(scan_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)[scan_path_length:]
                self.add_file(file_meta.FileMeta(rootdir = scan_path, filepath = filepath))

    def save(self, index_file_name):
        with open(index_file_name, "w") as f:
            f.write(json.dumps(self.meta.dump(), ensure_ascii = False) + os.linesep)
            for file_meta in self.file_index.values():
                serialized = json.dumps(file_meta.dump(), ensure_ascii = False)
                f.write(serialized + os.linesep)

    def load(self, index_file_name):
        self.logger.debug("Loading index from {}".format(index_file_name))
        with open(index_file_name, "r") as f:
            self.meta = index_meta.IndexMeta()
            self.meta.load(json.loads(f.readline()), index_file_name)
            for line in f:
                file_dict = json.loads(line)
                self.add_file(file_meta.FileMeta(meta = file_dict))
