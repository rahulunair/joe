#!usr/bin/env python
import json
import sys
from collections import defaultdict
from hashlib import blake2b, md5
from pathlib import Path
from time import perf_counter

import tqdm

class DupException(Exception):
    pass

def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stdout)


def chksum(fname):
    """hash file."""
    h = blake2b()
    try:
        with open(fname, "rb") as fh:
            while chunk := fh.read(128 * h.block_size):
                h.update(chunk)
    except OSError as e:
        eprint(e)
        raise OSError("file descriptor error")
    return h.hexdigest().strip()[:15]


def files(file_type):
    return (path for path in Path(".").rglob(file_type) if path.is_file())


def f_hash(path=".", file_type="*.*"):
    dup_size = 0
    hashed_files = defaultdict(list)
    duplicate_files = defaultdict(list)
    time_1 = perf_counter()

    for f in tqdm.tqdm(files(file_type)):
        try:
            key = chksum(f)
        except DupException:
            continue
        if key in hashed_files:
            dup_size += f.stat().st_size
            duplicate_files[key].append(str(f))
            duplicate_files[key].append(str(hashed_files[key]))
        else:
            hashed_files[key] = f

    print(f"total size of duplicate files:: {dup_size / 10 ** 6} MB")
    print(f"time taken: {perf_counter() - time_1}")
    print("saving duplicate files to dups.json")
    json.dump(duplicate_files, open("dups.json", "w"))


if __name__ == "__main__":
    f_hash()
