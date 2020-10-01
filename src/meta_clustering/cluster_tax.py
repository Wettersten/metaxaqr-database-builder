from .handling import return_proj_path, tax_list_to_str
import os
from collections import Counter

#: global list of accepted flags for prompt_accept flags
accepted_flags = []


class Cluster:
    """Cluster class, this contains the cluster label and all entries in the
    cluster. Used between functions to calculate/change representative taxonomy
    or flags etc.
    """
    def __init__(
        self,
        label,
        cluster_entries,
        flags='',
        repr_tax='',
        str_id=''
    ):
        self.label = label
        self.cluster_entries = cluster_entries
        self.flags = flags
        self.repr_tax = repr_tax
        self.str_id = str(label.split("_")[1])

    def add_entry(self, tax):
        self.cluster_entries.append(tax)

    def get_taxeslist(self):
        tcluster = []
        for tax in self.cluster_entries:
            tcluster.append(" ".join(tax.split(" ")[1:]).split(";"))

        return tcluster

    def get_taxesstring(self):
        tcluster = []
        for tax in self.cluster_entries:
            tcluster.append(" ".join(tax.split(" ")[1:]))

        return tcluster

    def get_entries(self):
        return self.cluster_entries

    def change_flags(self, flags):
        self.flags = flags

    def get_flags(self):
        return self.flags

    def change_label(self, label):
        self.label = label

    def get_label(self):
        return self.label

    def change_reprtax(self, repr_tax):
        self.repr_tax = repr_tax

    def get_reprtax(self):
        return self.repr_tax

    def get_strid(self):
        return self.str_id


def create_cluster_tax(str_id, loop=False):
    """Create a tax_clusters file, this contains the label for each cluster
    followed by the label + taxonomy of all hits in the cluster.
    """
    run_path = return_proj_path() + str_id
    uc_file = run_path + "/uc"
    tax_clusters_file = run_path + "/tax_clusters"
    cluster_dir = run_path + "/clusters"

    with open(tax_clusters_file, 'w') as clust_out, \
         open(uc_file, 'r') as read_uc:

        for line in read_uc:
            curr_line = line.rstrip().split("\t")

            if curr_line[0] == "C" and int(curr_line[2]) > 1:
                curr_cluster = curr_line[1]
                cluster_file = cluster_dir + "/cluster_" + curr_cluster

                with open(cluster_file, 'r') as read_cluster:
                    new_cluster = curr_cluster
                    if loop:
                        new_cluster = curr_line[9].split("_")[2]
                    clust_out.write("MQR_{}_{}\n".format(
                                                         str_id,
                                                         new_cluster
                                                         ))

                    for lines in read_cluster:
                        if lines[0] == ">":
                            if loop:
                                loop_line = lines.rstrip().split("\t")
                                loop_tlabel = loop_line[0]
                                loop_clabel = "MQR_{}_{}".format(
                                    str_id,
                                    loop_line[1].split("_")[2]
                                )
                                loop_repr = loop_line[2]
                                curr_id = "{} {}".format(
                                    loop_tlabel,
                                    loop_repr
                                )
                            else:
                                curr_id = remove_cf_line(lines.rstrip())
                            clust_out.write("{}\n".format(curr_id))

        clust_out.write("end")


def remove_cf_line(tax_line):
    """Removes all occurences of "cf. " within a line of taxonomy.
    """
    return tax_line.replace('cf. ', '')


def flag_check(cluster):
    """Checks various flag scenarios and returns appropriate flags. Expand to
    further checks TODO
    """
    flag = ''

    chl_flag = chlor_mito_flag(cluster)
    if chl_flag:
        flag += chl_flag + ", "

    return flag[:-2]


def chlor_mito_flag(cluster):
    """Flags if both Chloroplast and Mitochondria are in the same cluster.
    """
    chlor_check = False
    mito_check = False
    flag_out = ''

    for tax in cluster:
        if "Chloroplast" in tax or "Chloroplastida" in tax:
            chlor_check = True
        elif "Mitochondria" in tax:
            mito_check = True
        if chlor_check and mito_check:
            flag_out = "Chlr_Mito"
            break

    return flag_out


