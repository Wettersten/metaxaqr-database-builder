import time
import os
import pathlib


def create_dir_structure(str_ident):
    """Creates the directory structure used by clustering and subsequent
    handling of clusters. Cluster files in mc_db/identity/clusters/
    """
    dir_path = os.getcwd()
    # Maybe use parser.out_path
    parent_dir = '/mqr_db/'
    cluster_dir = '/clusters/'
    new_dir_path = dir_path + parent_dir + str_ident + cluster_dir
    pathlib.Path(new_dir_path).mkdir(parents=True, exist_ok=True)


def return_proj_path():
    """Returns the path to current path, appending identity will return path to
    clustering files.
    """
    proj_path = os.getcwd() + '/mqr_db/'
    return proj_path


def tax_list_to_str(tlist):
    """Changes a split list of taxonomies back to a string.
    """
    return ";".join(tlist)


def id_range_to_list(identity):
    """Converts identity arg to a list of either a identity or a range of
    identities, depending on input. Also returns True if range and False if
    not. Returning a list in the format of floats.
    """
    check_id_range(identity)
    id_list = []
    id_range = str(identity).split("-")
    if len(id_range) > 1:
        is_range = True
        c_range = int((float(id_range[1])*100) - (float(id_range[0])*100))+1
        for i in range(c_range):
            id_list.append("{:.2f}".format(float(id_range[0]) + float(i/100)))
    else:
        id_list.append("{:.2f}".format(float(id_range[0])))
    return id_list


def float_to_str_id(identity):
    """Converts a float identity (0.95) to a str (95).
    """
    str_id = (str(int(float(identity)*100)))
    return str(str_id)


def logging():
    """Todo - Used to log time used etc
    """
    start_time = time.time()
    elapsed_time = time.time() - start_time

    with open('cluster_tax_log.txt', 'w') as out_file:
        out_file.write("Project: {}\n".format(fasta_file))
        out_file.write("Identities performed: {}\n".format(str(idents)))
        out_file.write("Done in Hours:Minutes:Seconds\n")
        out_file.write(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
