"""Used for the handling of parsing all command line options and controlling
for valid installation(s) etc
"""

import os
import argparse
from .handling import get_version

seq_version = get_version()
seq_name = 'MetaxaQR Database Builder'


def create_parser():
    """Creates a command line parser, --h shows help, --version shows version.
    Required arguments: One of the main 4 arguments, -c/-r/-f/-m
    Optional arguments:
    """
    parser = argparse.ArgumentParser(
        prog=seq_name,
        description="""Create database for MetaxaQR using taxonomic database of
        genetic markers.""",
        epilog='Examples: ')

    parser.add_argument('-c', '--cluster', dest='opt_clustering', type=str,
                        metavar='',
                        help="""Clustering of input database at 100%% identity
                        and preparation of files for manual review""")

    parser.add_argument('-o', '--output', dest='output', type=str, metavar='',
                        help="""{PATH} Specify output path, path/mqr_db/...""")

    parser.add_argument('-r', '--review', dest='opt_review',
                        action='store_true', default=False,
                        help="""Manual review of flagged clusters""")

    parser.add_argument('-f', '--finalize', dest='opt_finalize',
                        action='store_true', default=False,
                        help="""Further clustering of their output centroid
                        files from manual review down to 95%% identity""")

    parser.add_argument('-m', '--makedb', dest='opt_makedb',
                        action='store_true', default=False,
                        help="""Creates a MetaxaQR database from the output
                        files""")

    parser.add_argument('-a', '--addseq', dest='opt_addseq', type=str,
                        metavar='',
                        help="""Reads FASTA format file of new entries and adds
                        to a finished database""")

    parser.add_argument('--format', dest='opt_format', type=str,
                        metavar='',
                        help="""Format used in the input FASTA file [x]""")

    parser.add_argument('--db', dest='opt_db', type=str,
                        metavar='',
                        help="""Path to finished database, used by --addseq""")

    parser.add_argument('-ds', '--dupstats', dest='opt_ds', type=str,
                        metavar='',
                        help="""{FILENAME} FASTA database for stats""")

    parser.add_argument('-q', '--quiet', dest='log_quiet',
                        action='store_true', default=False,
                        help="""No status print out, only writing to log file
                        """)

    parser.add_argument('--version', action='version',
                        version='{} - {}'.format(seq_name, seq_version))
    return parser


def return_args(parser):
    """Returns all arguments from command line when the script is run.
    """
    args = parser.parse_args()
    return args