def repr_taxonomy(tax_cluster):
    """Calculates the representative taxonomy for a cluster, checking species
    first and the continuing down to lower categories. Returning representative
    taxonomy and any flags.
    """
    repr_tax = 'No Match'  # if no repr_tax is found
    flag = ''
    found = False
    sp_splits = 6

    new_cluster = []
    for tax in tax_cluster:
        if tax[-1][0].isupper():
            new_cluster.append(tax)

    #: loop for species
    if len(new_cluster) > 0:
        for i in range(sp_splits):
            curr_cluster = []
            for tax in new_cluster:
                stripped_tax = tax[:-1]
                sp_tax = " ".join((tax[-1].split(" ")[:(sp_splits-i)]))
                stripped_tax.append(sp_tax)
                curr_cluster.append(stripped_tax)

            found, new_repr_tax, new_flag = calc_repr_taxonomy_species(
                curr_cluster
                )
            if (
                new_repr_tax[-3:] == 'sp.'
                or new_repr_tax[-1:] == '#'
                or 'environmental' in new_repr_tax.split(";")[-1].split(" ")
            ):
                found = False
            if found:
                repr_tax = new_repr_tax
                if new_flag and new_flag not in flag.split(", "):
                    flag += new_flag + ", "
                break

    #: loop for categories below species
    #: starting at lowest category and moving upwards, if more than 4
    #: categories it starts at category nr 4 to speed up the process
    if not found:
        start = 0
        if len(tax_cluster[0]) > 4:
            start = len(tax_cluster[0])-5

        for i in range(start, len(tax_cluster[0])-1):
            curr_cluster = []
            for tax in tax_cluster:
                if tax[:i+1][-1][0].isupper():
                    curr_cluster.append(tax[:i+1])
            if len(curr_cluster) > 0:
                found, new_repr_tax, new_flag = calc_repr_taxonomy_rest(
                    curr_cluster
                )
            if found:
                repr_tax = new_repr_tax
                if new_flag and new_flag not in flag.split(", "):
                    flag += new_flag + ", "
            else:
                break

    tmp_flag = flag_check(tax_cluster)
    if tmp_flag and tmp_flag not in flag.split(", "):
        flag += tmp_flag + ", "
    if repr_tax == 'No Match':
        flag += 'No_Match, '

    return flag[:-2], repr_tax


def calc_repr_taxonomy_species(tax_cluster):
    """Gets the representative taxonomy for species, first checking if all
    entries in the cluster are equal then checking if they match using the
    algorithm.
    """
    eq_tax = True
    repr_tax = tax_cluster[0]
    flag = ''
    for tax in tax_cluster:
        if len(tax) > 0:
            if tax[-1] != repr_tax[-1]:
                eq_tax = False
                break
        if len(tax) > len(repr_tax):
            repr_tax = tax

    if not eq_tax:
        eq_tax, repr_tax, flag = algo_repr(tax_cluster)

    return eq_tax, tax_list_to_str(repr_tax), flag


def calc_repr_taxonomy_rest(tax_cluster):
    """Gets the representative taxonomy for lower categories, first checking if
    all entries in the cluster are equal then checking if they match using the
    algorithm.
    """
    eq_tax = True
    repr_tax = tax_cluster[0]
    flag = ''
    for tax in tax_cluster:
        if tax != repr_tax:
            eq_tax = False
            break

    if not eq_tax:
        eq_tax, repr_tax, flag = algo_repr(tax_cluster)

    return eq_tax, tax_list_to_str(repr_tax), flag


def algo_repr(tax_cluster):
    """Algorithm used to calculate representative taxonomy in cluster, looking
    for highest fraction and calculating if smaller fraction(s) are just
    wrongly annotated.
    """
    new_cluster = []
    repr_tax = ''
    found = False
    flag = ''

    if len(tax_cluster) > 10:
        for tax in tax_cluster:
            new_cluster.append(tax_list_to_str(tax))

        c_cluster = []
        high_fract = 0.0
        total_count = 0
        highest = 0
        c_cluster = Counter(new_cluster)
        mc = c_cluster.most_common(1)
        repr_tax = mc[0][0].split(";")
        highest = mc[0][1]
        total_count = len(tax_cluster)

        high_fract = highest/total_count
        if high_fract >= 0.9:
            found = True
            flag = 'Outlier'

    return found, repr_tax, flag


