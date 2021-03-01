"""Main method, compiling all module options to run the program
"""

import argparse
import os
from pathlib import Path

from .cluster_tax import create_cluster_tax, repr_and_flag, create_taxdb
from .cluster_tax import flag_correction
from .cluster_loop import cluster_loop
from .clustering import cluster_vs
from .handling import logging, return_label, print_license, return_proj_path
from .db_stats import db_dupestats
from .make_db import make_db
from .add_entries import add_entries


def main_mqrdb(args):
    """Main method, uses user args to run corresponding methods/modules
    """
    quiet = args.log_quiet

    #: running start command, clustering at 100% identity
    if args.opt_prepare:
        logging("initialize", quiet=quiet)
        str_id = '100'
        float_id = 1.0
        run_label = ''
        db = args.opt_prepare
        path = return_proj_path()

        removed_path = "{}removed".format(path)
        init_path = "{}init".format(path)
        Path(removed_path).mkdir(parents=True, exist_ok=True)
        Path(init_path).mkdir(parents=True, exist_ok=True)

        if args.opt_label:
            run_label = args.opt_label
            label_file = "{}/label".format(init_path)
            with open(label_file, 'w') as f:
                f.write(run_label)

        logging("clustering_start", quiet=quiet)
        cluster_vs(db, float_id)
        logging("clustering_seq_end", quiet=quiet)

        logging("clustering_tax_start", quiet=quiet)
        create_taxdb()
        create_cluster_tax(str_id, run_label)
        repr_and_flag(str_id)
        logging("clustering_tax_end", quiet=quiet)

        logging("clustering_end", quiet=quiet)

    #: running creation of the MetaxaQR database
    if args.opt_makedb:
        str_id = '100'
        run_label = return_label()

        #: manual review of flag file and creation of corrected repr file
        logging("manual review_start", quiet=quiet)
        flag_correction(str_id)
        logging("manual review_end", quiet=quiet)

        #: finalizing files and further clustering
        #: loop down from 100 to 50, clustering using the centroid files
        #: 100, 99, ... 90, 85, 80, ... 50
        a_loop = [str(i) for i in range(100, 90-1, -1)]
        b_loop = [str(a) for a in range(85, 50-5, -5)]
        v_loop = a_loop + b_loop

        logging("finalize_start", quiet=quiet)

        for id in v_loop:

            logging("finalize_loop_start", id=id, quiet=quiet)
            cluster_loop(id, run_label)
            logging("finalize_loop_end", id=id, quiet=quiet)

        logging("finalize_end", quiet=quiet)

        #: creating the database
        logging("make db_start", quiet=quiet)
        make_db(args.opt_qc)
        logging("make db_end", quiet=quiet)

    #: running duplicate stats method
    if args.opt_ds:
        db_dupestats(args.opt_ds)

    #: running the add new sequences method
    if args.opt_addseq:
        logging("add entries_start", quiet=quiet)
        add_entries(args.opt_addseq, args.opt_db)
        logging("add entries_end", quiet=quiet)

    #: returns the license for MetaxaQR Database Builder
    if args.opt_license:
        print_license()
