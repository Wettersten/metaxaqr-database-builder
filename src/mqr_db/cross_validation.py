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
    cv_label = f"cv_{run_label}"
    tax_dict = {}
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
    Path(data_path).mkdir(parents=True, exist_ok=True)

    #: split into training, test sets
    training_set, test_set = split_fasta(centroid_file, eval_prop, data_path)

    #: make new temp database from training set
    str_id = '100'
    float_id = 1.0
    tmp_dir = f"{os.getcwd()}/tmp"
    removed_path = f"{tmp_dir}/removed/"
    init_path = f"{tmp_dir}/init/"
    proj_path = return_proj_path(cv_label)
    Path(removed_path).mkdir(parents=True, exist_ok=True)
    Path(init_path).mkdir(parents=True, exist_ok=True)
    Path(proj_path).mkdir(parents=True, exist_ok=True)

    # TODO - fix QC options
    qc_taxonomy_quality = False
    qc_sequence_quality = False
    gene_marker = ""

    cluster_vs(training_set, float_id, cv_label)
    create_taxdb(cv_label)
    create_cluster_tax(
                       str_id,
                       cv_label,
                       qc_taxonomy_quality,
                       qc_sequence_quality,
                       gene_marker=gene_marker
                       )
    repr_and_flag(str_id, cv_label)
    exclude_all = True
    qc_limited_clusters = False
    flag_correction(str_id, cv_label, exclude_all)
    v_loop = get_v_loop()

    for id in v_loop:
        cluster_loop(
                     id,
                     cv_label,
                     qc_sequence_quality,
                     gene_marker
                    )

    make_db(cv_label, qc_limited_clusters, qc_taxonomy_quality)
    cleanup("md", False, cv_label)
    tree_file = f"{Path(return_proj_path(cv_label)).parent}/mqr.tree"
    mode = "divergent"  # TODO give options for mode selection
    make_hmms(
             mode,
             tree_file,
             cv_label
             )

    cleanup("mh", False, cv_label)

    #: creating the training taxonomy cheat sheet, and reading into dict
    train_centroids = f"{Path(return_proj_path(cv_label)).parent}/mqr.fasta"
    training_tax_file = make_train_tax(train_centroids, data_path)

    tax_dict = get_tax_dict(training_tax_file)

    #: contains test_full, test_half and test_read
    #: test set in differing read lengths
    test_files = cut_test_set(test_set, data_path)
    test_results = {}

    #: run metaxaQR on each test file
    for test_file in test_files:
        test_run = test_file.split("/")[-1].split(".")[0].split("_")[-1]
        mqr_results = run_mqr(
            test_file,
            run_label,
            cv_label,
            data_path,
            test_run
            cpu=10  # todo - make not hardcoded
            )
        test_results[test_run] = evaluation(mqr_results, tax_dict)

    print("Cross validation results\n")  # todo - make writeout instead
    for result in test_results:
        correct = sum(test_results[result][:-1]) / sum(test_results[result])
        corr_perc = "{:.2%}".format(correct)
        print(f"{result}: {corr_perc}")  # todo - make writeout instead


def split_fasta(fasta_file, eval_prop, out_path):
    """Splits the mqr.fasta, finished database fasta file, into a training set
    and a test set used for cross validation.
    """
    fasta_dict = read_fasta(fasta_file)
    test_keys = get_test_keys(fasta_dict, eval_prop)

    training_file = f"{out_path}/training.fasta"
    test_file = f"{out_path}/test_full.fasta"

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


def make_train_tax(centroid_file, out_dir):
    """
    """
    taxes = {}
    tax_file = f"{out_dir}/train_tax.txt"
    with open(centroid_file, 'r') as c, \
         open(tax_file, 'w') as f:

        for line in c:
            if line[0] == ">":
                split_line = line.rstrip().split("\t")
                id = split_line[0]
                tax = split_line[-1]
                f.write(f"{id}\t{tax}\n")

    return tax_file


