"""Main MetaxaQR Database Builder
"""

import argparse
import time

from src.mqr_db.handling import error_check
from src.mqr_db.parsing import create_parser, return_args
from src.mqr_db.mqrdb_run import main_mqrdb


if __name__ == "__main__":
    #: creates the parser and gets the arguments input by user
    parser = create_parser()
    args = return_args(parser)

    #: runs the main loop of meta_clustering
    main_mqrdb(args)
