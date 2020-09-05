from .handling import return_proj_path
from collections import Counter
import os


"""Depreciated, might keep some functions at later stages when analysing
taxonomy within clusters to calculate representative taxonomy.
"""

ident_file = "/ident_clusters"
run_dir = return_proj_path()


def calc_avg_ident(ident_list):
    return sum(ident_list) / len(ident_list)


def find_avg_ident(tax_id):
    avg_idents = []
    output_idents = []
    tot_species = []
    run_path = run_dir + tax_id

    with open(run_path + ident_file) as read_file:
        for line in read_file:
            curr_line = (line.rstrip().split("\t")[1])
            curr_list = curr_line[2:len(curr_line)-1].split(", ")
            if len(curr_list) > len(avg_idents):
                for i in range(len(curr_list) - len(avg_idents)):
                    avg_idents.append([])

            for i in range(len(curr_list)):
                avg_idents[i].append(float(curr_list[i]))

            tot_species.append(float(curr_list[-1]))

    for i in range(len(avg_idents)):
        if len(avg_idents[i]):
            output_idents.append(
                                 "{:.4f}".format(calc_avg_ident(avg_idents[i]))
                                 )
    avg_species = ("{:.4f}".format(calc_avg_ident(tot_species)))
    output_text = ""
    for ident in output_idents:
        output_text += "{}, ".format(str(ident))
    return(output_text[:-2], avg_species)


def most_frequent(tax_list):
    count_list = Counter(tax_list)
    return count_list.most_common(1)[0][0]


def count_highest_fraction(tax_list):
    nr_occur = tax_list.count(most_frequent(tax_list))
    return nr_occur / len(tax_list)


def fract_cluster(cluster_list):
    all_tax = [[] for i in range(len(max(cluster_list, key=len)))]
    for tax in cluster_list:
        if len(all_tax) == len(tax):
            for i in range(len(tax)):
                all_tax[i].append(tax[i])
        else:
            for i in range(0, len(tax)-1):
                all_tax[i].append(tax[i])
            for i in range(
                           len(tax)-1, len(all_tax)-1
                           ):
                all_tax[i].append("-")
            all_tax[-1].append(tax[-1])

    return all_tax


def taxonomy_identities(tax_id):
    tax_file = "/tax_clusters"
    run_path = run_dir + tax_id

    with open(run_path + tax_file, 'r') as read_file:
        with open(run_path + ident_file, 'w') as out_file:
            cluster_id = 0
            first_line = True
            tax_fractions = []
            all_tax = []
            curr_cluster = []
            old_cluster = 0

            for line in read_file:
                curr_line = line.rstrip()
                if curr_line.isdigit() or curr_line == "end":
                    old_cluster = cluster_id
                    cluster_id = curr_line

                    if not first_line:
                        all_tax = fract_cluster(curr_cluster)
                        tax_fractions = [[] for i in range(len(all_tax))]
                        for i in range(len(tax_fractions)):
                            tax_fractions[i] = count_highest_fraction(
                                all_tax[i]
                                )

                        out_file.write(
                            "{} \t {}\n".format(old_cluster, tax_fractions)
                            )

                    first_line = False
                    curr_cluster = []

                else:
                    curr_cluster.append(
                                        " ".join(curr_line.split(" ")[1:]
                                                 ).split(";"))


def calc_stats(identities, proj):
    """
    """
    with open('stats_clusters.txt', 'w') as file_out:
        for id in identities:
            taxonomy_identities(str(id))
            avg_out, avg_species = find_avg_ident(str(id))

            file_out.write("Cluster id: {}\n".format(str(id)))
            file_out.write("{}\n".format(avg_out))
            file_out.write("{}\n".format(avg_species))