def cluster_filter_species(tax_cluster):
    """Takes a cluster of taxonomy and an index list, using the index list all
    corresponding taxonomies are extracted and returned as a new cluster list.
    Avoiding all entries where the first letter is lowercase in species name.
    """
    c_dict = {}
    new_cluster = []
    chosen = [i for i in range(len(tax_cluster))]

    for i in range(len(tax_cluster)):
        if (tax_cluster[i][-1][0].islower()):
            chosen.remove(i)

    for i in range(len(tax_cluster)):
        c_dict[i] = tax_cluster[i]
    for i in chosen:
        new_cluster.append(c_dict[i])
    return new_cluster


def flag_header(str_id):
    """Gets the flag header from the flag_clusters file, (first line, starts
    with #\t)
    """
    run_path = return_proj_path() + str_id
    flag_clusters_file = run_path + '/flag_clusters'
    header = ''

    flag_file = open(flag_clusters_file, 'r')
    header = flag_file.readline()
    flag_file.close()

    return header


def repr_and_flag(str_id):
    """Takes an identity (in str) and opens the corresponding tax_clusters
    file, where all clusters are iterated over. Each cluster is assigned a
    representative taxonomy and those that are considered unusual are flagged
    for later manual review.
    """
    run_path = return_proj_path() + str_id
    tax_clusters_file = run_path + '/tax_clusters'
    repr_clusters_file = run_path + '/repr_clusters'
    flag_clusters_file = run_path + '/flag_clusters' + '.bak'

    with open(tax_clusters_file, 'r') as tax_file, \
         open(repr_clusters_file, 'w') as repr_file, \
         open(flag_clusters_file, 'w') as flag_file:

        first_line = True
        curr_cluster = []
        header_dict = {}
        c_label = ''
        old_label = ''

        for line in tax_file:
            curr_line = line.rstrip()
            if (curr_line[0:3] == 'MQR' or curr_line == 'end'):
                old_label = c_label

                if not first_line:
                    my_cluster = Cluster(old_label, curr_cluster)
                    flag, repr_tax = repr_taxonomy(my_cluster.get_taxeslist())

                    my_cluster.change_flags(flag)
                    my_cluster.change_reprtax(repr_tax)

                    repr_file.write("{}\t{}\n".format(
                        my_cluster.get_label(),
                        my_cluster.get_reprtax()
                        ))
                    if my_cluster.get_flags():
                        for flag in my_cluster.get_flags().split(", "):
                            if flag not in header_dict:
                                header_dict[flag] = 1
                            else:
                                header_dict[flag] += 1

                        flag_file.write("{}\t{}\t{}\n".format(
                            my_cluster.get_label(),
                            my_cluster.get_reprtax(),
                            my_cluster.get_flags()
                            ))
                        for tax in my_cluster.get_entries():
                            flag_file.write(tax + "\n")

                c_label = curr_line
                first_line = False
                curr_cluster = []

            else:
                curr_cluster.append(curr_line)

    #: creates a new file with the header at start, followed by all flags
    header_flag = '#\t'
    for flag in header_dict:
        header_flag += "{}: {}\t".format(flag, header_dict[flag])
    flag_out = flag_clusters_file[:-4]

    with open(flag_out, 'w') as flag_file, \
         open(flag_clusters_file, 'r') as orig_file:

        flag_file.write(header_flag[:-1] + "\n")
        for line in orig_file:
            flag_file.write(line)
        flag_file.write('end')
    os.remove(flag_clusters_file)


