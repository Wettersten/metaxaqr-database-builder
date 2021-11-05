"""Make HMM module, makes hidden markov models from a MetaxaQR database.
"""
import os  # todo can remove later
import subprocess
from pathlib import Path
from collections import Counter
from .handling import return_proj_path, return_label


def make_hmms(
    mode,
    seq_id="50",
    label_file="",
    seq_db="",
    cpu="4",
    conservation_cutoff=0.6,
    look_ahead=4,
    min_length=20,
    max_gaps=5
):
    """Creates HMMs from MetaxaQR database or a provided sequence database, 3
    modes - divergent, hybrid and conserved. Uses MAFFT to align the sequences
    then HMMER to make the HMMs.
    """
    create_align_structure()
    run_label = return_label()
    hmm_dir = f"{run_label}_results/HMMs/"
    cluster_dir = f"{return_proj_path()}100/clusters/"
    align_dir = f"{return_proj_path()}alignment/"

    #: divergent mode
    if mode.lower() == "divergent":
        tmp_ids = []

        #: get all clusters
        tmp_ids = make_cluster_seq_file(
            seq_id,
            label_file,
            cluster_dir,
            align_dir
            )

        cluster_ids = format_cluster_ids(tmp_ids)

        for id in cluster_ids:
            format_id = cluster_ids[id]
            file = f"{align_dir}cluster_{id}"

            #: align the sequences
            a_file = run_mafft(file, cpu)

            #: split the alignment in two
            head, tail = split_alignment(a_file)
            split_files = {"01": head, "02": tail}

            #: make the HMM files
            hmm_files = []
            for split_id in split_files:
                h_file = run_hmmer_build(
                    split_files[split_id],
                    format_id,
                    split_id,
                    align_dir,
                    cpu
                    )
                hmm_files.append(h_file)

            run_hmmer_press(hmm_files, format_id, hmm_dir)

    #: hybrid mode
    elif mode.lower() == "hybrid":
        tmp_ids = []

        tmp_ids = make_cluster_seq_file(
            seq_id,
            label_file,
            cluster_dir,
            align_dir
            )

        cluster_ids = format_cluster_ids(tmp_ids)

        for id in cluster_ids:
            format_id = cluster_ids[id]
            file = f"{align_dir}cluster_{id}"

            #: aligns the file
            a_file = run_mafft(file, cpu)

            #: trims the aligned file
            t_file = trim_alignment(a_file)

            #: aligns the trimmed file
            a_file = run_mafft(t_file, cpu)

            #: gets all conserved regions
            conserved_regions = get_conserved_regions(
                a_file,
                conservation_cutoff,
                look_ahead,
                min_length,
                max_gaps
            )

            hmm_files = []
            for conserved_id in conserved_regions:
                #: alignes the conserved region
                a_file = run_mafft(conserved_regions[conserved_id], cpu)

                #: makes hmm file from the conserved region
                h_file = run_hmmer_build(
                    a_file,
                    format_id,
                    conserved_id,
                    align_dir,
                    cpu
                    )
                hmm_files.append(h_file)

            #: builds full hmm files from the hmmbuilder files
            run_hmmer_press(hmm_files, format_id, hmm_dir)

    #: conserved mode
    elif mode.lower() == "conserved":
        format_id = "A"

        #: aligns the file
        a_file = run_mafft(seq_db, cpu, align_dir=align_dir)

        #: trims the aligned file
        t_file = trim_alignment(a_file)

        #: aligns the trimmed file
        a_file = run_mafft(t_file, cpu)

        #: gets all conserved regions
        conserved_regions = get_conserved_regions(
            a_file,
            conservation_cutoff,
            look_ahead,
            min_length,
            max_gaps
        )

        hmm_files = []
        for conserved_id in conserved_regions:
            #: alignes the conserved region
            a_file = run_mafft(conserved_regions[conserved_id], cpu)

            #: makes hmm file from the conserved region
            h_file = run_hmmer_build(
                a_file,
                format_id,
                conserved_id,
                align_dir,
                cpu
                )
            hmm_files.append(h_file)

        #: builds full hmm files from the hmmbuilder files
        run_hmmer_press(hmm_files, format_id, hmm_dir)


