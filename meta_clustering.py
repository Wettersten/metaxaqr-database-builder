import argparse

from src.meta_clustering.parsing import create_parser, return_args

from src.meta_clustering.handling import id_range_to_list
from src.meta_clustering.handling import float_to_str_id

from src.meta_clustering.clustering import cluster_vs

from src.meta_clustering.cluster_tax import create_cluster_tax
from src.meta_clustering.cluster_tax import repr_and_flag
from src.meta_clustering.cluster_tax import flag_correction

from src.meta_clustering.cluster_loop import cluster_loop


if __name__ == "__main__":
    parser = create_parser()
    args = return_args(parser)

    print("Running Meta_clustering")
    print(args.input)

    id_range = id_range_to_list(args.identity)

    id = id_range[0]
    ident = float_to_str_id(id)

    #: 1) cluster vsearch id -
    print('Running VSEARCH at id: {} using database: {}'.format(
            ident,
            args.input
        ))
    cluster_vs(args.input, id)

    #: 2) create tax_clusters files - test on vs_10k files
    create_cluster_tax(ident)

    #: 3) create flag and repr cluster files
    repr_and_flag(ident)

    #: 4) manual review of flag file and creation of corrected repr file
    flag_correction(ident)

    #: 5) loop down from 100 to 95, clustering using the centroid files
    v_loop = [str(i) for i in range(100, 95-1, -1)]
    for id in v_loop:
        print('Running VSEARCH at id: {} using database: {}'.format(
                id,
                args.input
            ))
        cluster_loop(id)
