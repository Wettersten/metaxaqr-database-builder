"""todo

"""

import argparse
import time

from src.meta_clustering.handling import error_check
from src.meta_clustering.parsing import create_parser, return_args
from src.meta_clustering.mc_run import main_mc


if __name__ == "__main__":
    #: creates the parser and gets the arguments input by user
    parser = create_parser()
    args = return_args(parser)

    #: looks for any errors in the args provided
    error_check(args)

    #: runs the main loop of meta_clustering
    main_mc(args)
