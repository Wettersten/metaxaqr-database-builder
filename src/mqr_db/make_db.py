"""Creates the final output files used by MetaxaQR as a new database
"""

import os
from pathlib import Path
import shutil
from .handling import return_proj_path


def get_centroids(path, result_path):
    """Copies the 'final_centroids' file from mqr_db/100/ to db result path
    """
    my_cent = Path("{}100/final_centroids".format(path))
    to_cent = Path("{}/final_centroids".format(result_path))
    shutil.copy(my_cent, to_cent)


def get_label_tree(path, result_path, v_loop):
    """Takes the label tree created at 50% seqence identity and converts it
    into a dictionary format where the mqr_100 (100% seq id) label is key and
    the values are all the labels of the lower sequence identities, in
    descending order.
    """
    label_file = "{}50/label_tree".format(path)
    final_label = "{}/final_label_tree".format(result_path)

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
                id = label.split("_")[1]
                dl["curr_{}".format(id)] = label

                if int(id) == 100:
                    for key in dl:
                        if key == "curr_100":
                            label_out = "{}\t".format(dl["curr_100"])
                        else:
                            label_out += "{} ".format(dl[key])
                    wf.write("{}\n".format(label_out[:-1]))


def get_repr(path, result_path, v_loop):
    """Creates a final_repr file which contains all lines from all final_repr
    files in the runs from 50-100% sequence identity. Every line is the label,
    entry id, and representative taxonomy, seperated by tabs.
    """
    final_repr = "{}/final_repr".format(result_path)

    with open(final_repr, 'w') as f:
        for id in v_loop:
            curr_repr = "{}{}/final_repr".format(path, id)
            with open(curr_repr, 'r') as tmp:
                curr = tmp.readlines()
                for line in curr:
                    if line:
                        f.write(line)


def make_db():
    """Creates the output datasets used by MetaxaQR. A centroid file which
    contains all entries clustered at 100% sequence identity, a representative
    taxonomy file containing all representative taxonomies at all sequence
    identity levels and finally a file containing the tree structure of all
    labels at all sequence identity levels.
    """
    path = return_proj_path()
    result_path = "{}results".format(path)
    Path(result_path).mkdir(parents=True, exist_ok=True)
    a_loop = [str(i) for i in range(100, 90-1, -1)]
    b_loop = [str(a) for a in range(85, 50-5, -5)]
    v_loop = a_loop + b_loop

    get_centroids(path, result_path)
    get_label_tree(path, result_path, v_loop)
    get_repr(path, result_path, v_loop)