def run_hmmer_build(file, cluster_id, hmm_id, align_dir, cpu):
    """Runs the hmmbuild command, building the separate HMMs.
    """
    hmm_name = f"{cluster_id}{hmm_id}"
    hmm_file = f"{align_dir}{hmm_name}.hmm"

    cmd_hmmbuild = f"hmmbuild -n {hmm_name} --dna --informat afa --cpu {cpu}".split(" ")
    cmd_hmmbuild.append(hmm_file)
    cmd_hmmbuild.append(file)

    subprocess.run(cmd_hmmbuild)

    return hmm_file


def run_hmmer_press(files, cluster_id, hmm_dir):
    """Runs the hmmpress command, pressing all HMMs into a single database.
    """
    combined_file = hmm_combine(files, cluster_id, hmm_dir)
    cmd_hmmpress = "hmmpress".split(" ")
    cmd_hmmpress.append(combined_file)
    subprocess.run(cmd_hmmpress)


def hmm_combine(files, cluster_id, hmm_dir):
    """Makes one file containing all text from all separate HMM files.
    """
    combined_file = ""
    cmd_combine = "cat".split(" ")
    full_hmm = f"{hmm_dir}{cluster_id}.hmm"
    for file in files:
        cmd_combine.append(file)
    with open(full_hmm, 'w') as f:
        subprocess.run(cmd_combine, stdout=f)

    return full_hmm


def run_mafft(file, cpu, align_dir=""):
    """Runs mafft, creating multiple sequence alignment from input sequences
    """
    #: use mafft to align input file
    err_file = f"{file}.error"
    out_file = f"{file}.aligned"

    if align_dir:
        filename = Path(file).name
        tmp_file = f"{align_dir}{filename}"
        err_file = f"{tmp_file}.error"
        out_file = f"{tmp_file}.aligned"

    cmd_mafft = f"mafft --auto --reorder --quiet --thread {cpu}".split(" ")
    cmd_mafft.append(file)

    with open(out_file, 'w') as stout, \
         open(err_file, 'a+') as sterr:
        subprocess.run(cmd_mafft, stdout=stout, stderr=sterr)

    return out_file


def split_alignment(align_file):
    """Splits a mutliple sequence alignment in middle according to the middle
    of the top-most sequence in the alignment
    """
    #: loop over aligned file, split each alignment in two
    align_head = f"{align_file}.head"
    align_tail = f"{align_file}.tail"

    with open(align_file, 'r') as f, \
         open(align_head, 'w') as f_head, \
         open(align_tail, 'w') as f_tail:
        seq = ""
        acc_id = ""
        seq_len = 0

        for line in f:
            curr_line = line.rstrip()

            if curr_line[0] == ">":
                if seq:
                    head_seq, tail_seq = split_seq(seq)
                    f_head.write(f"{acc_id}\n{head_seq}\n")
                    f_tail.write(f"{acc_id}\n{tail_seq}\n")

                acc_id = curr_line
                seq = ""
            else:
                seq += curr_line

        head_seq, tail_seq = split_seq(seq)
        f_head.write(f"{acc_id}\n{head_seq}\n")
        f_tail.write(f"{acc_id}\n{tail_seq}\n")

    return align_head, align_tail


def format_cluster_ids(cluster_ids):
    """Used to rename the HMM files in alphabetical order
    """
    alph = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U" "V", "W", "X", "Y", "Z"]
    formatted_ids = {}
    for i in range(len(cluster_ids)):
        formatted_ids[cluster_ids[i]] = alph[i]

    return formatted_ids


