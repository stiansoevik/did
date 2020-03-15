Introduction
============
`did` is short for Directory Diff. It recursively compares two directories, and detects files that are added, deleted, modified or moved.

Use cases
=========
`did` is a powerful tool for auditing changes to multiple files, or verifying that files have been transferred successfully. It can be especially useful when re-organizing directories, since it can detect whether any files got lost or inadvertently modified in the process.

It can also index a directory and save the results to a file for later comparison. This allows very fast comparison, comparing directories that are deleted, compare towards an earlier version of the same directory, or comparing directories on different computers.

Examples
========
Output is truncated for readability. File names are random, and the files have been put in `old` and `new` directories with some changes done to `new`.

:warning: Examples are not update. Use --help for syntax.

Compare two directories on the fly
----------------------------------
```
# did compare old new
Moved: 85Rldjb_K0o.jpg -> album/2017/Rome/85Rldjb_K0o.jpg
Moved: eUpobvnbWIs.jpg -> album/2019/Oslo/eUpobvnbWIs.jpg
Moved: jRpyGmlucuA.jpg -> album/2018/Paris/jRpyGmlucuA.jpg
Moved: _x2l5lMRKwU.jpg -> album/_x2l5lMRKwU.jpg
Moved: ISBRo8D913Q.jpg -> album/2019/Oslo/ISBRo8D913Q.jpg
Moved: gQ-tX3xbCDA.jpg -> album/2019/Oslo/gQ-tX3xbCDA.jpg
Moved: pv8jyM-3Ous.jpg -> album/pv8jyM-3Ous.jpg
Added: None -> album/unsamples.zip
Added: None -> album/2019/Oslo/LUgZuKle8U0.jpg
Modified: U0u02uYk4Pk.jpg -> U0u02uYk4Pk.jpg
Deleted: mXDYcXjLcBI.jpg -> None
Deleted: LUgZuKle8U0.jpg -> None
```

Notice that it detects when files with identical names have been modified, or files with identical content has been moved.

Moved or renamed files can be ignored using the `-c` parameter.
Identical files can be shown using the `-i` parameter.
Files can be excluded using `--exclude <glob>` parameter.

Index directory
---------------
```
# did index old old.did -m "Indexing old directory before deletion"
```
This command scans the `old` directory, and saves the contents to `old.did`. The optional message will be displayed together with some other useful metadata (full path, time, username and host) when comparing later if the `-v` option is provided.
The index file `old.did` can then be specified instead of a directory when using `did compare`. This saves time when comparing multiple times, or allows keeping an index of an old or remote directory.

Verbose output
--------------
More verbose logging can be enabled using `-v` or even `-vv`:
```
# did -vv index old old.did
INFO:__main__:Indexing old
DEBUG:file_index:Created new index
DEBUG:file_index:Added 85Rldjb_K0o.jpg to index
DEBUG:file_index:Added eUpobvnbWIs.jpg to index
DEBUG:file_index:Added jRpyGmlucuA.jpg to index
DEBUG:file_index:Added 1LSzt81Z9w0.jpg to index
DEBUG:file_index:Added WG_3_khuYug.jpg to index
```

```
# did -v compare old.did new
INFO:__main__:Comparing changes from old.did to new
INFO:__main__:From: 2020-02-26 23:00:02 stian@matebook:/home/stian/dev/did/examples/old [old.did]
INFO:__main__:To  : 2020-02-26 23:02:29 stian@matebook:/home/stian/dev/did/examples/new [scanned now]
INFO:index_comparator:Comparing indexes
INFO:index_comparator:Matching files with identical filepath
INFO:index_comparator:Matching files with identical content
INFO:index_comparator:Adding remaining files
Moved: 85Rldjb_K0o.jpg -> album/2017/Rome/85Rldjb_K0o.jpg
Moved: eUpobvnbWIs.jpg -> album/2019/Oslo/eUpobvnbWIs.jpg
Moved: jRpyGmlucuA.jpg -> album/2018/Paris/jRpyGmlucuA.jpg
Moved: 1LSzt81Z9w0.jpg -> album/2017/Rome/1LSzt81Z9w0.jpg
Moved: xqITEzw5JDY.jpg -> album/xqITEzw5JDY.jpg
Moved: pv8jyM-3Ous.jpg -> album/pv8jyM-3Ous.jpg
Added: None -> album/unsamples.zip
Added: None -> album/2019/Oslo/LUgZuKle8U0.jpg
Modified: U0u02uYk4Pk.jpg -> U0u02uYk4Pk.jpg
Deleted: mXDYcXjLcBI.jpg -> None
Deleted: LUgZuKle8U0.jpg -> None
```

To do
=====
`did` is in an early development stage. Pull requests welcome.

Some ideas for future improvements:
- Store statistics in index (number of files, total size)?
- Display summary after indexing and comparing
- Exception handling when reading files during indexing. Retry? Store as failed?
- Update index based on changed mtime
- Package for pip or similar?
- Support non Unix path separators?
- Similarity index?
- Improve parameters. It should be possible to specify them in any order.
- Improve help text
- Support fnmatch --exclude parameters for indexing
- Optionally, group renamed directories (so that instead of printing each file, print dir)
- Display new duplicates (all that are left in b after best match, still matching an existing)
- Support searching for duplicates in only one directory?