def cut_test_set(test_file, out_dir):
    """
    """
    half_file = f"{out_dir}/test_half.fasta"
    read_file = f"{out_dir}/test_read.fasta"
    half_dict = {}
    read_dict = {}
    seq_len = 1000
    smallest_seq_len = 1000
    output_files = [test_file]

    with open(test_file, 'r') as f_full:
        seq = ""

        for line in f_full:
            if line[0] == ">":
                if seq:
                    seq_len = len(seq)
                    if seq_len < smallest_seq_len:
                        smallest_seq_len = seq_len

                    half_dict[id] = get_half_seq(seq)

                    if len(seq) >= 300:
                        read_dict[id] = get_read_seq(seq)

                id = line.split(" ")[0]
                seq = ""
            else:
                seq += line.rstrip()

        half_dict[id] = get_half_seq(seq)
        if len(seq) >= 300:
            read_dict[id] = get_read_seq(seq)

    with open(half_file, 'w') as f_half:
        for id in half_dict:
            half_tmp = half_dict[id]
            half_out = "\n".join([half_tmp[i:i+80] for i in range(0, len(half_tmp), 80)])
            f_half.write(f"{id}\n{half_out}\n")
    output_files.append(half_file)

    if smallest_seq_len >= 300:
        with open(read_file, 'w') as f_read:
            for id in read_dict:
                read_tmp = read_dict[id]
                read_out = "\n".join([read_tmp[i:i+80] for i in range(0, len(read_tmp), 80)])
                f_read.write(f"{id}\n{read_out}\n")
        output_files.append(read_file)

    return output_files


def get_half_seq(seq):
    """
    """
    half_seq = ""
    half_len = int(len(seq)/2)
    half_max = len(seq) - half_len
    half_start = random.randrange(0, half_max)
    half_seq = seq[half_start:half_start+half_len]

    return half_seq


def get_read_seq(seq):
    """
    """
    read_seq = ""
    read_len = 100
    read_max = len(seq) - read_len
    read_start = random.randrange(0, read_max)
    read_seq = seq[read_start:read_start+read_len]

    return read_seq


def get_tax_dict(file):
    """
    """
    tax_dict = {}
    with open(file, 'r') as f:
        for line in f:
            curr_line = line.rstrip()
            split_line = curr_line.split("\t")
            tax_dict[split_line[0]] = split_line[1]

    return tax_dict


def run_mqr(test_set, run_label, cv_label, output_dir, test_len, cpu=10):
    """
    """
    inp_opt = f"-i {test_set}"
    outfile = f"{output_dir}/{test_len}_{run_label}"
    out_opt = f"-o {outfile}"
    cpu_opt = f"--cpu {cpu}"
    db_opt = f"-g {cv_label}"
    mqr_cmd = f"./metaxaQR {inp_opt} {out_opt} {cpu_opt} {db_opt}".split(" ")

    subprocess.run(mqr_db)

    taxonomy_file = f"{outfile}.taxonomy.txt"
    return taxonomy_file


def evaluation(test_results, tax_dict):
    """
    """
    species_hits = 0
    genus_hits = 0
    partial_hits = 0
    incorrect_hits = 0

    with open(test_results, 'r') as f:
        for line in f:
            curr_line = line.rstrip()

            acc_id = ">{}".format(curr_line.split("\t")[0])
            facit_tax = tax_dict[acc_id].lower()
            facit_split = facit_tax.split(";")
            curr_tax = curr_line.split("\t")[1].lower()

            if curr_tax:  # no empty entries allowed
                if curr_tax[-1] == ";":
                    curr_tax = curr_tax[:-1]
                curr_split = curr_tax.split(";")

                #: make sure that the taxonomy is there
                if len(curr_split) <= 1:
                    incorrect_hits += 1
                    print(curr_line)
                    print(facit_tax, "\n")

                else:
                    curr_sp = " ".join(curr_split[-1].split(" ")[:2]).lower()
                    if len(curr_split[-1].split(" ")) < 2:
                        curr_sp = "no species"
                    facit_sp = " ".join(facit_split[-1].split(" ")[:2]).lower()

                    curr_genus = curr_split[-1].lower()
                    facit_genus = facit_split[-1].split(" ")[0].lower()

                    #: check for species
                    if facit_sp == curr_sp:
                        species_hits += 1

                    #: check for genus
                    elif facit_genus == curr_genus:
                        genus_hits += 1

                    #: check for partial perfect subset
                    elif facit_split[:len(curr_split)] == curr_split:
                        partial_hits += 1

                    #: check for partial perfect subset - order nonspecific
                    elif all(x in facit_split for x in curr_split):
                        partial_hits += 1

                    #: otherwise add to incorrects
                    else:
                        incorrect_hits += 1
                        print(curr_line)
                        print(facit_tax, "\n")
            else:
                incorrect_hits += 1
                print(curr_line)
                print(facit_tax, "\n")

    return [species_hits, genus_hits, partial_hits, incorrect_hits]
