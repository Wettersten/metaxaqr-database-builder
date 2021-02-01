# MetaxaQR Database Builder

Takes a database of sequences in FASTA format, comprised of taxonomic information coupled with sequences of a genetic marker, these are clustered together in order to build a database for MetaxaQR.



## Dependencies

- VSEARCH 2.15.0 (conda install -c bioconda vsearch)
- pathlib (?) (conda install -c menpo pathlib)

Text here explaining packages needed



## "Help" output


python mqr_db.py -h
usage: mqr_db [-h] [-c] [-i] [-o] [-r] [-f] [-m] [-q] [--version]

Analyse taxonomy within clusters based on sequence identity.

optional arguments:

- -h, --help      show this help message and exit
- -c, --cluster   Clustering of input database at 100% identity and preparation of files for manual review
- -i , --input    {FILENAME} FASTA database to be clustered
- -o , --output   {PATH} Specify output path, path/mqr_db/...
- -r, --review    Manual review of flagged clusters
- -f, --finalize  Further clustering of their output centroid files from manual review down to 95% identity
- -m, --makedb    Creates a MetaxaQR databse from the created files
- -q, --quiet     No status print out, only writing to log file
- --version       show program's version number and exit


Examples:



## Running

python mqr_db.py -c -i silva_trunc_database.FASTA

python mqr_db.py -r

python mqr_db.py -f



## Program Documentation

### General Information

A full run of SILVA truncated database (2.4M sequences) from start to finish is around 10 hours. Most (8 hours) is spent in the first full (100% sequence identity) clustering phase using VSEARCH. Subsequent clustering is faster for every step down to the last step of 50% sequence identity.

### Structure

mqr_db.py

src/
	init.py

src/mqr_db/
	init.py
	cluster_loop.py
	cluster_tax.py
	clustering.py
	handling.py
	mc_run.py
	parsing.py

### Documentation

#### meta_clustering.py

Main module, executing the program when used.

1. Creates the argparse parse and retrieves the input arguments from user
2. Error checking which checks if correct arguments are input, if the files are valid and if all dependencies are installed.
3. Arguments are used to run main_mc.

#### cluster_loop.py

Module containing a loop which handles all clustering down from 99% to 50% sequence identity, creating required files along the way.

#### cluster_tax.py

Module containing the main bulk of functions needed to create cluster_tax taxonomy files, calculate representative taxonomy as well as reviewal of flagged taxonomies.

#### clustering.py

Module containing the function used to cluster with VSEARCH.

#### handling.py

Module containing error checks, the project path, logging etc.

#### mc_run.py

Module containing the main method used to execute all code called from meta_clustering.py. Here various functions are called in order depending on which arguments are used.

#### parsing.py

Module handling all parsing using argparse.