def make_cluster_seq_file(seq_id, label_file, cluster_dir, align_dir):
    """Creates the cluster file, containing all sequences from all 100 sequence
    identity clusters
    """
    #: makes dict with 100 cluster files belonging to each seq_id cluster
    #: dict with each id being one 50 id, containing all 100 ids
    id_clusters = {}
    curr_cluster = ""
    seq_id_pos = -1
    if seq_id != "50":
        if int(seq_id) >= 90:
            seq_id_pos = -9 - (int(seq_id)-90)
        elif int(seq_id) > 50:
            seq_id_pos = -1 - round((int(seq_id)-50)/5)

    with open(label_file, 'r') as r:
        for line in r:
            curr_line = line.rstrip().split("\t")
            curr_cluster = curr_line[1].split(" ")[seq_id_pos].split("_")[-1]
            curr_100_cluster = curr_line[0].split("_")[-1]

            if curr_cluster in id_clusters:
                id_clusters[curr_cluster] += f" cluster_{curr_100_cluster}"
            else:
                id_clusters[curr_cluster] = curr_100_cluster

    #: makes the sequence file from a cluster
    #: uses id_cluster to loop, writing one file per 50 cluster
    #: containing all 100 seqs
    for id in id_clusters:
        singleton = False
        out_cluster_file = f"{align_dir}cluster_{id}"
        with open(out_cluster_file, 'w') as h_f:
            if len(id_clusters[id].split(" ")[1:]) == 1:
                singleton = True
            for cluster_100_id in id_clusters[id].split(" ")[1:]:
                cluster_file = f"{cluster_dir}{cluster_100_id}"
                with open(cluster_file, 'r') as c_f:
                    curr_seq = ""
                    acc_id = ""
                    for cluster_line in c_f:
                        if cluster_line[0] == ">":
                            if curr_seq:
                                h_f.write(f"{acc_id}\n{curr_seq}\n")
                            acc_id = cluster_line.split(" ")[0]
                            curr_seq = ""
                        else:
                            curr_seq += cluster_line.rstrip()
                    h_f.write(f"{acc_id}\n{curr_seq}\n")

                    #: MAFFT single sequence alignment protection
                    #: duplicates sequences in clusters with only 1 sequence
                    if singleton:
                        h_f.write(f"{acc_id}_dupl\n{curr_seq}\n")

    out_ids = []
    for id in id_clusters:
        out_ids.append(id)
    return out_ids


def create_align_structure():
    """Creates the output directories
    """
    #: makes return_proj_path/hmm/ & alignment
    align_dir = f"{return_proj_path()}alignment/"
    run_label = return_label()
    hmm_dir = f"{run_label}_results/HMMs/"
    Path(align_dir).mkdir(parents=True, exist_ok=True)
    Path(hmm_dir).mkdir(parents=True, exist_ok=True)


def split_seq(sequence):
    """Cuts a sequence in half, producing head and tail sequences
    """
    cut_seq = round(len(sequence)/2)
    head_seq = ""
    tail_seq = ""

    #: making the head sequence
    tmp_seq = sequence[:cut_seq]
    head_seq = "\n".join([tmp_seq[i:i+60] for i in range(
        0, len(tmp_seq), 60)])

    #: making the tail sequence
    tmp_seq = sequence[cut_seq:]
    tail_seq = "\n".join([tmp_seq[i:i+60] for i in range(
        0, len(tmp_seq), 60)])

    return head_seq, tail_seq


def trim_alignment(file):
    """Trims a mutliple sequence alignment, removing all position to the left,
    and the right, of the top-most sequence in the alignment
    """
    file_out = f"{file}.trimmed"
    start = 0
    end = 0
    align_dict = {}
    first = True
    first_seq = ""

    with open(file, 'r') as f, \
         open(file_out, 'w') as f_out:
        seq = ""
        acc_id = ""
        for line in f:
            curr_line = line.rstrip()
            if curr_line[0] == ">":
                if seq:
                    if first:
                        start, end = get_start_end_indices(seq)
                        first = False

                    tmp_seq = seq[start:end+1]
                    trim_seq = "\n".join([tmp_seq[i:i+60] for i in range(
                        0, len(tmp_seq), 60)])
                    f_out.write(f"{acc_id}\n{trim_seq}\n")

                acc_id = curr_line
                seq = ""

            else:
                seq += curr_line

        tmp_seq = seq[start:end+1]
        trim_seq = "\n".join([tmp_seq[i:i+60] for i in range(
            0, len(tmp_seq), 60)])
        f_out.write(f"{acc_id}\n{trim_seq}\n")

    return file_out


def get_start_end_indices(sequence):
    """Gets the start and end positions from a sequence in order to trim
    around it
    """
    start = 0
    end = 0
    #: gets start point to trim alignment
    for i in range(len(sequence)):
        if sequence[i] != "-":
            start = i
            break

    #: gets end point to trim alignment
    for i in range(len(sequence)-1, 0, -1):
        if sequence[i] != "-":
            end = i
            break

    return start, end


