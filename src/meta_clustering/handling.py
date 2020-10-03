import time
import os
import pathlib


def create_dir_structure(str_id):
    """Creates the directory structure used by clustering and subsequent
    handling of clusters. Cluster files in mc_db/identity/clusters/
    """
    cluster_dir = return_proj_path() + str_id + '/clusters/'
    pathlib.Path(cluster_dir).mkdir(parents=True, exist_ok=True)


def return_proj_path():
    """Returns the path to current path, appending identity will return path to
    clustering files.
    """
    #: fix to use input path? TODO
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


def check_id_range(identity):
    """Checks if valid input in identity arg.
    """
    id_range = str(identity).split("-")
    error_msg = "Error in identity range input."

    try:
        (isinstance(float(id_range[0]), float))
    except ValueError:
        quit(error_msg)

    if len(id_range) > 1:
        if float(id_range[0]) >= float(id_range[1]):
            quit(error_msg)


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
    logging_file = os.getcwd() + 'mc_log.txt'

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
        elif int(str_id) > 95:
            log_msg = "{txt1}: {id1} {txt2}: {id2}\n".format(
                    txt1="Finalizing id",
                    id1=str_id,
                    txt2="and running VSEARCH at id",
                    id2=str(int(str_id)-1)
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
