import os
from pathlib import Path
import random
from .handling import check_dir, check_file, return_proj_path, get_v_loop
from .handling import cleanup
from .cluster_tax import create_taxdb, create_cluster_tax, repr_and_flag
from .cluster_tax import flag_correction
from .clustering import cluster_vs
from .cluster_loop import cluster_loop
from .make_db import make_db
from .make_hmms import make_hmms


def cross_validation(run_label, eval_prop=0.1):
    """
    """
    tmp_label = f"cv_{run_label}"
    #: get centroid file
    centroid_file = ""
    path = Path(return_proj_path(run_label)).parent
    if check_dir(path):
        centroid_file = f"{path}/mqr.fasta"
        if not check_file(centroid_file):
            error_msg = "ERROR: Missing centroid file from specified database"
            quit(error_msg)
    else:
        error_msg = """ERROR: Missing database directory for specified label"""
        quit(error_msg)

    cv_path = f"{path}/cross_validation"
    data_path = f"{cv_path}/data"

    #: split into training, test sets
    training_set, test_set = split_fasta(centroid_file, eval_prop, data_path)

    #: make new temp database from training set
    str_id = '100'
    float_id = 1.0
    tmp_dir = f"{os.getcwd()}/tmp"
    removed_path = f"{tmp_dir}/removed/"
    init_path = f"{tmp_dir}/init/"
    proj_path = return_proj_path(tmp_label)
    Path(removed_path).mkdir(parents=True, exist_ok=True)
    Path(init_path).mkdir(parents=True, exist_ok=True)
    Path(proj_path).mkdir(parents=True, exist_ok=True)

    # TODO - fix QC options
    qc_taxonomy_quality = False
    qc_sequence_quality = False
    gene_marker = ""

    cluster_vs(training_set, float_id, tmp_label)
    create_taxdb(tmp_label)
    create_cluster_tax(
                       str_id,
                       tmp_label,
                       qc_taxonomy_quality,
                       qc_sequence_quality,
                       gene_marker=gene_marker
                       )
    repr_and_flag(str_id, tmp_label)
    exclude_all = True
    path = return_proj_path(run_label)
    qc_limited_clusters = False
    flag_correction(str_id, tmp_label, exclude_all)
    v_loop = get_v_loop()

    for id in v_loop:
        cluster_loop(
                     id,
                     tmp_label,
                     qc_sequence_quality,
                     gene_marker
                    )

    make_db(tmp_label, qc_limited_clusters, qc_taxonomy_quality)
    cleanup("md", False, tmp_label)
    tree_file = f"{Path(return_proj_path(tmp_label)).parent}/mqr.tree"
    mode = "divergent"  # TODO give options for mode selection
    make_hmms(
             mode,
             tree_file,
             tmp_label
             )

    cleanup("mh", False, run_label)
    print("done CV")

    #: doing the 'make' run

    #: run metaxaQR test set vs training set database

    #: evaluiate results from run

    #: post results


def split_fasta(fasta_file, eval_prop, out_path):
    """Splits the mqr.fasta, finished database fasta file, into a training set
    and a test set used for cross validation.
    """
    fasta_dict = read_fasta(fasta_file)
    test_keys = get_test_keys(fasta_dict, eval_prop)

    training_file = f"{out_path}/training.fasta"
    test_file = f"{out_path}/test.fasta"

    with open(training_file, 'w') as train, \
         open(test_file, 'w') as test:

        for key in fasta_dict:
            id = key.split("\t")[0]
            tax = key.split("\t")[1]
            tmp_seq = fasta_dict[key]
            seq = "\n".join([tmp_seq[i:i+80] for i in range(0, len(tmp_seq), 80)])
            if key in test_keys:
                test.write(f"{id} {tax}\n{seq}\n")
            else:
                train.write(f"{id} {tax}\n{seq}\n")

    return training_file, test_file


def get_test_keys(fasta_dict, prop):
    """Uses a FASTA dictionary of keys (acc_id+taxonomy) and sequences to
    create a list of keys used for training, at random, equal to a proportion
    of the total number of keys.
    """
    nr_rand = int(prop * len(fasta_dict))
    test_keys = []

    while len(test_keys) < nr_rand:
        new_key = random.choice(list(fasta_dict))
        if new_key not in test_keys:
            test_keys.append(new_key)

    return test_keys


def read_fasta(fasta_file):
    """Reads a fasta file and stores it as a dictionary.
    """
    fasta_dict = {}
    seq = ""
    id = ""

    with open(fasta_file, 'r') as f:
        for line in f:
            curr_line = line.rstrip()
            if curr_line[0] == ">":
                if seq:
                    fasta_dict[id] = seq

                acc_id = curr_line.split("\t")[0]
                tax = curr_line.split("\t")[-1]
                id = f"{acc_id}\t{tax}"
                seq = ""
            else:
                seq += curr_line

        fasta_dict[id] = seq

    return fasta_dict
