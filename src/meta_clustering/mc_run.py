import time
import argparse
import os

from .cluster_tax import create_cluster_tax, repr_and_flag
from .cluster_tax import flag_correction
from .cluster_loop import cluster_loop
from .clustering import cluster_vs
from .handling import logging


def main_mc(args):
    quiet_opt = args.log_quiet

    #: running start command, clustering at 100 identity
    if args.opt_clustering:
        str_id = '100'
        float_id = 1.0
        db = args.input
        logging(str_id=str_id, db=db, quiet=quiet, start=True)
        start_time = time.time()

        cluster_vs(db, float_id)

        elapsed_time = time.time() - start_time
        logging(etime=elapsed_time, time_log=True, quiet=quiet)

        #: create tax_clusters files
        create_cluster_tax(str_id)

        #: create flag and repr cluster files
        repr_and_flag(str_id)

    #: running the manual review
    if args.opt_review:
        str_id = '100'

        #: manual review of flag file and creation of corrected repr file
        msg = "Running manual review of flagged clusters\n"
        logging(quiet=quiet, custom=True, custom_msg=msg)
        start_time = time.time()

        flag_correction(str_id)

        elapsed_time = time.time() - start_time
        logging(etime=elapsed_time, time_log=True, quiet=quiet)

    #: finalizing files and further clustering
    if args.opt_finalize:
        #: loop down from 100 to 95, clustering using the centroid files
        v_loop = [str(i) for i in range(100, 95-1, -1)]
        for id in v_loop:

            logging(str_id=id, quiet=quiet)
            start_time = time.time()

            cluster_loop(id)

            elapsed_time = time.time() - start_time
            logging(etime=elapsed_time, time_log=True, quiet=quiet)

    #: running the make database command
    if args.opt_makedb:
        pass
