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
