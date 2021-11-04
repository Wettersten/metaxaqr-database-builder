"""Methods related to various handling functions, such as getting the path to
the project, checking if files exists, error handling etc.
"""

import argparse
from datetime import datetime
import importlib
import os
from pathlib import Path
import shutil


def create_dir_structure(str_id):
    """Creates the directory structure used by clustering and subsequent
    handling of clusters. Cluster files in mqr_db/identity/clusters/
    """
    cluster_dir = return_proj_path() + str_id + '/clusters/'
    Path(cluster_dir).mkdir(parents=True, exist_ok=True)


def return_proj_path():
    """Returns the path to project dir.
    """
    proj_path = "{}/mqr_db/".format(os.getcwd())

    return proj_path


def return_label():
    """Gets the label specified for the run.
    """
    label = ''
    label_file = "{}init/label".format(return_proj_path())
    if check_file(label_file):
        with open(label_file, 'r') as f:
            label = f.read()

    return label


def return_qc_opts():
    """Gets the quality check options for the run from initial -p command.
    """
    qc_opts = ''
    qc_opts_file = "{}init/qc_opts"
    if check_file(qc_opts_file):
        with open(qc_opts_file, 'r') as f:
            qc_opts = f.read()

    return qc_opts


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
        and not args.opt_version_history
        and not args.opt_makehmms
        # and not args.opt_ds
    ):
        error_msg = "ERROR: No option chosen"
        quit(error_msg)

    if (
        args.opt_keep and not args.opt_makedb
    ):
        error_msg = "ERROR: --keep only works with -m/--makedb"
        quit(error_msg)

    if (
        args.opt_label and not args.opt_prepare
        or args.opt_qc and not args.opt_prepare
        or args.opt_gene_marker and not args.opt_prepare
    ):
        error_msg = """ERROR: --label, --qc and --gene_marker only works with
 -p/--prepare"""
        quit(error_msg)

    if (
        args.opt_gene_marker and not args.opt_qc
        or args.opt_qc and not args.opt_gene_marker
    ):
        error_msg = """ERROR: --label, --qc and --gene_marker only works with
 -p/--prepare"""
        quit(error_msg)

    if (
        args.opt_format and not args.opt_prepare
        or args.opt_format and not args.opt_addseq
    ):
        error_msg = """ERROR: --format only works with -p/--prepare or
-a/--addseq"""
        quit(error_msg)

    if (
        args.opt_db and not args.opt_addseq
    ):
        error_msg = "ERROR: --db only works with -a/--addseq"
        quit(error_msg)

    if args.opt_makehmms:
        if args.opt_makehmms not in ["conserved", "divergent", "hybrid"]:
            error_msg = """ERROR: incorrect mode chosen for -mh/--make_hmms,
            choose from conserved, divergent or hybrid."""
            quit(error_msg)

    if args.opt_makehmms == "conserved":
        if not check_file(args.opt_con_seq_db):
            error_msg = "ERROR: incorrect sequence database provided"
            quit(error_msg)


def check_dir(path):
    """Checks if the directory/path exists, returning True/False
    """
    return os.path.isdir(path)


