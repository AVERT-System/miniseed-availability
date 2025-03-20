"""
Module containing methods for computing data availability.

:copyright:
    2025, Conor A. Bacon.
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import pathlib
from datetime import datetime as dt
from itertools import chain
from statistics import mean
from typing import Generator

import obspy
import pandas as pd

from .utils import SOURCE_CODES


def peek(
    generator: Generator[pathlib.Path, None, None],
) -> Generator[pathlib.Path, None, None]:
    """
    Tests whether or not a generator (such as that returned by glob) is empty.

    Parameters
    ----------
    generator: A generator function to be tested for membership.

    Returns
    -------
    None if empty else non-iterated generated.

    """

    try:
        first = next(generator)
    except StopIteration:
        return None

    return chain([first], generator)


def evaluate_availability(station: str, file_: pathlib.Path) -> tuple[str, float]:
    """
    Checks the availability of a given station on a given date.

    Parameters
    ----------
    station: Unique identifying code for a seismometer.
    file_: Path to the given seismic data file.

    Returns
    -------
    score: {
        0.0: no data,
        0.5: overlapping data,
        1.0: data with gaps,
        1.5: data with short and long gaps,
        2.0: likely event data,
        2.5: data with just short gaps ('transmission' gaps),
        3.0: full data,
    }

    """

    date = "-".join(str(file_.name).split(".")[5:7])
    date = dt.strptime(date, "%Y-%j")

    try:
        st = obspy.read(file_, headonly=True)

        midnight = obspy.UTCDateTime("2001-001").time

        overlaps = st.get_gaps(max_gap=0.00001)
        long_gaps = st.get_gaps(min_gap=181)
        short_gaps = st.get_gaps(min_gap=0, max_gap=180)

        if overlaps:
            score = 0.5
        elif long_gaps:
            if mean([tr.stats.npts * tr.stats.delta for tr in st]) < 300:
                score = 2.0
            elif short_gaps:
                score = 1.5
            else:
                score = 1.0
        elif short_gaps:
            if mean([tr.stats.npts * tr.stats.delta for tr in st]) < 300:
                score = 2.0
            elif st.sort(keys=["starttime"])[0].stats.starttime.time > midnight.replace(
                minute=3
            ):
                score = 1.5
            else:
                score = 2.5
        elif mean([tr.stats.npts * tr.stats.delta for tr in st]) < 86400.0:
            if mean([tr.stats.npts * tr.stats.delta for tr in st]) < 300:
                score = 2.0
            else:
                score = 1.0
        else:
            score = 3.0
    except TypeError:
        score = 0.0

    print(f"      ...{date}, score: {score}...")

    return date.strftime("%Y-%m-%d"), score


def compute_entrypoint(config: dict) -> None:
    """Entry point for the compute command-line utility."""

    source_code = SOURCE_CODES[config["channel"][1]]

    for year in config["years"]:
        print(f"Evaluating availability for {year}...")
        for station_id in config["stations"]:
            print(f"   ...station {station_id}")
            network, station = station_id.split(".")
            files = sorted(
                pathlib.Path(config["archive_path"]).glob(
                    f"{year}/{network}/{station}/{config['channel']}.D/*"
                )
            )

            availability = [evaluate_availability(station, file_) for file_ in files]
            availability_df = pd.DataFrame(
                availability, columns=["Date", "Availability"]
            )

            outfile = (
                pathlib.Path(config["product_path"])
                / f"timeseries/{source_code}/availability"
                / f"{year}/{network}/{station}"
                / f"{station_id}.{year}.availability.csv"
            )
            outfile.parent.mkdir(parents=True, exist_ok=True)

            if outfile.exists():
                existing_availability_df = pd.read_csv(outfile)
                availability_df = pd.concat([availability_df, existing_availability_df])
                availability_df.drop_duplicates(subset="Date")

            if not len(availability_df.index) == 0:
                availability_df.to_csv(outfile, index=False)