def confirm_accept(option, flag=''):
    """Used for the confirmation propt in the accept prompt option.
    """
    input_loop = True

    if option == 'accept':
        opt_out = 'current suggestion'
    elif option == 'accept all':
        opt_out = 'all remaining suggestions'
    elif option == 'accept flag':
        opt_out = 'all from the flag: ' + flag

    opt_cmd = input("{}{}{}".format(
        'Accept ',
        opt_out,
        '? y/n\nInput: '
    ))
    curr_opt = opt_cmd.lower()

    if curr_opt == 'y' or curr_opt == 'yes':
        print('Accepting\n')
        input_loop = False
    elif curr_opt == 'n' or curr_opt == 'no':
        print('Not accepting\n')
    else:
        print("Invalid input")

    return input_loop


def confirm_prompt(sugg_repr_tax, old_repr_tax):
    """Used as a confirm prompt, prompted if want to use the new suggestion or
    keep the old suggestion.
    """
    print("\n{}\n\t{}\n".format("New suggested taxonomy: ", sugg_repr_tax))

    new_repr_tax = old_repr_tax
    opt_cmd = input("Keep new suggestion? y/n\nInput: ")
    curr_opt = opt_cmd.lower()
    input_loop = True

    if curr_opt == 'y' or curr_opt == 'yes':
        print('Keeping new suggestion: ' + sugg_repr_tax)
        new_repr_tax = sugg_repr_tax
        input_loop = False
    elif curr_opt == 'n' or curr_opt == 'no':
        print('Discarding new suggestion ' + sugg_repr_tax)
    else:
        print("Invalid input")

    return new_repr_tax, input_loop


def check_input_rem(input):
    """Checks if the input from the removal prompt is valid.
    """
    valid = True
    for entry in input:
        curr_range = entry.split("-")
        dig1 = curr_range[0]
        if not dig1.isdigit():
            valid = False
        if len(curr_range) > 1:
            dig2 = curr_range[1]
            if int(curr_range[0]) > int(curr_range[1]) or not dig2.isdigit():
                valid = False

    return valid


def prompt_accept(input, header):
    """Method for the accept alternative in manual_correction. Either accepts
    current suggestion, accepts all suggestions or accepts all suggestions from
    a given flag.
    """
    input_loop = True
    skip_review = False

    #: accepts current suggestion
    if len(input.split(" ")) == 1:

        input_loop = confirm_accept('accept')

    else:
        #: accepts all remaining suggestions
        if input.split(" ")[1] == 'all':
            input_loop = confirm_accept('accept all')
            skip_review = True

        #: accepts all remining suggestions from a specific flag
        elif input.split(" ")[1] in header.lower():
            input_loop = confirm_accept('accept flag', input.split(" ")[1])
            if not input_loop:
                accepted_flags.append(input.split(" ")[1])

        else:
            print("Invalid flag\n")

    return input_loop, skip_review


def prompt_exclude(my_cluster, exclusion_file):
    """Method for the exclude alternative in manual_correction. Removes a bad
    cluster and stores it in a flag_exclusions file for later review, this
    cluster does not appear in the final corrected repr_tax file.
    """
    input_loop = True
    opt_cmd = input("{}{}".format(
        'Are you sure you want to exclude current cluster?',
        ' y/n\nInput: '
    ))
    curr_opt = opt_cmd.lower()

    if curr_opt == 'y' or curr_opt == 'yes':
        print('Excluding\n')

        with open(exclusion_file, 'a+') as exclusions:

            exclusions.write("{}\t{}\t{}\n".format(
                my_cluster.get_label(),
                my_cluster.get_reprtax(),
                my_cluster.get_flags() + ", Excluded"
                ))
            for tax in my_cluster.get_entries():
                exclusions.write(tax + "\n")

        my_cluster.change_reprtax('Excluded')
        input_loop = False
    elif curr_opt == 'n' or curr_opt == 'no':
        print('Not excluding\n')
    else:
        print("Invalid input")

    return input_loop


def prompt_exit():
    """Method for the exit alternative in manual_correction. Exiting the
    correction prompt loop and rejecting all further suggestions.
    """
    exit_review = False
    input_loop = True

    opt_cmd = input('Are you sure you want to exit? y/n\nInput: ')
    curr_opt = opt_cmd.lower()

    if curr_opt == 'y' or curr_opt == 'yes':
        print("Discarding remaining flags")
        exit_review = True
        input_loop = False
    elif curr_opt == 'n' or curr_opt == 'no':
        print('Not exiting\n')
    else:
        print("Invalid input")

    return exit_review, input_loop


