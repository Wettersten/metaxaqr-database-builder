"""Methods related to various handling functions, such as getting the path to
the project etc
"""

import os
from pathlib import Path
import argparse
import importlib
from datetime import datetime
from shutil import which


def create_dir_structure(str_id):
    """Creates the directory structure used by clustering and subsequent
    handling of clusters. Cluster files in mqr_db/identity/clusters/
    """
    cluster_dir = return_proj_path() + str_id + '/clusters/'
    Path(cluster_dir).mkdir(parents=True, exist_ok=True)


def return_proj_path():
    """Returns the path to project dir, if output path specified mqr_db will be
    created in that path.
    """
    path_file = os.getcwd() + "/mqrdb_init.txt"
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
    path_file = os.getcwd() + "/mqrdb_init.txt"
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
    check_installation(args)
    check_args(args)
    check_prereqs(args)


def check_args(args):
    """Checks that the use of args are correct, at least one main argument is
    used, the input file and output paths are valid.
    """
    if (
        not args.opt_prepare
        and not args.opt_makedb
        and not args.opt_addseq
        and not args.opt_license
        and not args.opt_ds
    ):
        error_msg = "ERROR: No option chosen."
        quit(error_msg)

    if args.opt_prepare:
        file = args.opt_prepare
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


def check_installation(args):
    """Checks if valid installation, checking for dependencies.
    """
    reqs = []
    preqs = []
    if (
        args.opt_prepare
        or args.opt_makedb
    ):
        reqs = ['vsearch']
        preqs = []

    for tool in reqs:
        error_msg = "{} was not found".format(tool)
        if not is_tool(tool):
            quit(error_msg)

    for package in preqs:
        error_msg = "{} was not found".format(package)
        if not is_package(package):
            quit(error_msg)


def check_prereqs(args):
    """Checks if the args are used correctly - in correct order (not starting
    with the review before using initial clustering).
    """
    if args.opt_prepare:
        dir = return_proj_path()

        if check_dir(dir):
            error_msg = "ERROR: {} already exists".format(dir)
            quit(error_msg)

    if args.opt_makedb:
        flag_file = return_proj_path() + '100/flag_clusters'
        error_msg = "ERROR: {file} {txt}".format(
            file=flag_file,
            txt="missing, please perform preparation [-p] first"
            )
        if not check_file(flag_file):
            quit(error_msg)

    #: deprecated
