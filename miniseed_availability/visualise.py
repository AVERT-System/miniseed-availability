"""
Module containing methods for visualising data availability.

:copyright:
    2025, Conor A. Bacon.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import itertools
import pathlib
from datetime import datetime as dt, timedelta as td

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import NullFormatter

from .utils import SOURCE_CODES


def plot_data_availability(
    product_dir: pathlib.Path, starttime: dt, endtime: dt, stations: list
) -> plt.Figure:
    """
    Plot a horizontal bar chart showing the data availability. Thinner lines indicate
    increasingly 'gappy' data.

    No bar = no data on a given day
    Red bar = overlapping data
    Narrow coloured bar = gappy data (gaps greater than a few seconds)
    Narrow black bar = gappy data (long AND short gaps)
    Narrowest coloured bar = 'event' data (i.e., only small chunks of data available)
    Medium thickness black bar = gappy data (short gaps, likely due to telemetry dropouts)
    Thick coloured bar = full day of data

    Parameters
    ----------
    product_dir:
        Path to the data availability product archive.
    starttime:
        Date from which to visualise availabiltiy.
    endtime:
        Date up to which to visualise availability.
    stations:
        A list of station IDs, as NW.STATX, where NW and STATX are the network and
        station codes, respectively.

    Returns
    -------
     :
        Bar chart showing data availability for requested timespan and stations.

    """

    fig, ax = plt.subplots(1, figsize=(12.5, 0.75 * len(stations)), constrained_layout=True)

    labels, ticks, colourscale = [], [], []

    colours = iter(
        plt.cm.Pastel2(np.linspace(0, len(stations), len(stations) + 1) % 8 / 8)
    )
    for i, station_id in enumerate(stations):
        network, station = station_id.split(".")
        j = len(stations) - i
        colour = next(colours)
        df = pd.DataFrame()
        dfs = [
            pd.read_csv(
                product_dir
                / f"{year}/{network}/{station}"
                / f"{station_id}.{year}.availability.csv"
            )
            for year in range(starttime.year, endtime.year + 1, 1)
            if (
                product_dir
                / f"{year}/{network}/{station}"
                / f"{station_id}.{year}.availability.csv"
            ).exists()
        ]
        df = pd.concat(dfs)

        for _, row in df.iterrows():
            date = dt.strptime(row.Date, "%Y-%m-%d")

            match row.Availability:
                case 0:
                    continue
                case 0.5:  # Overlapping data
                    color, linewidth = "red", 6
                case 1:  # Gappy data
                    color, linewidth = colour, 4
                case 1.5:  # Gappy including transmission gaps
                    color, linewidth = "black", 4
                case 2:  # Event data
                    color, linewidth = colour, 2
                case 2.5:  # Transmission gaps only
                    color, linewidth = "black", 6
                case 3:  # Full day, no gaps
                    color, linewidth = colour, 10

            ax.hlines(
                j,
                date,
                date + td(days=1),
                color=color,
                linewidth=linewidth,
            )

        labels.append(station)
        ticks.append(j)
        colourscale.append(colour)

    ax.tick_params(
        which="both",
        left=True,
        right=True,
        labelleft=True,
        labelright=True,
        bottom=False,
        top=False,
        labelbottom=False,
        labeltop=False,
    )

    plt.ylim(0, len(stations) + 1)
    plt.yticks(ticks, labels, size="8")

    # Colour y labels to match lines
    gytl = ax.get_yticklabels()
    for yt, color in zip(gytl, itertools.cycle(colourscale)):
        yt.set_backgroundcolor(color)
        yt.set_bbox(dict(facecolor=color, edgecolor=color, pad=2))

    ax.tick_params(
        axis="x",
        which="both",
        length=0,
        bottom=False,
        top=False,
        labelbottom=False,
        labeltop=False,
    )
    ax.set_xlim([starttime, endtime])
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment("center")
        tick.label1.set_fontsize(9)
        tick.label2.set_horizontalalignment("center")
        tick.label2.set_fontsize(9)

    ax.tick_params(which="both", bottom=True, labelbottom=True, top=True, labeltop=True)
    ax.grid(True, which="major", axis="x")

    return fig


def visualise_entrypoint(config: dict) -> None: 
    """Entry point for the visualise command-line utility."""

    source_code = SOURCE_CODES[config["channel"][1]]

    fig = plot_data_availability(
        pathlib.Path(config["product_path"]) / f"timeseries/{source_code}/availability",
        dt.strptime(config["starttime"], "%Y-%m-%d"),
        dt.strptime(config["endtime"], "%Y-%m-%d"),
        config["stations"],
    )

    plot_dir = pathlib.Path(config["product_path"]) / f"plots/{source_code}/availability"
    plot_dir.mkdir(parents=True, exist_ok=True)

    plt.savefig(plot_dir / f"{config['filename']}.png", dpi=400, format="png")

    plt.clf()
