import time
import os
import pathlib
import argparse
from shutil import which


def create_dir_structure(str_id):
    """Creates the directory structure used by clustering and subsequent
    handling of clusters. Cluster files in mc_db/identity/clusters/
    """
    cluster_dir = return_proj_path() + str_id + '/clusters/'
    pathlib.Path(cluster_dir).mkdir(parents=True, exist_ok=True)


def return_proj_path():
    """Returns the path to project dir, if output path specified mqr_db will be
    created in that path.
    """
    path_file = os.getcwd() + "/mc_init.txt"
    if check_file(path_file):
        with open(path_file, 'r') as file:
            proj_path = file.readline().rstrip() + '/mqr_db/'
    else:
        proj_path = os.getcwd() + '/mqr_db/'

    return proj_path


def set_proj_path(path):
    """Sets custom project path (if -p given when -c is used), this is saves as
    the first line in a local file for later retrieval.
    """
    path_file = os.getcwd() + "/mc_init.txt"
    if check_file(path_file):
        os.remove(path_file)

    with open(path_file, 'w') as file:
        if path[-1] == '/':
            file.write(path[:-1])
        else:
            file.write(path)


def tax_list_to_str(tlist):
    """Changes a split list of taxonomies back to a string.
    """
    return ";".join(tlist)


def float_to_str_id(identity):
    """Converts a float identity (0.95) to a str (95).
    """
    str_id = (str(int(float(identity)*100)))
    return str(str_id)


def error_check(args):
    """Main error checking method, ran when executing main script first after
    the parser, checks that all arguments are valid, all required programs are
    installed and that any files needed exist or paths not already created.
    Quits with error messages if anything is invalid.
    """
    check_installation()
    check_args(args)
    check_prereqs(args)


def check_args(args):
    """Checks that the use of args are correct, at least one main argument is
    used, the input file and output paths are valid.
    """
    if (
        not args.opt_clustering
        and not args.opt_review
        and not args.opt_finalize
        and not args.opt_makedb
    ):
        error_msg = "ERROR: No option chosen, use one from [-c/-r/-f/-m]"
        quit(error_msg)

    if (
        (args.input and not args.opt_clustering)
        or (args.output and not args.opt_clustering)
    ):
        error_msg = "ERROR: [-i]/[-o] only works using clustering [-c]"
        quit(error_msg)

    if args.input:
        file = args.input
        error_msg = "ERROR: Could not find the file: {}".format(file)
        if not check_file(file):
            quit(error_msg)

    if args.output:
        out_dir = args.output

        if out_dir[-1] == '/':
            dir = out_dir + "mqr_db/"
        else:
            dir = args.output + "/mqr_db/"

        error_msg = "ERROR: {} already exists".format(dir)

        if check_dir(dir):
            quit(error_msg)


def check_dir(path):
    """Checks if the directory/path exists, returning True/False
    """
    return os.path.isdir(path)


def check_file(file):
    """Checks if the file exists, retuning True/False
    """
    return os.path.isfile(file)


def check_installation():
    """Checks if valid installation, if vsearch + ? is found.
    """
    reqs = ['vsearch']

    for tool in reqs:
        error_msg = "{} was not found".format(tool)
        if not is_tool(tool):
            quit(error_msg)


def check_prereqs(args):
    """Checks if the args are used correctly - in correct order (not starting
    with the review before using initial clustering).
    """
    if args.opt_clustering:
        dir = return_proj_path()

        if check_dir(dir):
            error_msg = "ERROR: {} already exists".format(dir)
            quit(error_msg)

        if not args.input:
            error_msg = "ERROR: no input database specified"
            quit(error_msg)

    if args.opt_review:
        flag_file = return_proj_path() + '100/flag_clusters'
        error_msg = "ERROR: {file} {txt}".format(
            file=flag_file,
            txt="missing, please perform clustering [-c] first"
            )
        if not check_file(flag_file):
            quit(error_msg)

    if args.opt_finalize:
        repr_file = return_proj_path() + '100/repr_correction'
        error_msg = "ERROR: {file} {txt}".format(
            file=repr_file,
            txt="missing, please perform review [-r] first"
            )
        if not check_file(repr_file):
            quit(error_msg)

    if args.opt_makedb:
        tree_file = return_proj_path() + '95/label_tree'
        error_msg = "ERROR: {file} {txt}".format(
            file=tree_file,
            txt="missing, please perform finalize [-f] first"
            )
        if not check_file(tree_file):
            quit(error_msg)


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable
    """
    return which(name)


def logging(
            str_id='',
            etime='',
            db='',
            time_log=False,
            quiet=False,
            start=False,
            custom=False,
            custom_msg=''
            ):
    """Used for logging messages/time spent on processes etc
    """
    log_msg = ''
    logging_file = os.getcwd() + '/mc_log.txt'

    if time_log:
        time_log_msg = "Done in Hours:Minutes:Seconds"
        time_msg = time.strftime("%H:%M:%S", time.gmtime(etime))
        log_msg = "{}\n{}\n\n".format(time_log_msg, time_msg)

    elif custom:
        log_msg = custom_msg

    else:
        if start:
            log_msg = "{txt1}: {id} {txt2}: {idb}\n".format(
                    txt1="Running VSEARCH at id",
                    id=str_id,
                    txt2="using database",
                    idb=db
                )
        elif int(str_id) > 50:
            if intr(str_id) > 90:
                nxt_id = str(int(str_id)-1)
            else:
                nxt_id = str(int(str_id)-5)

            log_msg = "{txt1}: {id1} {txt2}: {id2}\n".format(
                    txt1="Finalizing id",
                    id1=str_id,
                    txt2="and running VSEARCH at id",
                    id2=nxt_id
                )
        else:
            log_msg = "Finalizing output\n"

    if start:
        if os.path.isfile(logging_file):
            os.remove(logging_file)
        with open(logging_file, 'w') as log_file:
            log_file.write(log_msg)
            if not quiet:
                print(log_msg)

    else:
        with open(logging_file, 'a') as log_file:
            log_file.write(log_msg)
            if not quiet:
                print(log_msg)
