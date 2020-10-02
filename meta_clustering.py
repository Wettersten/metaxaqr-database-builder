import argparse
import time

from src.meta_clustering.parsing import create_parser, return_args

from src.meta_clustering.handling import id_range_to_list
from src.meta_clustering.handling import float_to_str_id
from src.meta_clustering.handling import logging

from src.meta_clustering.clustering import cluster_vs

from src.meta_clustering.cluster_tax import create_cluster_tax
from src.meta_clustering.cluster_tax import repr_and_flag
from src.meta_clustering.cluster_tax import flag_correction

from src.meta_clustering.cluster_loop import cluster_loop


if __name__ == "__main__":
    parser = create_parser()
    args = return_args(parser)

    #: check args for any problems, such as missing input etc TODO
    #: quit with error msg if any errors

    #: running the start clustering command
    #: make into separate method TODO
    if args.opt_clustering:
        #: cluster vsearch id -
        id = 1.0
        ident = float_to_str_id(id)

        log_msg = "Running VSEARCH at id: {} using database: {}".format(
                ident,
                args.input
            )
        time_log_msg = "Done in Hours:Minutes:Seconds"
        logging(log_msg, start=True)
        start_time = time.time()

        cluster_vs(args.input, id)

        elapsed_time = time.time() - start_time
        time_msg = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        log_msg = "{}\n{}\n\n".format(time_log_msg, time_msg)
        logging(log_msg)

        #: create tax_clusters files - test on vs_10k files
        create_cluster_tax(ident)

        #: create flag and repr cluster files
        repr_and_flag(ident)

    #: running the manual review and further clusterging command
    #: make into separate method TODO
    if args.opt_review:

        #: manual review of flag file and creation of corrected repr file
        flag_correction(ident)

        #: loop down from 100 to 95, clustering using the centroid files
        v_loop = [str(i) for i in range(100, 95-1, -1)]
        for id in v_loop:
            cmd = ''
            if int(id) > 95:
                out_id = str(int(id)-1)
                log_msg = "Running VSEARCH at id: {}".format(out_id)
                logging(log_msg)

            else:
                log_msg = "Finalizing output"
                logging(log_msg)

            start_time = time.time()

            cluster_loop(id)

            elapsed_time = time.time() - start_time
            time_msg = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            log_msg = "{}\n{}\n\n".format(time_log_msg, time_msg)
            logging(log_msg)

    #: running the make database command
    #: make into separate method TODO
    if args.opt_makedb:
        pass