def check_file(file):
    """Checks if the file exists, returning True/False
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
        or args.opt_addseq
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


def cleanup(all=True):
    """Cleanup of intermediate files, moves all files in mqr_db/removed/ and
    mqr_db/results to final output directory mqr_label.
    """
    run_label = return_label()
    mqr_path = return_proj_path()
    src_res = "{}results/".format(return_proj_path())
    src_rem = "{}removed/".format(return_proj_path())
    dest = "{}/{}_results/".format(os.getcwd(), run_label)
    Path(dest).mkdir(parents=True, exist_ok=True)

    files_res = os.listdir(src_res)
    files_rem = os.listdir(src_rem)

    for f in files_res:
        shutil.move(src_res + f, dest)
    for f in files_rem:
        shutil.move(src_rem + f, dest)

    shutil.rmtree(src_res)
    shutil.rmtree(src_rem)

    if all:
        shutil.rmtree(mqr_path)


def check_prereqs(args):
    """Checks if the args are used correctly - in correct order (not starting
    with the review before using initial clustering).
    """
    if args.opt_prepare:
        dir = return_proj_path()

        if check_dir(dir):
            error_msg = "ERROR: {} already exists".format(dir)
            quit(error_msg)

        if not args.opt_label:
            error_msg = "ERROR: No label specified"
            quit(error_msg)

    if args.opt_makedb:
        flag_file = return_proj_path() + '100/flag_clusters'
        error_msg = "ERROR: {file} {txt}".format(
            file=flag_file,
            txt="missing, please perform preparation [-p] first"
            )
        if not check_file(flag_file):
            quit(error_msg)


def is_tool(name):
    """Check whether `name` is on PATH and marked as executable
    """
    return shutil.which(name)


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

    if not quiet:
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
                st = "Clustering at {id}% sequence identity is \
finished.".format(id=str(int(id)-1))

                print("{dt} : {st}".format(
                    dt=get_dateinfo(),
                    st=st
                ))
            else:
                st = "Clustering at {id}% sequence identity is \
finished.".format(id=str(int(id)-5))

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

        elif option == "make hmms_start":
            print("{he}\n{ln}\n{dt} : {st}".format(
                he=get_header(option.split("_")[0]),
                ln=ln,
                dt=get_dateinfo(),
                st="Creating MetaxaQR HMMs..."
            ))
        elif option == "make hmms_end":
            print("{dt} : {st}\n".format(
                dt=get_dateinfo(),
                st="MetaxaQR HMMs have been created!"
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
    return "Version: 1.0.2"


def print_updates():
    """Prints the update history.
    """
    upd_history = """Version: Notes
