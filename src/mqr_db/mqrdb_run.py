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
from .handling import cleanup, format_file, sep_tax, get_v_loop, check_file
from .handling import print_updates, check_installation, error_check
from .make_db import make_db
from .add_entries import add_entries
from .make_hmms import make_hmms


def main_mqrdb(args):
    """Main method, uses user args to run corresponding methods/modules
    """
    quiet = args.opt_quiet

    #: running start command, clustering at 100% identity
    if args.opt_prepare:
        error_check(args)
        check_installation(args)
        logging("initialize", quiet=quiet)
        str_id = '100'
        float_id = 1.0
        run_label = "tmp"
        db = args.opt_prepare
        qc_sequence_quality = False
        qc_taxonomy_quality = False

        if args.opt_label:
            run_label = args.opt_label

        tmp_dir = f"{os.getcwd()}/tmp"
        removed_path = f"{tmp_dir}/removed/"
        init_path = f"{tmp_dir}/init/"
        proj_path = return_proj_path(run_label)
        Path(removed_path).mkdir(parents=True, exist_ok=True)
        Path(init_path).mkdir(parents=True, exist_ok=True)
        Path(proj_path).mkdir(parents=True, exist_ok=True)

        label_file = f"{init_path}label"
        with open(label_file, 'w') as f:
            f.write(run_label)

        if args.opt_taxfile:
            db = sep_tax(db, args.opt_taxfile)

        #: formatting if another format is used in the database
        if args.opt_format:
            db = format_file(db, args.opt_format)

        #: gets quality checking options
        if args.opt_qc:
            qc_opts = str(args.opt_qc).lower()
            if "s" in qc_opts:
                qc_sequence_quality = True
            if "t" in qc_opts:
                qc_taxonomy_quality = True

        gene_marker = ""
        if args.opt_gene_marker:
            gene_marker = str(args.opt_gene_marker).lower()

        logging("clustering_start", quiet=quiet)
        cluster_vs(db, float_id, run_label)
        logging("clustering_seq_end", quiet=quiet)

        logging("clustering_tax_start", quiet=quiet)
        create_taxdb()
        create_cluster_tax(
                           str_id,
                           run_label,
                           qc_taxonomy_quality,
                           qc_sequence_quality,
                           gene_marker=gene_marker
                           )
        repr_and_flag(str_id)
        logging("clustering_tax_end", quiet=quiet)

        logging("clustering_end", quiet=quiet)

    #: running creation of the MetaxaQR database
    if args.opt_makedb:
        error_check(args)
        check_installation(args)
        str_id = '100'
        run_label = ''
        if args.opt_label:
            run_label = args.opt_label
        else:
            run_label = return_label()
        exclude_all = False
        path = return_proj_path(run_label)
        if args.opt_exclude_all:
            exclude_all = True

        #: initializing quality check options
        qc_limited_clusters = False
        gene_marker = ""  # TODO remove - replace if not needed
        qc_sequence_quality = False  # TODO remove - check in /removed instead
        qc_taxonomy_quality = False  # TODO remove - check in /removed instead

        if args.opt_qc:
            qc_opts = str(args.opt_qc).lower()
            if "l" in qc_opts:
                qc_limited_clusters = True

        #: manual review of flag file and creation of corrected repr file
        logging("manual review_start", quiet=quiet)
        flag_correction(str_id, exclude_all)
        logging("manual review_end", quiet=quiet)

        #: finalizing files and further clustering
        #: loop down from 100 to 50, clustering using the centroid files
        v_loop = get_v_loop()

        logging("finalize_start", quiet=quiet)

        for id in v_loop:

            logging("finalize_loop_start", id=id, quiet=quiet)
            cluster_loop(
                         id,
                         run_label,
                         qc_sequence_quality,
                         gene_marker
                        )
            logging("finalize_loop_end", id=id, quiet=quiet)

        logging("finalize_end", quiet=quiet)

        #: creating the database
        logging("make db_start", quiet=quiet)
        make_db(run_label, qc_limited_clusters, qc_taxonomy_quality)
        logging("make db_end", quiet=quiet)

        #: cleans up intermediate files after process
        cleanup("md", args.opt_keep, run_label)

    #: running the make HMMs method
    if args.opt_makehmms:
        error_check(args)
        check_installation(args)
        run_label = ''
        if args.opt_label:
            run_label = args.opt_label
        else:
            run_label = return_label()
        tree_file = f"{Path(return_proj_path(run_label)).parent}/mqr.tree"
        mode = args.opt_makehmms
        logging("make hmms_start", quiet=quiet)
        make_hmms(
                 mode,
                 tree_file,
                 run_label,
                 seq_id=str(args.opt_con_seq_id),
                 seq_db=args.opt_con_seq_db,
                 cpu=args.opt_cpu
                 )
        logging("make hmms_end", quiet=quiet)

        #: cleans up intermediate files after process
        cleanup("mh", args.opt_keep, run_label)

    #: running the add new sequences method
    if args.opt_addseq:
        db = args.opt_addseq

        if args.opt_format:
            db = format_file(db, args.opt_format)

        logging("add entries_start", quiet=quiet)
        add_entries(db, args.opt_db)
        logging("add entries_end", quiet=quiet)

    #: returns the license for MetaxaQR Database Builder
    if args.opt_license:
        print_license()

    #: prints the version history
    if args.opt_version_history:
        print_updates()
