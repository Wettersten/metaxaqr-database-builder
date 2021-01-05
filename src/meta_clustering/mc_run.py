import time
import argparse
import os

from .cluster_tax import create_cluster_tax, repr_and_flag, create_taxdb
from .cluster_tax import flag_correction
from .cluster_loop import cluster_loop
from .clustering import cluster_vs
from .handling import logging, set_proj_path
from .db_stats import db_dupestats
from .make_db import make_db


def main_mc(args):
    """Main method, uses user args to run corresponding methods/modules
    """
    quiet = args.log_quiet

    #: running start command, clustering at 100 identity
    if args.opt_clustering:
        str_id = '100'
        float_id = 1.0
        db = args.input
        if args.output:
            path = args.output
            set_proj_path(path)

        logging(str_id=str_id, db=db, quiet=quiet, start=True)
        start_time = time.time()

        cluster_vs(db, float_id)

        elapsed_time = time.time() - start_time
        logging(etime=elapsed_time, time_log=True, quiet=quiet)

        #: create tax_db
        create_taxdb()

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
        #: loop down from 100 to 50, clustering using the centroid files
        #: 100, 99, ... 90, 85, 80, ... 50
        a_loop = [str(i) for i in range(100, 90-1, -1)]
        b_loop = [str(a) for a in range(85, 50-5, -5)]
        v_loop = a_loop + b_loop

        for id in v_loop:

            logging(str_id=id, quiet=quiet)
            start_time = time.time()

            cluster_loop(id)

            elapsed_time = time.time() - start_time
            logging(etime=elapsed_time, time_log=True, quiet=quiet)

    #: running the make database command
    if args.opt_makedb:
        makedb()

    #: running duplicate stats method
    if args.opt_ds:
        db_dupestats(args.opt_ds)
