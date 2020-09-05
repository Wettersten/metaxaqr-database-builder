from .handling import return_proj_path
import os


def create_cluster_tax(ident):
    """Create a tax_clusters file, this contains the label for each cluster
    followed by the label + taxonomy of all hits in the cluster.
    """
    uc_file = "/uc"
    tax_clusters = "/tax_clusters"
    cluster_dir = "/clusters"
    run_path = return_proj_path() + ident

    with open(run_path + tax_clusters, 'w') as clust_out:
        with open(run_path + uc_file, 'r') as read_uc:
            for line in read_uc:
                curr_line = line.rstrip().split("\t")

                if curr_line[0] == "C" and int(curr_line[2]) > 1:
                    curr_cluster = curr_line[1]
                    cluster_file = "/cluster_" + curr_cluster

                    with open("{}{}{}".format(
                                                run_path,
                                                cluster_dir,
                                                cluster_file
                                                ), 'r') as read_cluster:
                        clust_out.write("MQR_{}_{}\n".format(
                                                             ident,
                                                             curr_cluster
                                                             ))
                        for lines in read_cluster:
                            if lines[0] == ">":
                                curr_id = lines.rstrip()
                                clust_out.write("{}\n".format(curr_id))

            clust_out.write("end")  # used by cluster_stats to denote eof


def mark_flag(cluster_label):
    """Used to flag a cluster label when the taxonomy within is weird and needs
    manual attention.
    """
    pass


def remove_cf(tax_file):
    """Removes all occurences of "cf. " within tax_clusters files as these only
    serve to complicate the taxonomy.
    """
    pass
