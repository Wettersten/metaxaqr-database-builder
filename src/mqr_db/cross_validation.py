import os
from pathlib import Path
import random
import argparse
from .handling import check_dir, check_file, return_proj_path
from .mqrdb_run import main_mqrdb


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
    #: doing the 'prepare' run
    parser_p = argparse.ArgumentParser()
    args_p = parser.parse_args()
    args_p.opt_prepare = training_set
    args_p.opt_label = tmp_label
    # TODO - add options for QC
    main_mqrdb(args_p)

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
