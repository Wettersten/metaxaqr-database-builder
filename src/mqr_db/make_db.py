"""Creates the final output files used by MetaxaQR as a new database
"""

import os
from pathlib import Path
import shutil
from .handling import return_proj_path, check_file, return_label


def get_deleted_clusters(path):
    excluded_clusters = []
    bad_hits = Path("{}removed/bad_hits".format(path))
    del_clusters = Path("{}removed/deleted_clusters_100".format(path))
    excluded_clusters = []

    if check_file(bad_hits):
        with open(bad_hits, 'r') as f:
            for label in f:
                if label.rstrip() not in excluded_clusters:
                    excluded_clusters.append(label.rstrip())

    if check_file(del_clusters):
        with open(del_clusters, 'r') as f:
            for label in f:
                if label.rstrip() not in excluded_clusters:
                    excluded_clusters.append(label.rstrip())

    return excluded_clusters


def get_centroids(path, result_path, qc, run_label):
    """Copies the 'final_centroids' file from mqr_db/100/ to db result path
    """
    my_cent = Path("{}100/final_centroids".format(path))
    to_cent = Path("{}/{}_final_centroids".format(result_path, run_label))

    if qc:
        excluded_clusters = get_deleted_clusters(path)

        first_line = True
        header = ''
        sequence = ''
        with open(my_cent, 'r') as rf, \
             open(to_cent, 'w') as of:

            for line in rf:
                curr_line = line.rstrip()

                if curr_line[0] == '>':
                    if not first_line and cluster not in excluded_clusters:
                        of.write("{}\n{}\n".format(header, sequence))

                    header = curr_line
                    sequence = ''
                    first_line = False
                    cluster = header.split("\t")[1]

                else:
                    sequence += curr_line + '\n'

    else:
        shutil.copy(my_cent, to_cent)


def get_label_tree(path, result_path, v_loop, qc, run_label):
    """Takes the label tree created at 50% seqence identity and converts it
    into a dictionary format where the mqr_100 (100% seq id) label is key and
    the values are all the labels of the lower sequence identities, in
    descending order.
    """
    excluded_clusters = []
    if qc:
        excluded_clusters = get_deleted_clusters(path)
    label_file = "{}50/label_tree".format(path)
    final_label = "{}/{}_final_label_tree".format(result_path, run_label)

    dl = {}
    for v in v_loop:
        dl["curr_{}".format(v)] = ""

    with open(final_label, 'w') as wf, \
         open(label_file, 'r') as rf:

        for line in rf:
            curr_line = line.rstrip()
            dl["curr_50"] = curr_line.split("\t")[0]
            label_out = ""

            for label in curr_line.split("\t")[1].split(" "):
                id = label.split("_")[-2]
                dl["curr_{}".format(id)] = label

                if int(id) == 100:
                    for key in dl:
                        if key == "curr_100":
                            label_out = "{}\t".format(dl["curr_100"])
                        else:
                            label_out += "{} ".format(dl[key])
                    if qc:
                        if label_out.split("\t")[0] not in excluded_clusters:
                            wf.write("{}\n".format(label_out[:-1]))
                    else:
                        wf.write("{}\n".format(label_out[:-1]))


def get_repr(path, result_path, v_loop, run_label):
    """Creates a final_repr file which contains all lines from all final_repr
    files in the runs from 50-100% sequence identity. Every line is the label,
    entry id, and representative taxonomy, seperated by tabs.
    """
    final_repr = "{}/{}_final_repr".format(result_path, run_label)

    with open(final_repr, 'w') as f:
        for id in v_loop:
            curr_repr = "{}{}/final_repr".format(path, id)
            with open(curr_repr, 'r') as tmp:
                curr = tmp.readlines()
                for line in curr:
                    if line:
                        f.write(line)


def find_bad_hits(cutoff_point=5, str_id='70', depth=False):
    """Looks at the tree_label file output in (str_id)% sequence identity run,
    if any entries at this point are matched with fewer than (cuttoff_point)
    other entries these are all added to /removed/bad_hits to be filtered out
    in creation of the databas. Entries not finding more than 5 matches at 70%
    sequence identity in a large database are fairly dubious.
    """
    run_path = return_proj_path() + str_id
    removed_path = return_proj_path() + 'removed'
    label_file = "{}/label_tree".format(run_path)
    bad_hits = "{}/bad_hits".format(removed_path)
    hit_label = "_100_"

    with open(label_file, 'r') as tree, \
         open(bad_hits, 'w') as out:

        for label in tree:
            labels = label.rstrip().split("\t")[1].split(" ")
            hits = [v for v in labels if hit_label in v]

            if len(hits) < cutoff_point:

                #: looks at total entries contained in all _100_x clusters
                if depth:
                    orig_count = 0

                    for hit in hits:
                        ind = hit.split("_")[-1]
                        cluster_file = "{}100/clusters/cluster_{}".format(
                            run_path,
                            ind
                        )
                        with open(cluster_file, 'r') as f:
                            orig_count += f.read().count(">")

                    if orig_count < cutoff_point:
                        for hit in hits:
                            out.write("{}\n".format(hit))

                else:
                    for hit in hits:
                        out.write("{}\n".format(hit))


def make_db(qc=True):
    """Creates the output datasets used by MetaxaQR. A centroid file which
    contains all entries clustered at 100% sequence identity, a representative
    taxonomy file containing all representative taxonomies at all sequence
    identity levels and finally a file containing the tree structure of all
    labels at all sequence identity levels.
    """
    run_label = return_label()
    path = return_proj_path()
    result_path = "{}results".format(path)
    Path(result_path).mkdir(parents=True, exist_ok=True)
    a_loop = [str(i) for i in range(100, 90-1, -1)]
    b_loop = [str(a) for a in range(85, 50-5, -5)]
    v_loop = a_loop + b_loop

    if qc:
        find_bad_hits()
    get_centroids(path, result_path, qc, run_label)
    get_label_tree(path, result_path, v_loop, qc, run_label)
    get_repr(path, result_path, v_loop, run_label)