V1.0.0: Initial release.\n
V1.0.1: Added support for the sequence quality option,
separating the QC option into 3 modes (Sequence, Taxonomy, Low clusters).\n
V1.0.2: Initial support for the Make HMMs module.\n
"""
    print(upd_history)


def print_license():
    """Prints the GNU GPL 3 license.
    """
    license_file = "{}/LICENSE".format(Path(__file__).parent.parent.parent)

    with open(license_file, 'r') as f:
        a = f.read()
        print(a)


def format_file(file, format):
    """Formatting method, used to take different inputs formats and format
    these to SILVA style.
    """
    out_file = "{}_formatted".format(file)

    with open(file, 'r') as to_format, \
         open(out_file, 'w') as formatted:

        if format == "ibol":
            format_ibol(to_format, formatted)
        elif format == "unite":
            format_unite(to_format, formatted)

    return out_file


def silva_format(id, tax, seq):
    """The format used by silva, this is used to create the final output format
    """
    silva_out = "{} {}\n{}\n".format(id, tax, seq)

    return silva_out


def format_ibol(to_format, formatted):
    """Formatting used by ibol
    """
    to_format.readline()  # removes header

    for line in to_format:
        splitline = line.rstrip().split("\t")

        tmp_id = splitline[0]
        id = ">{}".format(tmp_id)

        tmp_tax = splitline[8:15]
        tax = ";".join(filter(None, tmp_tax))

        tmp_seq = splitline[30]
        seq = "\n".join([tmp_seq[i:i+80] for i in range(0, len(tmp_seq), 80)])

        formatted.write(silva_format(id, tax, seq))


def format_unite(to_format, formatted):
    """Formatting used by ibol
    """
    base_tax = 'Eukaryota;Amorphea;Obazoa;Opisthokonta;Nucletmycea'
    tax = base_tax

    first_line = True

    for line in to_format:
        splitline = line.rstrip().split("|")

        if splitline[0][0] == '>':
            if not first_line:
                formatted.write(silva_format(id, tax, seq))
                tax = base_tax

            tmp_id = splitline[1]
            id = ">{}".format(tmp_id)
            for tmp_tax in splitline[4].split(";"):
                split_tax = tmp_tax.split("__")[1]
                tax += ";" + split_tax.replace('_', ' ').replace('sp', 'sp.')

            first_line = False

        tmp_seq = splitline[0]
        seq = "\n".join([tmp_seq[i:i+80] for i in range(0, len(tmp_seq), 80)])

    formatted.write(silva_format(id, tax, seq))


def sep_tax(fasta_file, tax_file):
    """Creates a combined fasta file containing taxonomies, ids and sequences
    using separate taxonomy and fasta files.
    """
    comb_file = "{}.combined".format(fasta_file)
    tax_dict = {}

    with open(tax_file, 'r') as f:
        for line in f:
            split_line = line.rstrip().split("\t")
            tax_dict[split_line[0]] = split_line[1]

    first_line = True
    tax = ''
    seq = ''
    id = ''
    with open(comb_file, 'w') as c_out, \
         open(fasta_file, 'r') as f_read:

        for line in f_read:
            if line[0] == '>':
                if not first_line:
                    c_out.write("{} {}\n{}".format(id, tax, seq))

                id = line.rstrip()
                tax = tax_dict[id]
                seq = ''
                first_line = False

            else:
                seq += line

        c_out.write("{} {}\n{}".format(id, tax, seq))

    return comb_file


def get_v_loop():
    """Returns list of all integers between 100-50, used as sequence identity
    for clustering. 100, 99, ..., 90, 85, ..., 50.
    """
    a_loop = [str(i) for i in range(100, 90-1, -1)]
    b_loop = [str(a) for a in range(85, 50-5, -5)]
    v_loop = a_loop + b_loop

    return v_loop


def sequence_quality_check(sequence, genetic_marker):
    """Used to quality check input sequences. Using genetic markers to
    determine min or max length of sequence to accept.
    """
    pass_checks = True

    sl = sequence_length_check(sequence, genetic_marker)

    """ Region check too strict to use outside E. coli, it is also very
    inefficient in its implementation making it unsustainable in use with
    large databases. Disabled for now
    """
    # sr = sequence_region_check(sequence, genetic_marker)
    sr = True

    if not sl or not sr:
        pass_checks = False

    return pass_checks


def genetic_region_found(sequence, ref_seq):
    """Loops through sequence to determine if reference sequence is found (with
    sequence similarity, default 70% bases needs to be found).
    """
    k = len(ref_seq)
    kmers = [sequence[i:i+k] for i in range(0, len(sequence)-k+1)]
    found = False

    for kmer in kmers:
        errors = 0
        for i in range(k):
            if ref_seq[i] != kmer[i]:
                errors += 1
        if float((k-errors)/k) >= 0.7:
            found = True
            break
    return found


def sequence_region_check(sequence, genetic_marker):
    """Main region sequence method, including the reference sequences used
    """
    seq = sequence.lower().replace('t', 'u')
    ref_seq_start = ""
    ref_seq_end = ""
    pass_checks = False

    if genetic_marker == "ssu":
        #: >X80721.1 E.coli rrnA gene
        ref_seq_start = """GTTTGATCATGGCTCAGATTGAACGCTGGCGGCAGGCCTAACACATGCAAGT
CGAACGGTAACAGGAAGAAGCTTGCTTCTTTGCTGACGAGTGGCGGAC"""
        ref_seq_end = """AGAATGCCACGGTGAATACGTTCCCGGGCCTTGTACACACCGCCCGTCACACCA
TGGGAGTGGGTTGCAAAAGAAGTAGGTAGCTTAACTTCGGGAGGGC"""

    cs = genetic_region_found(seq, ref_seq_start.lower().replace('t', 'u'))
    if cs:
        ce = genetic_region_found(seq, ref_seq_end.lower().replace('t', 'u'))
        if ce:
            pass_checks = True

    return pass_checks


def sequence_length_check(sequence, genetic_marker):
    """Does the min and max length checks, if sequence shorter or longer than
    allowed it returns False
    """
    cutoff_min = 0
    cutoff_max = 99999

    if genetic_marker == "ssu":
        cutoff_min = 1000
        cutoff_max = 3000

    if len(sequence) < cutoff_min or len(sequence) > cutoff_max:
        return False
    else:
        return True