def get_conserved_regions(
    file,
    conservation_cutoff=0.6,
    look_ahead=4,
    min_length=20,
    max_gaps=5
):
    """Takes a multiple sequence alignment and produces files containing all
    conserved regions found
    """
    #: makes the dictionary containing all entries from the cluster
    cluster_dict = {}
    with open(file, 'r') as f:
        acc_id = ""
        sequence = ""
        for line in f:
            curr_line = line.rstrip()
            if curr_line[0] == ">":
                if sequence:
                    cluster_dict[acc_id] = sequence
                acc_id = curr_line
                sequence = ""
            else:
                sequence += curr_line.lower()
        cluster_dict[acc_id] = sequence

    #: makes the most conserved sequence
    conservation_sequence = ""
    sequence_length = len(cluster_dict[list(cluster_dict)[0]])
    total_ids = len(list(cluster_dict))
    for i in range(sequence_length):
        curr_pos_content = []
        for id in cluster_dict:
            curr_pos_content.append(cluster_dict[id][i])
        c = Counter(curr_pos_content)
        common_base = c.most_common(1)[0][0]
        cons_base = c.most_common(1)[0][1]
        if cons_base/total_ids >= conservation_cutoff:
            conservation_sequence += common_base
        else:
            conservation_sequence += "x"

    #: gets conserved regions from the conservation sequence
    conserved_regions = calc_conserved_regions(
        conservation_sequence,
        look_ahead=look_ahead,
        min_length=min_length,
        max_gaps=max_gaps
    )

    #: uses regions to get the alignment for each region
    cr_files = {}
    for i in range(len(conserved_regions)):
        id = i + 1
        if id < 10:
            id = str(f"0{id}")
        else:
            id = str(id)
        cr_file = f"{file}.{id}"
        cr_files[id] = cr_file
        start, end = conserved_regions[i]

        with open(cr_file, 'w') as cr_out:
            for acc_id in cluster_dict:
                tmp_seq = cluster_dict[acc_id][start:end+1]
                seq = "\n".join([tmp_seq[i:i+60] for i in range(
                    0, len(tmp_seq), 60)])
                cr_out.write(f"{acc_id}\n{seq}\n")

    return cr_files


def calc_conserved_regions(sequence,
                           look_ahead,
                           min_length,
                           max_gaps
                           ):
    """Calculates the conserved regions from a conserved sequence, these are
    scored and the top scoring regions that do not overlap are returned
    """
    conserved_regions = []
    hits = {}

    #: makes segments from each position to the end to test for regions
    for i in range(len(sequence)-min_length+1):
        curr_seq = sequence[i:]
        start = i
        end = 0
        curr_len = 0
        local_gaps = 0
        curr_gap = 0
        score_cutoff = 10
        score = 0
        last_gap = 0
        #: only starts if start on conserved position
        if curr_seq[0] != "x":
            #: checking every position in segment
            for j in range(len(curr_seq)):
                nt = curr_seq[j]
                if nt == "x":
                    curr_gap += 1
                    score -= curr_gap * local_gaps
                else:
                    score += 1
                    if curr_gap > 0:
                        local_gaps += 1
                        last_gap = curr_gap
                        curr_gap = 0
                curr_len += 1

                #: breaks if more unconserved pos than look_ahead
                if curr_gap > look_ahead:
                    end = start + j - (look_ahead + 1)
                    break

                #: breaks if more gaps than max_gaps
                if local_gaps > max_gaps:
                    end = start + j - (last_gap + 1)
                    break

            if end == 0:
                end = start + (len(curr_seq)-1)

            if curr_len >= min_length and score >= score_cutoff:
                hits[(start, end)] = score

    #: get top scoring, non-intersecting, conserved regions
    conserved_regions = remove_overlaps(hits)

    return conserved_regions


def remove_overlaps(conserved_dictionary):
    """ Takes a dictionary of tuples with start/end positions and their
    conservation scores, sorting by score and adding the highest scoring
    regions that do not overlap. Returning all conserved regions found not
    overlapping maximizing total conservation score.
    """
    conserved_regions = []
    sorted_hits = dict(sorted(
        conserved_dictionary.items(),
        key=lambda item: item[1],
        reverse=True
        ))

    for hit in sorted_hits:
        if not conserved_regions:
            conserved_regions.append([hit[0], hit[1]])
        else:
            found = False
            for cr in conserved_regions:
                if (
                    hit[0] >= cr[0] and hit[0] <= cr[1]
                    or hit[1] >= cr[0] and hit[1] <= cr[1]
                ):
                    found = True
                    break

            if not found:
                conserved_regions.append([hit[0], hit[1]])

    return sorted(conserved_regions)
