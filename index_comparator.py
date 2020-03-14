import enum
import fnmatch
import logging

class IndexComparator():
    def __init__(self, a, b, excludes = None):
        self.a = a
        self.b = b
        self.changes = Changes()
        self.excludes = excludes if excludes else []
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created new IndexComparator")

    def compare(self):
        self.logger.info("Comparing indexes")

        if len(self.excludes) > 0:
            self.logger.info("Excluding files according to {}".format(self.excludes))
            for f in self.a.get_unmatched_files():
                if any([fnmatch.fnmatch(f.filepath, e) for e in self.excludes]):
                    self.changes.add(f, None, Change.Type.EXCLUDED)
            for f in self.b.get_unmatched_files():
                if any([fnmatch.fnmatch(f.filepath, e) for e in self.excludes]):
                    self.changes.add(None, f, Change.Type.EXCLUDED)

        self.logger.info("Matching files with identical filepath")
        for a_file in self.a.get_unmatched_files():
            b_name_match = self.b.get_best_name_match(a_file)

            if b_name_match is not None:
                if a_file.is_same_contents(b_name_match):
                    self.changes.add(a_file, b_name_match, Change.Type.IDENTICAL)
                else:
                    self.changes.add(a_file, b_name_match, Change.Type.CHANGED)

        self.logger.info("Matching files with identical content")
        for a_file in self.a.get_unmatched_files():
            b_content_match = self.b.get_best_content_match(a_file)
            if b_content_match is not None:
                self.changes.add(a_file, b_content_match, Change.Type.MOVED)
            else:
                if self.b.has_file_matching_content(a_file):
                    self.changes.add(a_file, None, Change.Type.DEDUPLICATED)
                else:
                    self.changes.add(a_file, None, Change.Type.DELETED)

        self.logger.info("Adding remaining files")
        for b_file in self.b.get_unmatched_files():
            if self.a.has_file_matching_content(b_file):
                self.changes.add(None, b_file, Change.Type.DUPLICATED)
            else:
                self.changes.add(None, b_file, Change.Type.ADDED)

        # Check that we got through all files
        assert(len([f for f in self.a.get_unmatched_files()]) == 0)
        assert(len([f for f in self.b.get_unmatched_files()]) == 0)

        self.logger.debug("Sorting results")
        self.changes.sort()

    def print_changes(self, show_changes):
        self.changes.print(show_changes)

class Changes():
    def __init__(self):
        self.changes = {}

    def add(self, old, new, change_type):
        if change_type not in self.changes:
            self.changes[change_type] = []
        self.changes[change_type].append(Change(old, new, change_type))

    def sort(self):
        for changes in self.changes.values():
            changes.sort()

    def print(self, show_changes):
        for change_type in Change.Type:
            if show_changes is None or change_type in show_changes:
                for change in self.changes[change_type]:
                    print(change)

class Change():
    class Type(enum.Enum):
        EXCLUDED = "Excluded"
        IDENTICAL = "Identical"
        CHANGED = "Changed"
        MOVED = "Moved"
        DELETED = "Deleted"
        ADDED = "Added"
        DUPLICATED = "Duplicated"
        DEDUPLICATED = "Deduplicated"

    def __init__(self, old, new, change_type):
        if old is not None:
            old.matched = True
        if new is not None:
            new.matched = True

        self.old = old
        self.new = new
        self.change_type = change_type

    def __str__(self):
        return "{}: {} -> {}".format(self.change_type.value, self.old, self.new)

    def __lt__(a, b):
        if a.old is not None and b.old is not None:
            return a.old.filepath < b.old.filepath
        elif a.new is not None and b.new is not None:
            return a.new.filepath < b.new.filepath
        else:
            return True