def prompt_flag(header):
    """Method for the flags alternative in manual_correction. Displays all
    flags and their respective occurences in the flag file.
    """
    print("\nFlag:\t\tCount")
    for flag in header.split("\t"):
        flag_line = flag.split(" ")
        print("{}\t{}".format(flag_line[0], flag_line[1]))
    print("\n")


def prompt_keep(input, my_cluster):
    """Method for the keep alternative in manual_correction. Takes the taxonomy
    from the cluster using the id specified. If using c/s-x the categories or
    species names are split by " " resp. ";" and removed equal to x.
    """
    cho_full_inp = input.split(" ")[1:]
    cho_id = int(cho_full_inp[0])
    cluster = my_cluster.get_taxeslist()
    tmp_repr_tax = cluster[cho_id-1]
    input_loop = True

    #: if keep and alternatives
    if len(cho_full_inp) > 1:
        cho_option = cho_full_inp[1].split("-")[0].lower()
        cho_digit = int(cho_full_inp[1].split("-")[1])

        #: removing from categories
        if cho_option == 'c':
            cho_repr_tax = ";".join(
                tmp_repr_tax[:len(tmp_repr_tax)-cho_digit])

            new_repr_tax, input_loop = confirm_prompt(
                cho_repr_tax,
                my_cluster.get_reprtax()
                )
            my_cluster.change_reprtax(new_repr_tax)

        #: removing from species
        elif cho_option == 's':
            tmp_split = tmp_repr_tax[-1].split(" ")
            tmp_sp = " ".join(tmp_split[:len(tmp_split)-cho_digit])
            cho_repr_tax = tmp_repr_tax[:-1]
            cho_repr_tax.append(tmp_sp)
            cho_repr_tax = ";".join(cho_repr_tax)

            new_repr_tax, input_loop = confirm_prompt(
                cho_repr_tax,
                my_cluster.get_reprtax()
                )
            my_cluster.change_reprtax(new_repr_tax)

        else:
            print("Invalid choice")

    #: if keeping just one id
    elif len(cho_full_inp) == 1:
        cho_str_tax = my_cluster.get_taxesstring()[cho_id-1]
        new_repr_tax, input_loop = confirm_prompt(
            cho_str_tax,
            my_cluster.get_reprtax()
        )
        my_cluster.change_reprtax(new_repr_tax)

    else:
        print("Invalid choice")

    return input_loop


def prompt_manual(input, my_cluster):
    """Method for the manual alternative in manual_correction. Uses the
    manually input suggestion as representative taxonomy for the cluster.
    """
    man_repr_tax = input.split(" ")[1]

    new_repr_tax, input_loop = confirm_prompt(
        man_repr_tax,
        my_cluster.get_reprtax()
        )
    my_cluster.change_reprtax(new_repr_tax)

    return input_loop


def prompt_print(my_cluster):
    """Method for the intial prompt print in manual_correction. Printing the
    label, the flags and the entries in the cluster followed by options to
    modify, accept or exclude the cluster.
    """
    prompt_before = "{}: {} {}: {}\n\n{}\t{}\n".format(
        'Cluster',
        my_cluster.get_label(),
        'Flag(s)',
        my_cluster.get_flags(),
        'Id',
        'Taxonomy'
    )

    prompt_clust = ""
    i = 1
    for tax in my_cluster.get_taxesstring():
        prompt_clust += "{}\t{}\n".format(
            i,
            tax
            )
        i += 1

    prompt_after = "\n{}: \n\t{}".format(
        'Suggested taxonomy',
        my_cluster.get_reprtax(),
    )

    prompt_clust_full = prompt_before + prompt_clust + prompt_after
    old_prompt_text = """

Accept suggestion, alt. accept all/all from one flag: accept [all] [flag]
Manual entry: manual Taxonomy;To;Use
Keep entry to represent: keep id [c-2 / s-3]
Need suggestion by removing ids: remove id1-id3 id5
Ignore current cluster and save it for later review: exclude
Show flags and their respective occurences: flags
Exit, discarding all remaining suggestions: exit


Input: """

    prompt_text = """

accept [all]/[flag]\tAccept current suggestion, accept all or all from one flag
manual Taxonomy;To;Use\tManual entry of taxonomy
keep id [c-2]/[s-3]\tKeep entry to represent, category/species - cut columns
remove id1-id3 id5\tNew suggestion calculated by removing entries
exclude\t\t\tIgnore current cluster and save it for later review
flags\t\t\tShow flags and their respective occurences
exit\t\t\tExit, discarding all remaining suggestions


Input: """

    prompt_out = prompt_clust_full + prompt_text
    return prompt_out


