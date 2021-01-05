"""Used for the handling of parsing all command line options and controlling
for valid installation(s) etc
"""

import os
import argparse

seq_version = 0.1
seq_name = 'meta_clustering'


def create_parser():
    """Creates a command line parser, --h shows help, --version shows version.
    Required arguments: One of the main 4 arguments, -c/-r/-f/-m
    -c requires the use -i to specify input database (in FASTA)
    Optional arguments:
    """
    parser = argparse.ArgumentParser(
        prog=seq_name,
        description="""Analyse taxonomy within clusters based on sequence
        identity.""",
        epilog='Examples: ')

    parser.add_argument('-c', '--cluster', dest='opt_clustering',
                        action='store_true', default=False,
                        help="""Clustering of input database at 100%% identity
                        and preparation of files for manual review""")

    parser.add_argument('-i', '--input', dest='input', type=str, metavar='',
                        help="""{FILENAME} FASTA database to be clustered""")

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
                        help="""Creates a Metaxa2 databse from the output
                        files""")

    parser.add_argument('-ds', '--dupstats', dest='opt_ds', type=str,
                        metavar='',
                        help="""{FILENAME} FASTA database for stats""")

    parser.add_argument('-q', '--quiet', dest='log_quiet',
                        action='store_true', default=False,
                        help="""No status print out, only writing to log file
                        """)

    parser.add_argument('--version', action='version',
                        version='{}: version {}'.format(seq_name, seq_version))
    return parser


def return_args(parser):
    """Returns all arguments from command line when the script is run.
    """
    args = parser.parse_args()
    return args
