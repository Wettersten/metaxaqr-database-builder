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
                                curr_id = remove_cf_line(lines.rstrip())
                                clust_out.write("{}\n".format(curr_id))

            clust_out.write("end")  # used by cluster_stats to denote eof


def mark_flag(cluster_label):
    """Used to flag a cluster label when the taxonomy within is weird and needs
    manual attention.
    """
    pass


def remove_cf_line(tax_line):
    """Removes all occurences of "cf. " within a line of taxonomy.
    """
    return tax_line.replace('cf. ', '')


def remove_cf_file(tax_file):
    """Removes all occurences of "cf. " within a tax_clusters file. (remove?)
    """
    cluster_file = tax_file
    old_file = "{}_old".format(cluster_file)
    if os.path.isfile(old_file):
        os.remove(old_file)
    os.rename(cluster_file, old_file)
    with open(old_file, 'r') as read_file:
        with open(cluster_file, 'w') as write_file:
            for line in read_file:
                new_line = "{}\n".format(line.rstrip().replace('cf. ', ''))
                write_file.write(new_line)
    os.remove(old_file)


def repr_taxonomy(cluster_label, cluster):
    """
    """
    repr_tax = 'No match'
    flag = False
    found = False
    sp_splits = 6
    for i in range(sp_splits):  # loop for species
        curr_cluster = []
        for tax in cluster:
            stripped_tax = tax[:-1]
            sp_tax = " ".join((tax[-1].split(" ")[:(sp_splits-i)]))
            stripped_tax.append(sp_tax)
            curr_cluster.append(stripped_tax)

        chosen = [i for i in range(len(curr_cluster))]
        for i in range(len(curr_cluster)):
            if (
                curr_cluster[i][-1] == 'unidentified'
                or curr_cluster[i][-1][0].islower()
            ):
                chosen.remove(i)
        chosen_cluster = cluster_filter(curr_cluster, chosen)
        if len(chosen) > 0:
            found, new_repr_tax, new_flag = calc_repr_taxonomy(chosen_cluster)
            if new_repr_tax[-3:] == 'sp.' or new_repr_tax[-1:] == '#':
                found = False
        if found:
            repr_tax = new_repr_tax
            flag = new_flag
            break

    if not found:
        for i in range(len(cluster[0])-2):  # loop for below species
            curr_cluster = []
            for tax in cluster:
                curr_cluster.append(tax[:len(tax)-(i+1)])
            found, new_repr_tax, new_flag = calc_repr_taxonomy(curr_cluster)
            if found:
                repr_tax = new_repr_tax
                flag = new_flag
                break

    return cluster_label, flag, repr_tax


def calc_repr_taxonomy(cluster):
    """
    """
    eq_tax = True
    repr_tax = cluster[0]
    flag = False
    for tax in cluster:
        if tax != repr_tax:
            eq_tax = False
            break

    if not eq_tax:
        eq_tax, repr_tax, flag = algo_repr(cluster)

    return eq_tax, tax_list_to_str(repr_tax), flag


def algo_repr(cluster):
    """Algorithm used to calculate representative taxonomy in cluster, looking
    for highest fraction and calculating if smaller fraction(s) are just
    wrongly annotated.
    """
    t_cluster = []
    c_cluster = []
    repr_tax = ''
    total_count = 0
    highest = 0
    found = False
    high_fract = 0.0
    flag = False

    if len(cluster) > 10:

        for tax in cluster:
            if tax not in t_cluster:
                t_cluster.append(tax)
                c_cluster.append(cluster.count(tax))

        for i in range(len(c_cluster)):
            curr_count = c_cluster[i]
            total_count += curr_count
            if curr_count > highest:
                highest = curr_count
                repr_tax = t_cluster[i]

        high_fract = highest/total_count
        if high_fract >= 0.9:
            found = True
            flag = True

    return found, repr_tax, flag


def cluster_filter(cluster, chosen):
    """Takes a cluster of taxonomy and an index list, using the index list all
    corresponding taxonomies are extracted and returned as a new cluster list.
    """
    c_dict = {}
    new_cluster = []
    for i in range(len(cluster)):
        c_dict[i] = cluster[i]
    for i in chosen:
        new_cluster.append(c_dict[i])
    return new_cluster


def repr_and_flag(str_id):
    """Takes an identity (in str) and opens the corresponding tax_clusters
    file, where all clusters are iterated over. Each cluster is assigned a
    representative taxonomy and those that are considered unusual are flagged
    for later manual review.
    """
    run_path = return_proj_path() + str_id
    tax_clusters_file = run_path + '/tax_clusters'
    repr_clusters_file = run_path + '/repr_clusters'
    flag_clusters_file = run_path + '/flag_clusters'

    with open(tax_clusters_file, 'r') as tax_file, \
        open(repr_clusters_file, 'w') as repr_file, \
            open(flag_clusters_file, 'w') as flag_file:
        first_line = True
        curr_cluster = []
        c_label = ''
        old_label = ''

        for line in tax_file:
            curr_line = line.rstrip()
            if curr_line[0:3] == 'MQR' or curr_line == 'end':
                old_label = c_label

                if not first_line:
                    cluster_label, flag, repr_tax = repr_taxonomy(
                        old_label, curr_cluster
                        )
                    repr_file.write("{}\n{}\n".format(cluster_label, repr_tax))
                    if flag:
                        flag_file.write(cluster_label + "\n")
                        for tax in flag_cluster:
                            flag_file.write(tax + "\n")

                c_label = curr_line
                first_line = False
                curr_cluster = []
                flag_cluster = []

            else:
                curr_cluster.append(
                                    " ".join(curr_line.split(" ")[1:]
                                             ).split(";"))
                flag_cluster.append(curr_line)