def prompt_remove(input, my_cluster):
    """Method for the remove alternative in manual_correction. Takes the input
    ids either as single, ranges of ids or a combination. These are removed
    from the cluster and fed into the repr_tax function and a new suggestion
    is attained using the trimmed cluster.
    """
    cluster = my_cluster.get_taxeslist()
    valid_input = check_input_rem(input.split(" ")[1:])

    if valid_input:
        remove_loop = True
        entries = input.split(" ")[1:]
        removed_ids = []
        kept_ids = [i for i in range(1, len(cluster) + 1)]
        for entry in entries:
            if '-' in entry:
                for i in range(
                    int(entry.split("-")[0]),
                    int(entry.split("-")[1])+1
                ):
                    removed_ids.append(i)
            else:
                removed_ids.append(int(entry))

        for id in removed_ids:
            kept_ids.remove(id)

        new_cluster = []
        for i in range(len(cluster)):
            if i+1 not in removed_ids:
                new_cluster.append(cluster[i])

        _, temp_repr_tax = repr_taxonomy(new_cluster)

        removed_ids_str = ''
        kept_ids_str = ''

        for id in removed_ids:
            removed_ids_str += str(id) + ", "
        print('\nRemoving entries: ' + removed_ids_str[:-2])

        for id in kept_ids:
            kept_ids_str += str(id) + ", "
        print('Keeping entries: ' + kept_ids_str[:-2])

        new_repr_tax, input_loop = confirm_prompt(
            temp_repr_tax,
            my_cluster.get_reprtax()
            )
        my_cluster.change_reprtax(new_repr_tax)

    else:
        print("Invalid input")

    return input_loop


def run_correction(my_cluster, skip_review, exit_review):
    """Wrapping function to perform full correction on cluster.
    """
    if skip_review or exit_review:
        pass
    else:
        skip_review, exit_review = manual_correction(my_cluster)
    return skip_review, exit_review


def repr_correction(str_id):
    """Creates a new file, repr_correction, which contains all manually
    corrected flagged taxonomies, as well as those that were not flagged.
    """
    run_path = return_proj_path() + str_id
    repr_clusters_file = run_path + '/repr_clusters'
    repr_correction_file = run_path + '/repr_correction'
    flag_correction_file = run_path + '/flag_correction'

    with open(repr_clusters_file, 'r') as repr_file, \
         open(repr_correction_file, 'w') as corr_file, \
         open(flag_correction_file, 'r') as flag_file:

        corr_dict = {}
        for line in flag_file:
            flag_split = line.rstrip().split("\t")
            corr_dict[flag_split[0]] = flag_split[1]

        for repr_line in repr_file:
            found = False
            curr_line = repr_line.rstrip()
            curr_label = curr_line.split("\t")[0]
            curr_repr = curr_line.split("\t")[1]

            if curr_label in corr_dict:
                new_repr = corr_dict[curr_label]
                if new_repr != 'Excluded':
                    corr_file.write("{}\t{}\n".format(curr_label, new_repr))
                corr_dict.pop(curr_label)
            else:
                corr_file.write("{}\t{}\n".format(curr_label, curr_repr))


