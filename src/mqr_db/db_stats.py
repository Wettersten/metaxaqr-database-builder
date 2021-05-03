"""Methods related to evaluating database quality - deprecated
"""

import os
import subprocess
import argparse


def db_dupestats(dbfile):
    """Looks at a database file and report total entries, number of entries
    with no distinct species, number of entries with distinct species, and
    number of those with species that are duplicates (more than one taxonomy
    for same species/genus).
    """
    tmp_file = "tmp_db"
    cmd_grep = "grep \">\" {}".format(dbfile)
    cmd_cut = "cut -d ' ' -f 2-"
    cmd_sort = "sort"
    cmd = "{grp} | {cut} | {srt} > {tmp}".format(
        grp=cmd_grep,
        cut=cmd_cut,
        srt=cmd_sort,
        tmp=tmp_file
    )
    subprocess.run(cmd, shell=True)

    verbose = False
    out_file = "db_stats.txt"
    count_nospecies = 0
    tax_dict = {}
    total_count = 0
    duplicate_count = 0

    with open(tmp_file, 'r') as f:
        for line in f:
            curr_line = line.rstrip().split(";")
            tax = ";".join(curr_line[:-1])
            genus = curr_line[-1].split(" ")[0]

            if genus[0].islower():
                count_nospecies += 1
            else:
                if genus not in tax_dict:
                    tax_dict[genus] = {tax: 1}
                else:
                    if tax in tax_dict[genus]:
                        tax_dict[genus][tax] += 1
                    else:
                        tax_dict[genus][tax] = 1

    os.remove(tmp_file)
    with open(out_file, 'w') as out:
        if verbose:
            out.write("Genus\tTaxonomy1: Occurence, ...\n")

        for item in tax_dict:
            if len(tax_dict[item]) == 1:
                curr_count = sum(tax_dict[item].values())
                total_count += curr_count

            else:
                if verbose:
                    curr_out = ''
                    for i in tax_dict[item]:
                        curr_out += "{}: {}, ".format(i, tax_dict[item][i])
                    out.write("{}\t{}\n".format(item, curr_out[:-2]))
                curr_count = max(tax_dict[item].values())
                dupes = sum(tax_dict[item].values()) - curr_count
                total_count += sum(tax_dict[item].values())
                duplicate_count += dupes

        if verbose:
            print("\n")

        out.write("Total Entries\tNo Genus\tTotal Genus\tTotal Duplicates\n")
        out.write("{ent}\t{ns}\t{ts}\t{td}".format(
            ent=total_count+count_nospecies,
            ns=count_nospecies,
            ts=total_count,
            td=duplicate_count
        ))
