"""
Command-line utility for the miniSEED availability package.

:copyright:
    2025, Conor A. Bacon
:license:
    GNU General Public License, Version 3
    (https://www.gnu.org/licenses/gpl-3.0.html)

"""

import argparse
import pathlib

from .compute import compute_entrypoint
from .utils import read_config
from .visualise import visualise_entrypoint


FN_MAP = {
    "compute": compute_entrypoint,
    "visualise": visualise_entrypoint,
}


def entrypoint(args=None):
    """
    A command-line interface for the server-side command-line interface for building
    data visualisations.

    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        help="top-level command used to select between compute and visualise modes.",
        choices=FN_MAP.keys(),
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Specify the path to a configuration file.",
        required=True,
    )
    args = parser.parse_args()

    config = read_config(pathlib.Path(args.config))

    FN_MAP[args.mode](config[args.mode])
