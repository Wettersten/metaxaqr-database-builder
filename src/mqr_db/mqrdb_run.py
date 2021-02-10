"""Main method, compiling all module options to run the program
"""

import argparse
import os

from .cluster_tax import create_cluster_tax, repr_and_flag, create_taxdb
from .cluster_tax import flag_correction
from .cluster_loop import cluster_loop
from .clustering import cluster_vs
from .handling import logging, set_proj_path
from .db_stats import db_dupestats
from .make_db import make_db
from .add_entries import add_entries


def main_mqrdb(args):
    """Main method, uses user args to run corresponding methods/modules
    """
    quiet = args.log_quiet

    #: running start command, clustering at 100% identity
    if args.opt_clustering:
        logging("initialize", quiet=quiet)
        str_id = '100'
        float_id = 1.0
        db = args.opt_clustering
        if args.output:
            path = args.output
            set_proj_path(path)

        logging("clustering_start", quiet=quiet)
        cluster_vs(db, float_id)
        logging("clustering_seq_end", quiet=quiet)

        logging("clustering_tax_start", quiet=quiet)
        create_taxdb()
        create_cluster_tax(str_id)
        repr_and_flag(str_id)
        logging("clustering_tax_end", quiet=quiet)

        logging("clustering_end", quiet=quiet)

    #: running the manual review
    if args.opt_review:
        str_id = '100'

        #: manual review of flag file and creation of corrected repr file

        logging("manual review_start", quiet=quiet)
        flag_correction(str_id)
        logging("manual review_end", quiet=quiet)

    #: finalizing files and further clustering
    if args.opt_finalize:
        #: loop down from 100 to 50, clustering using the centroid files
        #: 100, 99, ... 90, 85, 80, ... 50
        a_loop = [str(i) for i in range(100, 90-1, -1)]
        b_loop = [str(a) for a in range(85, 50-5, -5)]
        v_loop = a_loop + b_loop

        logging("finalize_start", quiet=quiet)

        for id in v_loop:

            logging("finalize_loop_start", id=id, quiet=quiet)
            cluster_loop(id)
            logging("finalize_loop_end", id=id, quiet=quiet)

        logging("finalize_end", quiet=quiet)

    #: running the make database command
    if args.opt_makedb:
        logging("make db_start", quiet=quiet)
        make_db()
        logging("make db_end", quiet=quiet)

    #: running duplicate stats method
    if args.opt_ds:
        db_dupestats(args.opt_ds)

    #: running the add new sequences method
    if args.opt_addseq:
        logging("add entries_start", quiet=quiet)
        add_entries(args.opt_addseq, args.opt_db)
        logging("add entries_end", quiet=quiet)
