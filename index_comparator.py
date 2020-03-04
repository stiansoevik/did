import fnmatch
import logging

class IndexComparator():
    class Change():
        EXCLUDED = "Excluded"
        IDENTICAL = "Identical"
        CHANGED = "Changed"
        MOVED = "Moved"
        DELETED = "Deleted"
        ADDED = "Added"

    def __init__(self, a, b, excludes = None):
        self.a = a
        self.b = b
        self.changes = []
        self.excludes = excludes if excludes else []
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created new IndexComparator")

    def compare(self):
        self.logger.info("Comparing indexes")

        if len(self.excludes) > 0:
            self.logger.info("Excluding files according to {}".format(self.excludes))
            for f in self.a.get_unmatched_files():
                if any([fnmatch.fnmatch(f.filepath, e) for e in self.excludes]):
                    self.add_change(f, None, IndexComparator.Change.EXCLUDED)
            for f in self.b.get_unmatched_files():
                if any([fnmatch.fnmatch(f.filepath, e) for e in self.excludes]):
                    self.add_change(None, f, IndexComparator.Change.EXCLUDED)

        self.logger.info("Matching files with identical filepath")
        for a_file in self.a.get_unmatched_files():
            b_name_match = self.b.get_best_name_match(a_file)

            if b_name_match is not None:
                if a_file.is_same_contents(b_name_match):
                    self.add_change(a_file, b_name_match, IndexComparator.Change.IDENTICAL)
                else:
                    self.add_change(a_file, b_name_match, IndexComparator.Change.CHANGED)

        self.logger.info("Matching files with identical content")
        for a_file in self.a.get_unmatched_files():
            b_content_match = self.b.get_best_content_match(a_file)
            if b_content_match is not None:
                self.add_change(a_file, b_content_match, IndexComparator.Change.MOVED)
            else:
                self.add_change(a_file, None, IndexComparator.Change.DELETED)

        self.logger.info("Adding remaining files")
        for b_file in self.b.get_unmatched_files():
            self.add_change(None, b_file, IndexComparator.Change.ADDED)

        # Check that we got through all files
        assert(len([f for f in self.a.get_unmatched_files()]) == 0)
        assert(len([f for f in self.b.get_unmatched_files()]) == 0)

    def add_change(self, old, new, change):
        self.logger.debug("{} ({} -> {})".format(change, old, new))
        self.changes.append({"old": old, "new": new, "change": change})
        if old is not None:
            old.matched = True
        if new is not None:
            new.matched = True

    def print_changes(self, show_identical, show_moved, show_added, show_changed, show_deleted):
        show_changes = []
        if show_identical:
            show_changes.append(IndexComparator.Change.IDENTICAL)
        if show_moved:
            show_changes.append(IndexComparator.Change.MOVED)
        if show_added:
            show_changes.append(IndexComparator.Change.ADDED)
        if show_changed:
            show_changes.append(IndexComparator.Change.CHANGED)
        if show_deleted:
            show_changes.append(IndexComparator.Change.DELETED)

        for change in show_changes:
            for c in [c for c in self.changes if c["change"] == change]:
                print("{}: {} -> {}".format(c["change"], c["old"], c["new"]))
