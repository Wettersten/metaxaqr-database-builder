"""Used for the handling of parsing all command line options and controlling
for valid installation(s) etc
"""

import os.path
from os import path
import argparse

seq_version = 0.1
seq_name = 'meta_clustering'


def create_parser():
    """Creates a command line parser, --h shows help, --version shows version.
    Required arguments:
    Optional arguments:
    """
    parser = argparse.ArgumentParser(
        prog=seq_name,
        description="""Analyse taxonomy within clusters based on sequence
        identity.""",
        epilog='Examples: ')
    parser.add_argument('-i', dest='input', type=str, required=True,
                        help="""{FILENAME} FASTA database to be analysed""")
    parser.add_argument('-id', dest='identity', type=str, required=True,
                        help="""{REAL/REAL-REAL} Identity cutoff used in
                        clustering, either a single identity (1.0) or a range
                        (0.95-1.0). Using a range results in clustering at each
                        identity in the range.
                        """)
    parser.add_argument('-p', dest='path', type=str,
                        help="""{PATH} Specify output path.""")
    parser.add_argument('--format', dest='file_format',
                        default='silva_tax_trunc',
                        choices=['silva_tax_trunc', 'genbank'],
                        help="""{genbank, meta, silva_tax_trunc} Format of the
                        input file (default: silva_tax_trunc)""")
    parser.add_argument('--gc', dest='gc_parse', action='store_true',
                        default=False,
                        help=""" Display GC content (%%) of sequences (default:
                         off)""")
    parser.add_argument('--version', action='version',
                        version='{}: version {}'.format(seq_name, seq_version))
    return parser


def return_args(parser):
    """Returns all arguments from command line when the script is run.
    """
    args = parser.parse_args()
    return args


def check_file(file):
    """Checks if the file input from the command line arguments is valid, quits
    otherwise.
    """
    error_msg = "Could not find the file: {}".format(file)
    if not os.path.isfile(file):
        quit(error_msg)


def check_installation():
    """Checks if valid installation; Vsearch + ?
    """
    pass
