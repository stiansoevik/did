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
        self.meta = None

        if name is not None:
            self.logger = logging.getLogger("{} [{}]".format(__name__, name))
        else:
            self.logger = logging.getLogger(__name__)

        self.logger.debug("Created new index")

    def __str__(self):
        return str(self.meta)

    def add_file(self, file_meta):
        if file_meta.error is not None:
            self.logger.warning("Error adding {} to index: {}".format(file_meta.filepath, file_meta.error))
            return

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
        self.logger.debug("Content match candidates for {}: {}".format(did_file, ", ".join(map(str, candidates))))
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
                def match_length(a, b):
                    matching_length = 0
                    while True:
                        next_check_pos = matching_length + 1
                        if matching_length == len(a) or matching_length == len(b):
                            return matching_length
                        if (a[-next_check_pos] == b[-next_check_pos]):
                            matching_length = next_check_pos
                        else:
                            return matching_length

                longest_matching_candidate = candidates[0] # Must choose one as default
                longest_matching_length = match_length(longest_matching_candidate._filepath_list, did_file._filepath_list)
                for c in candidates:
                   if match_length(c._filepath_list, did_file._filepath_list) > longest_matching_length:
                       longest_matching_candidate = c
                self.logger.debug("Longest name match for {}: {}".format(did_file, longest_matching_candidate))
                return longest_matching_candidate

    def add_path(self, path):
        # Returns True if did index, False if directory, raises exception if invalid
        def is_index(path):
            if os.path.isdir(path):
                return False
            if not os.path.isfile(path):
                raise IOError("{} does not exist".format(path))
            return True

        if is_index(path):
            self.load(path)
        else:
            self.scan_dir(path)

    def scan_dir(self, scan_path, message = None):
        if self.meta is None:
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
            meta = index_meta.IndexMeta()
            meta.load(json.loads(f.readline()), index_file_name)
            self.logger.debug("Loaded {}".format(meta))
            if self.meta is None:
                self.meta = meta
            else:
                f.readline() # Throw away meta
            for line in f:
                file_dict = json.loads(line)
                self.add_file(file_meta.FileMeta(meta = file_dict))