"""
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
"""


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable
    """
    return which(name)


def is_package(name):
    """Check whether `name` is an installed python package
    """
    package = importlib.util.find_spec(name)
    if package:
        return True
    else:
        return False


def logging(option, id='', quiet=False):
    """
    """
    ln = "-----------------------------------------------------------------"

    if option == "initialize":
        print("{he}\n{ln}\n{dt} : {st}\n{ln}".format(
            he=get_header(option),
            ln=ln,
            dt=get_dateinfo(),
            st="Starting MetaxaQR_DB Clustering..."
        ))

    elif option == "clustering_start":
        print("{he}\n{ln}\n{dt} : {st}".format(
            he=get_header(option.split("_")[0]),
            ln=ln,
            dt=get_dateinfo(),
            st="Clustering input database at 100% sequence identity"
            " (this may take a long while)..."
        ))

    elif option == "clustering_seq_end":
        print("{dt} : {st}".format(
            dt=get_dateinfo(),
            st="Clustering at 100% sequence identity finished."
        ))

    elif option == "clustering_tax_start":
        print("{dt} : {st}".format(
            dt=get_dateinfo(),
            st="Taxonomic flagging and processing started."
        ))

    elif option == "clustering_tax_end":
        print("{dt} : {st}".format(
            dt=get_dateinfo(),
            st="Taxonomic flagging and processing finished."
        ))

    elif option == "clustering_end":
        print("{dt} : {st}\n{ln}".format(
            ln=ln,
            dt=get_dateinfo(),
            st="Clustering finished!"
        ))

    elif option == "manual review_start":
        print("{dt} : {st}\n{ln}\n{he}\n{ln}\n{dt} : {tt}".format(
            he=get_header(option.split("_")[0]),
            ln=ln,
            dt=get_dateinfo(),
            st="Starting MetaxaQR_DB Manual Review...",
            tt="Manual Review of flagged clusters started."
        ))

    elif option == "manual review_end":
        print("{dt} : {st}\n{ln}".format(
            ln=ln,
            dt=get_dateinfo(),
            st="Manual Review of flagged clusters finished!"
        ))

    elif option == "finalize_start":
        print("{dt} : {st}\n{ln}\n{he}\n{ln}".format(
            he=get_header(option.split("_")[0]),
            ln=ln,
            dt=get_dateinfo(),
            st="Starting MetaxaQR_DB Finalize..."
        ))

    elif option == "finalize_loop_start":
        st = ""
        if int(id) == 100:
            st = "Clustering at 99% sequence identity..."
        elif int(id) == 50:
            st = "Finalizing output from the 50% sequence identity run..."
        elif int(id) > 90:
            st = "Clustering at {id2}% sequence identity...".format(
                id2=str(int(id)-1)
            )
        else:
            st = "Clustering at {id2}% sequence identity...".format(
                id2=str(int(id)-5)
            )

        print("{dt} : {st}".format(
            dt=get_dateinfo(),
            st=st
        ))

    elif option == "finalize_loop_end":
        st = ""
        if int(id) == 50:
            pass
        elif int(id) > 90:
            st = "Clustering at {id}% sequence identity is finished.".format(
                id=str(int(id)-1)
            )

            print("{dt} : {st}".format(
                dt=get_dateinfo(),
                st=st
            ))
        else:
            st = "Clustering at {id}% sequence identity is finished.".format(
                id=str(int(id)-5)
            )

            print("{dt} : {st}".format(
                dt=get_dateinfo(),
                st=st
            ))

    elif option == "finalize_end":
        print("{dt} : {st}\n{ln}".format(
            ln=ln,
            dt=get_dateinfo(),
            st="Clustering and finalization of output is finished!"
        ))

    elif option == "make db_start":
        print("{he}\n{ln}\n{dt} : {st}".format(
            he=get_header(option.split("_")[0]),
            ln=ln,
            dt=get_dateinfo(),
            st="Creating the MetaxaQR database..."
        ))

    elif option == "make db_end":
        print("{dt} : {st}\n".format(
            dt=get_dateinfo(),
            st="MetaxaQR database has been created!"
        ))

    elif option == "add entries_start":
        print("{dt} : {st}\n{ln}\n{he}\n{ln}\n{dt} : {at}".format(
            he=get_header(option.split("_")[0]),
            ln=ln,
            dt=get_dateinfo(),
            st="Starting MetaxaQR_DB Add Entries...",
            at="Adding new entries to the MetaxaQR database..."
        ))
    elif option == "add entries_end":
        print("{dt} : {st}\n".format(
            dt=get_dateinfo(),
            st="New entries have been added to the MetaxaQR database!"
        ))


def get_dateinfo():
    date = datetime.today()
    weekday = date.strftime('%a')
    month = date.strftime('%b')
    day = date.strftime('%d')
    time = date.strftime('%X')
    year = date.strftime('%Y')
    out_date = "{} {} {} {} {}".format(
        weekday,
        month,
        day,
        time,
        year
    )
    return out_date


def get_header(option):
    header = ""
    version = get_version()
    bytext = "by Sebastian Wettersten, University of Gothenburg."
    license = "This program is distributed under the GNU GPL 3 license, use" \
              " the --license option for more information on this license."

    if option == "initialize":
        htext = "MetaxaQR Database Builder -- Automatic curation of genetic" \
                " marker databases for MetaxaQR"
        header = "{}\n{}\n{}\n{}".format(
            htext,
            bytext,
            version,
            license
        )

    elif option == "clustering":
        htext = "MetaxaQR_DB Clustering -- Clusters a database using" \
                " VSEARCH"
        header = "{}\n{}\n{}".format(
            htext,
            bytext,
            version,
        )

    elif option == "manual review":
        htext = "MetaxaQR_DB Manual Review -- Manual review of clusters" \
                " flagged during taxonomic processing"
        header = "{}\n{}\n{}".format(
            htext,
            bytext,
            version,
        )

    elif option == "finalize":
        htext = "MetaxaQR_DB Finalize -- Preparation of final output files" \
                " and clustering down to 50% sequence identity."
        header = "{}\n{}\n{}".format(
            htext,
            bytext,
            version,
        )

    elif option == "make db":
        htext = "MetaxaQR_DB Make DB -- Creates the MetaxaQR database from" \
            " the output of 'Finalize'."
        header = "{}\n{}\n{}".format(
            htext,
            bytext,
            version,
        )

    elif option == "add entries":
        htext = "MetaxaQR_DB Add Entries -- Adds new entries from a FASTA" \
            " file to a finished MetaxaQR database."
        header = "{}\n{}\n{}".format(
            htext,
            bytext,
            version,
        )

    return header


def get_version():
    """Current version of the MetaxaQR Database Builder.
    """
    return "Version: 0.2"


def print_license():
    """Prints the GNU GPL 3 license.
    """
    license_file = "{}/LICENSE".format(Path(__file__).parent.parent.parent)

    with open(license_file, 'r') as f:
        a = f.read()
        print(a)
