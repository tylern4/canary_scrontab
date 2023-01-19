#!/usr/bin/env python

from datetime import datetime
from pathlib import Path
import time
import logging
import numpy as np
import h5py

from argparse import ArgumentParser
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "CRITICAL"))


class FileWriter:
    def __init__(self, file_name: Path) -> None:
        self.write_header = False if file_name.exists() else True
        self.write_file = open(file_name, 'a')

    def __del__(self):
        logging.debug("Closing file")
        self.write_file.close()

    def __write_array(self, data: list):
        data = [str(d) for d in data]
        output_string = ",".join(data) + "\n"
        self.write_file.write(output_string)

    def write(self, data: dict):
        if self.write_header:
            self.__write_array(data.keys())
            self.write_header = False
        self.__write_array(data.values())


def count_files(canary_dir: Path, output):
    output["glob_start"] = time.perf_counter()
    out = canary_dir.glob("*")
    output["glob_end"] = time.perf_counter()
    output["glob"] = len(list(out))


def dir_size(canary_dir: Path, output):
    all_files = canary_dir.glob("*")
    output["dir_size_start"] = time.perf_counter()
    out = [f.stat().st_size for f in all_files]
    output["dir_size_end"] = time.perf_counter()
    output["dir_size"] = sum(out)


def write_bytes(canary_dir: Path, output, num_mb=10):
    a = np.random.random(size=(4096, 4096))
    test_file = Path(canary_dir / ".tempfile")
    output["write_file_start"] = time.perf_counter()
    h5f = h5py.File(test_file, 'w')
    h5f.create_dataset('dataset_1', data=a)
    h5f.close()
    output["write_file_end"] = time.perf_counter()
    logging.debug(f"File size: {test_file.stat().st_size} bytes")

    output["write_file"] = test_file.stat().st_size
    output["read_file"] = test_file.stat().st_size
    output["read_file_start"] = time.perf_counter()
    h5f = h5py.File(test_file, 'r')
    b = h5f['dataset_1'][:]
    h5f.close()
    output["read_file_end"] = time.perf_counter()
    test_file.unlink()


def get_dir_contents(canary_dir: Path, file_name):
    output_file = FileWriter(file_name)
    output = {"@timestamp": str(datetime.now()), "path": canary_dir.as_posix()}

    count_files(canary_dir, output)
    dir_size(canary_dir, output)
    write_bytes(canary_dir, output)

    output_file.write(output)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--path", help="Path to get test", required=True, nargs='+')
    parser.add_argument("-o", "--output", help="Path to output file",
                        required=False,
                        default=None)

    args = parser.parse_args()

    canary_dirs = [Path(d) for d in args.path]
    outout_file_name = Path(
        args.output) if args.output is not None else Path("canary.csv")
    logging.debug(f"Writing data for {canary_dirs} to file {outout_file_name}")

    for canary in canary_dirs:
        if canary.exists():
            get_dir_contents(canary_dir=canary, file_name=outout_file_name)
        else:
            print(f"Dir not found {canary}")
