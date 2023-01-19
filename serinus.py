#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from argparse import ArgumentParser
from pathlib import Path
import os
import logging


logging.basicConfig(level=os.environ.get("LOGLEVEL", "WARNING"))


def ploter(data: pd.DataFrame, kind: str, name: Path):
    fig, ax = plt.subplots()
    ax.plot(pd.to_datetime(data[f'{kind}_start'], unit='s'),
            data[f'{kind}'])
    ax.set_ylim(bottom=0)
    fig.savefig(name.as_posix() + f"_{kind}_count" + ".png")

    fig, ax = plt.subplots()
    delta_time = (data[f'{kind}_end'] - data[f'{kind}_start'])
    ax.plot(pd.to_datetime(data[f'{kind}_start'], unit='s'),
            delta_time)

    ax.set_ylim(bottom=0)
    fig.savefig(name.as_posix() + f"_{kind}_time" + ".png")


def make_time_plots(dataframe: pd.DataFrame, output_dir: Path):
    paths = dataframe.groupby('path')

    for directory, data in paths:
        name = output_dir / (directory[1:].replace("/", "_"))
        ploter(data=data, kind="glob", name=name)
        ploter(data=data, kind="dir_size", name=name)
        ploter(data=data, kind="write_file", name=name)
        ploter(data=data, kind="read_file", name=name)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="Path to get csv file", required=True)
    parser.add_argument("-o", "--output", help="Path to output directory",
                        required=False,
                        default=None)

    args = parser.parse_args()

    input_file = Path(args.input)
    if not input_file.exists():
        logging.error(f"Input file not found {input_file}")
        exit(1)

    output_dir = Path(args.output) if args.output is not None \
        else Path().cwd() / input_file.stem.replace(" ", "_")
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file) as header_read:
        header = header_read.readline().split(",")

    df = pd.read_csv(input_file)

    make_time_plots(df, output_dir=output_dir)