def manual_correction(my_cluster):
    """Displays each cluster with its suggested taxonomy and label. Prompts
    """
    input_loop = True
    skip_review = False
    exit_review = False
    str_id = my_cluster.get_strid()
    run_path = return_proj_path() + str_id
    flag_exclusions_file = run_path + '/flag_exclusions'
    header = "\t".join(flag_header(str_id).split("\t")[1:]).rstrip()

    def_prompt = prompt_print(my_cluster)
    while input_loop:

        #: checks flags if accepted already
        flags = my_cluster.get_flags().lower().split(", ")
        flag = flags[0]
        if len(flags) == 1:
            if flag in accepted_flags:
                input_loop = False

        else:
            input_loop = False
            for flag in flags:
                if flag not in accepted_flags:
                    input_loop = True

        if not input_loop:
            break

        inp_cmd = input(def_prompt)
        curr_inp = inp_cmd.lower()

        #: accept option
        #: accepting cluster/all/all from flag
        if curr_inp.split(" ")[0] == 'accept':
            input_loop, skip_review = prompt_accept(curr_inp, header)

        #: exclude option
        #: excluding current cluster, saving to flag_exclusions
        elif curr_inp == 'exclude':
            input_loop = prompt_exclude(my_cluster, flag_exclusions_file)

        #: exit option
        #: rejects all remaining suggestions and exits
        elif curr_inp == 'exit':
            exit_review, input_loop = prompt_exit()

        #: flag option
        #: prints all flags and their occurences
        elif curr_inp == 'flags' or curr_inp == 'flag':
            prompt_flag(header)

        #: keep option
        #: keeping an id and optionally removing from species or categories
        elif (curr_inp.split(" ")[0] == 'keep'):
            input_loop = prompt_keep(curr_inp, my_cluster)

        #: manual option
        #: takes manual input as suggestion
        elif (
            curr_inp.split(" ")[0] == 'manual'
            and len(curr_inp.split(" ")) > 1
        ):
            input_loop = prompt_manual(inp_cmd, my_cluster)

        #: remove option
        #: removes all entries by id then suggest new taxonomy with remaining
        elif (
            curr_inp.split(" ")[0] == 'remove'
            and len(curr_inp.split(" ")) > 1
        ):
            input_loop = prompt_remove(curr_inp, my_cluster)

        else:
            print("Invalid choice")

    return skip_review, exit_review


def flag_correction(str_id):
    """Opens the flag file, and with the use of manual inputs corrects the
    flagged suggestions of representative taxonomy, into a new file with all
    non-flagged suggestions.
    """
    accepted_flags = []
    run_path = return_proj_path() + str_id
    flag_clusters_file = run_path + '/flag_clusters'
    flag_correction_file = run_path + '/flag_correction'
    flag_exclusions_file = run_path + '/flag_exclusions'
    if os.path.isfile(flag_exclusions_file):
        os.remove(flag_exclusions_file)

    with open(flag_clusters_file, 'r') as flag_file, \
         open(flag_correction_file, 'w') as corr_file:

        curr_cluster = []
        cluster_label = ''
        old_label = ''
        cluster_repr = ''
        old_repr = ''
        cluster_flags = ''
        old_flags = ''
        first_line = True
        skip_review = False
        exit_review = False

        header = flag_file.readline()

        for line in flag_file:
            curr_line = line.rstrip()
            if (
                curr_line.split("\t")[0][:3] == "MQR"
                or curr_line == 'end'
            ):

                old_label = cluster_label
                old_repr = cluster_repr
                old_flags = cluster_flags

                if not first_line:
                    my_cluster = Cluster(
                        old_label,
                        curr_cluster,
                        repr_tax=old_repr,
                        flags=old_flags
                        )
                    skip_review, exit_review = run_correction(
                        my_cluster,
                        skip_review,
                        exit_review
                        )

                    if exit_review:
                        break

                    corr_file.write("{}\t{}\n".format(
                        my_cluster.get_label(),
                        my_cluster.get_reprtax()
                        ))

                if curr_line != 'end':
                    cluster_label = curr_line.split("\t")[0]
                    cluster_repr = curr_line.split("\t")[1]
                    cluster_flags = curr_line.split("\t")[2]

                first_line = False
                curr_cluster = []

            else:
                curr_cluster.append(curr_line)

    repr_correction(str_id)
