import argparse
import time

from src.meta_clustering.handling import error_check
from src.meta_clustering.parsing import create_parser, return_args
from src.meta_clustering.mc_run import main_mc


if __name__ == "__main__":
    parser = create_parser()
    args = return_args(parser)

    error_check(args)

    #: check args for any problems, such as missing input etc TODO
    #: quit with error msg if any errors TODO

    main_mc(args)
