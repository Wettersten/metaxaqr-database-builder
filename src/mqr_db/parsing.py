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

    parser.add_argument('-p', '-prepare', dest='opt_prepare', type=str,
                        metavar='',
                        help="""Clustering of input database at 100%% identity
                        and preparation of files for manual review""")

    parser.add_argument('--label', dest='opt_label', type=str,
                        metavar='',
                        help="""{label} Specify label for the output database,
 required when running --prepare""")

    parser.add_argument('--format', dest='opt_format', type=str,
                        metavar='',
                        help="""Format used in the input database, supported
 formats: {ibol, unite""")

    parser.add_argument('--taxfile', dest='opt_taxfile', type=str,
                        metavar='', help="Taxonomy file")

    parser.add_argument('--qc', dest='opt_qc', type=str,
                        metavar='',
                        help="""Quality check options, several can be used at
 the same time [slt], s&t works in -p, l works in -md.
    [s]: (s)equence quality - Removes entries not passing length/region check.
    [l]: (l)ow quantity cluster - Removes clusters with no related clusters.
    [t]: (t)axonomy quality - Remove entries with differing taxonomies.""")

    parser.add_argument('--gene_marker', dest='opt_gene_marker', type=str,
                        metavar='',
                        help="""Gene marker used for quality sequence checks,
 e.g. SSU""")

    parser.add_argument('-md', '--makedb', dest='opt_makedb',
                        action='store_true', default=False,
                        help="""Starts the manual review followed creation of
                        the output MetaxaQR database files""")

    parser.add_argument('--keep', dest='opt_keep',
                        action='store_true', default=False,
                        help="""Keeps intermediate files after run""")

    parser.add_argument('--exclude_all_flags', dest='opt_exclude_all',
                        action='store_true', default=False,
                        help="""Skips the manual review step by excluding all
 flagged clusters""")

    parser.add_argument('-mh', '--makehmms', dest='opt_makehmms', type=str,
                        metavar='',
                        help="""Creates HMMs from the MetaxaQR Database using
                        3 different modes (divergent, conserved, hybrid)
                        """)

    parser.add_argument('--conservation_length', dest='opt_con_len', type=int,
                        metavar='', default=20,
                        help="""Minimum length required for a conserved region
                        used to make HMMs (default=20)""")

    parser.add_argument('--look_ahead', dest='opt_look_ahead', type=int,
                        metavar='', default=4,
                        help="""Number of bases/amino acids to look ahead when
                        creating the conserved region, ignoring small sections
                        of non-conserved nucleotides/amino acids
                        (default=4)""")

    parser.add_argument('--conservation_cutoff', dest='opt_con_cutoff',
                        type=float, metavar='', default=0.6,
                        help="""Consensus cutoff point for nucleotides/amino
                        acids in the alignment, between 0-1 (default=0.6)""")

    parser.add_argument('--max_gaps', dest='opt_max_gaps',
                        type=int, metavar='', default=5,
                        help="""Maximum number of gaps allowed in a conserved
                        region (default=5)""")

    parser.add_argument('--conservation_seq_id', dest='opt_con_seq_id',
                        type=str, metavar='', default="50",
                        help="""Sequence id used to create the HMMs from
                        (default=50)""")

    parser.add_argument('--conservation_seq_db', dest='opt_con_seq_db',
                        type=str, metavar='',
                        help="""Database to create HMMs from, when using the
                        hybrid mode.""")

    parser.add_argument('-a', '--addseq', dest='opt_addseq', type=str,
                        metavar='',
                        help="""Reads FASTA format file of new entries and adds
                        to a finished database""")

    parser.add_argument('--quiet', dest='opt_quiet',
                        action='store_true', default=False,
                        help="""No status print out""")

    parser.add_argument('--cpu', dest='opt_cpu', type=int, default=4,
                        help="""Threads used (default=4)""")

    parser.add_argument('--license', dest='opt_license',
                        action='store_true', default=False,
                        help="""Displays the license""")

    parser.add_argument('--version_history', dest='opt_version_history',
                        action='store_true', default=False,
                        help="""Displays the version history""")

    parser.add_argument('--version', action='version',
                        version='{} - {}'.format(seq_name, seq_version))
    return parser


def return_args(parser):
    """Returns all arguments from command line when the script is run.
    """
    args = parser.parse_args()
    return args
