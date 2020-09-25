import argparse
from src.meta_clustering.parsing import create_parser, return_args
from src.meta_clustering.handling import id_range_to_list
from src.meta_clustering.handling import float_to_str_id
from src.meta_clustering.handling import create_dir_structure
from src.meta_clustering.clustering import cluster_vs
from src.meta_clustering.cluster_tax import create_cluster_tax
from src.meta_clustering.cluster_tax import repr_and_flag
from src.meta_clustering.cluster_tax import flag_correction


if __name__ == "__main__":
    parser = create_parser()
    args = return_args(parser)

    print("Running Meta_clustering")
    print(args.input)

    id_range = id_range_to_list(args.identity)

    for id in id_range:
        ident = float_to_str_id(id)

        """
        #: 1) create output directories - done
        create_dir_structure(ident)

        #: 2) cluster vsearch id - todo
        print('Running VSEARCH at id: {} using database: {}'.format(
                id,
                args.input
            ))
        cluster_vs(args.input, id)

        #: 3) create tax_clusters files - test on vs_10k files
        create_cluster_tax(ident)
        """

        #: 4) create flag and repr cluster files
        repr_and_flag(ident)

        #: 5) manual review of flag file and creation of corrected repr file
        flag_correction(ident)
