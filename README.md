# User's Guide: Manual for MetaxaQR Database Builder

This guide contains explanations on how to install and use the MetaxaQR Database builder, version 0.2, as well as documentation of the major parts of the software. The software is written for Unix-like platforms.

MetaxaQR Database Builder automatically curates a database of genetic markers, such as 16S/18S small subunit rRNA gene, in FASTA format and outputs a dataset useable by MetaxaQR for taxonomic classification of metagenomic data.



## Contents of this manual:

1. Installation instructions
2. Usage and commands
3. Output files
4. Documentation: 'prepare'
5. Documentation: 'makedb'
6. Documentation: 'addseq'
7. License information



## 1. Installation instructions

Python version 3.7, or later, (https://www.python.org/) is required to run the MetaxaQR Database Builder.

Download and install VSEARCH version 2.15 or later (https://github.com/torognes/vsearch). VSEARCH is used to perform all clustering steps and is therefore required to use the MetaxaQR Database Builder.

Download the MetaxaQR Database Builder (https://github.com/Wettersten/metaxaqr-database-builder).

Testing the installation:
`python --version`
`vsearch --version`
`python metaxaqr-database-builder/mqr_db.py --version`



## 2. Usage and commands

MetaxaQR Database Builder accepts databases of genetic markers in FASTA formats, either as combined files (by default) or using `--taxonomy` to direct to a separate taxonomy file. By default the SILVA FASTA format is used but the format of the input database can be specified using `--format`, which supports the following formats: UNITE, iBol. Two steps are used in order to create the output MetaxaQR files; first the preparation step where the input file(s) are clustered `python mqr_db.py -p input_file --label label_name`, followed by `python mqr_db.py -m` which starts with a manual review of all dubious clusters followed by the creation of the output dataset.  To list all the available options for MetaxaQR Database Builder, type `python mqr_db.py --help`.

### Options

| Option                      | Description                                                                                                     |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------|
| -p {file}                   | Prepare - initial clustering and preparation of the input FASTA database                                        |
| --label {name}              | Labelling of the output files, required by '-p'                                                                 |
| --format {ibol, unite}      | Format of the input FASTA file                                                                                  |
| --taxfile {file}            | Separate taxonomy file                                                                                          |
| -m                          | Makedb - creates the MetaxaQR database from the prepared files, starting with manual review of flagged clusters |
| --qc                        | Disables quality checking; works in -p and -m                                                                   |
| --keep                      | Keeps all intermediate files                                                                                    |
| --exclude_all_flags         | Excludes all flagged clusters, skipping manual review                                                           |
| --a {file}                  | Addseq - adds new entries to a completed MetaxaQR database                                                      |
| --db {path}                 | Path to completed MetaxaQR database, required by '-a'                                                           |
| --ds                        | Temp text here                                                                                                  |
| --quiet                     | Disables status output                                                                                          |
| --license                   | Displays the license                                                                                            |
| --version                   | Displays the current version of the software                                                                    |
| -h                          | Displays the help message                                                                                       |


### Example usage

| Command                                       | Description                                                             |
|-----------------------------------------------|-------------------------------------------------------------------------|
| mqr_db.py -p database --label SSU             | Preparation step, using 'SSU' as a label                                |
| mqr_db.py -m --keep                           | Makes the MetaxaQR database, keeping all intermediate files             |
| mqr_db.py -a new_entries --db metaxaQR_db/    | Adds entries from new entry database to a finished MetaxaQR database    |



## 3. Output files

Output files are creating in the 'label_results' directory, for example 'SSU_results' if 'SSU' was used in `--label`. The default MetaxaQR database structure that is created by the MetaxaQR Database Builder consists of  the 'final_centroids', 'final_label_tree' and 'final_repr' files. Quality checks are on by default, and any entries or clusters removed in this process is recorded in the 'bad_hits', 'deleted_clusters_100',  'deleted_entries_100' and 'flag_exclusions' files.  

### MetaxaQR Database files

The structure of the database allows for the use of matching new unknown sequence entries against the database and retrieving predicted taxonomy for the entries. This is done by matching them against the reference 'final_centroid' file, if a new entry matches a cluster here at, for example, 94% identity, the matching cluster labels relation to other clusters is found in the 'final_label_tree' file, using the 94% cluster label here allows for the retrieval of its representative taxonomy from the 'final_repr' file.

#### final_centroids

This FASTA file contains all clusters found during the 100% sequence identity clustering, excluding those removed during the manual review step. The header for each entry is tab-delimited consisting of accession number, the cluster label and the taxonomy. All non-singleton clusters, those consisting of more than one entries, display the representative taxonomy created either during the taxonomy processing step or altered during the manual review. The sequence for the entry follows the header in normal FASTA fashion.

>\>BD359736.3.2150	MQR_100_0	Eukaryota;SAR;Alveolata;Apicomplexa;Aconoidasida;Haemosporoidia;Plasmodium;Plasmodium malariae

#### final_label_tree

This file is an index of each cluster at 100% sequence identity, showing what clusters these fall within when clustered at all other sequence identities, in descending order. Each line start with the 100% label followed by a tab then the descending labels separated by spaces. This allows for retrieval of what cluster a specific cluster belongs to at lower sequence identity.

> MQR_100_185	MQR_99_185 MQR_98_185 MQR_97_185 MQR_96_185 MQR_95_185 MQR_94_185 MQR_93_185 MQR_92_185 MQR_91_185 MQR_90_185 MQR_85_185 MQR_80_185 MQR_75_185 MQR_70_185 MQR_65_185 MQR_60_185 MQR_55_185 MQR_50_4

#### final_repr

This tab-delimited file is used as a reference index in order to retrieve the representative taxonomy from a cluster label. Each line is one cluster and these include the cluster label, the accession number of the centroid entry and the representative taxonomy,  starting with the clusters from the 100% sequence identity followed by descending order down to 50% sequence identity. All clusters from all sequence identities are included.

> MQR_100_0	>AF106036.1.3725	Eukaryota;Discoba;Discicristata;Euglenozoa;Euglenida;Aphagea;Distigma proteus

### Quality Check files

Certain quality checks can be disabled using `--qc`. If done using `-p` the 'deleted_entries_100' and 'deleted_clusters_100' files are affected, for `-m` the 'bad_hits' file is affected, while the files may still be created during the process they are not used in the creation of the MetaxaQR Database. For a detailed explanation refer to the documentation for these two steps. Entries that are excluded in the manual review step are recorded in the 'flag_exclusion' file.

#### bad_hits

Contains entries, at the 100% sequence identity level, that cluster together with too few other entries at lower identity levels, deemed by the quality check in `-m`.

> MQR_SSU_100_0

#### deleted_clusters_100

Contains clusters where all entries in that cluster are marked for removal.

> MQR_SSU_100_1278

#### deleted_entries_100

Contains all entries marked for removal, due to conflicting taxonomy, by the quality check in `-p`.

> \>AB742453.1.2271 Eukaryota;Archaeplastida;Chloroplastida;Chlorophyta;Chlorophyceae;Coelastrella sp. KGU-Y002

#### flag_exclusions

Contains all clusters that are excluded in the manual review step, either manually or by using `--exclude_all_flags`. The cluster label followed by the warning flags is used as a header. Then all entries in the cluster follows.

> MQR_SSU_100_10665	Mismatch	Origin, Mismatch, Excluded
> \>EU660574.1258.3158 Mitochondria;Archaeplastida;Chloroplastida;Charophyta;Phragmoplastophyta;Streptophyta;Embryophyta;Anthocerotophyta;Nothoceros aenigmaticus
> \>NC_012651.1_1 Eukaryota;Archaeplastida;Chloroplastida;Charophyta;Phragmoplastophyta;Streptophyta;Embryophyta;Anthocerotophyta;Megaceros aenigmaticus



## 4. Documentation: '-p', '--prepare'

'Prepare' creates initial directory structure, if any `--format` options are chosen the database is formatted before usage, clustering of the database at 100% sequence identity is done using VSEARCH, a tax_db file is created. Followed by taxonomic processing of all clusters created and warning flags applied to clusters that match any flagging conditions. All files are then prepared to for manual review and further clustering done in `-m`.

### Formatting

If `--format` is used the input database will be used to create a temporary formatted database, in the format of a SILVA database, that will be used for the creation of the MetaxaQR database. Allowed formats are the UNITE and the iBol formats.

### Clustering

Clustering is performed here at 100% sequence identity, using VSEARCH: `VSEARCH --cluster_fast input database --clusters mqr_db/clusters/cluster_ --uc mqr_db/100/uc --centroids mqr_db/100/centroids --id 1.0 --log mqr_db/vs_log.txt --no_progress --notrunclabels --quiet`.

### Taxonomic processing

After the clustering is complete, taxonomic processing is applied to all clusters that contain more than one entry. This is done in order to get a representative taxonomy for all multiple entry clusters, where more than one taxonomy can be present. The algorithm to get the representative taxonomy is done in several steps.

First the taxonomic rank containing the species is compared across the cluster, if the same species is present in all entries this is chosen as the representative taxonomy. If there is no exact match an algorithm is used which checks if there are more than 10 entries in the cluster and if the species in the most common entry occurs in at least 90% of the entries, if a match is found this is chosen as the representative taxonomy. If no match is found after the algorithm this process is run again using the species but removing the last word in the species information being compared, until only the genus name is left. If no match is found at the genus level the processing continues down to compare the taxonomy below species level.

The comparison of taxonomic ranks below the species level is done in a similar manner, starting at the lowest taxonomic rank e.g. the origin or the domain, comparing first exact matches across the cluster followed by algorithmic matches across the cluster. If a match is found at the taxonomic rank the process continues up to the next rank, if a match is not found the representative taxonomy chosen is the matching taxonomic ranks up to the rank where no match was found.

If no match is found in the taxonomic ranks below species level, e.g. in the first step - the origin, then the representative taxonomy is marked as "Mismatch".

### Flagging

Clusters are marked as flagged for manual review if the meet any of the following requirements:

* Mismatch - No matching taxonomy can be found in the cluster, marking the representative taxonomy for the cluster as "Mismatch".
* Origin - The cluster contains entries from more than one origin, e.g. archaea, bacteria, chloroplast, eukaryota, or mitochondria.

Flagging is only performed during the taxonomy processing step after the clustering at 100% sequence identity.

### Quality checks

In order to prevent the inclusion of entries with dubious taxonomy into the final database a filtering step exists, which can be turned off using `--qc`, where any entry with a taxonomy that differs too much from the "correct" taxonomy for that species is excluded from the database processing. In order to determine the "correct" taxonomy for species a 'tax_db' file of reference taxonomies is created, which contains all unique taxonomy entries from the input database containing species level information. The species rank is stripped to only contain the genus then all taxonomies with the same genus are compared in order to determine the "correct" taxonomy for that genus. This is decided by matching the following criteria: if possible the genus should be the last taxonomic rank before the species level information and the entry should have the greatest amount of taxonomic ranks.

Comparisons of all entries, containing species level information, are made against this 'tax_db', using the genus as index, if the genus exists in the 'tax_db'. If at least 80% of the taxonomic ranks in the entry being compared matches those of the reference taxonomy the reference taxonomy will be used, but with the species level information from the compared entry. If the entry is too different from the reference it will be excluded, and saved to the 'deleted_entries_100' file.



## 5. Documentation: '-m','--makedb'

'Makedb' start with a manual review of any flagged clusters, after which files are prepared for further clustering using the corrected taxonomies from the manual review. A loop of clustering followed by preparation for further clustering is then repeated, done by descending sequence identity % in steps of 1% between 100-90% and then in steps of 5% between 90-50%. After the loop is completed the MetaxaQR database files are created using the output.

### Manual review

Manual review is performed at the start of `-m` if any clusters are flagged during taxonomic processing. Here the user is presented with all flagged clusters, one at a time, and given options how the representative taxonomy should be for that cluster. Each cluster is presented with the flag(s), the cluster id, all the entries in the cluster, their index in the cluster and the corresponding taxonomies, as well as the suggested representative taxonomy for the cluster. Following options to process the cluster are available:

* `accept`: Accepts the suggested representative taxonomies for clusters. Using `accept` will prompt the user to accept the suggested representative taxonomy for the current cluster. Accepting all clusters with a specific flag can be done using `accept flagname` and accepting the suggested taxonomy for all flagged clusters can be done using `accept all`.
* `exclude`: Excludes the cluster from further processing and the cluster will not appear in the final MetaxaQR database. Using `exclude` will prompt the user to exclude the current cluster. Excluding all clusters with a specific flag can be done using `exclude flagname` and excluding all flagged clusters can be done using `exclude all`.
* `exit`: Exits the manual review.
* `flags`: Shows all flag names as well as how many in total of each are in the manual review and how many are left of each to process.
* `keep`: Keep takes the taxonomy from a specified entry in the cluster, by index, and uses its taxonomy, keep can additionally also be used to prune the taxonomy to remove taxonomic either ranks or words in the species level taxonomic rank. Using the taxonomy of entry in index 5 but removing the 1 highest taxonomic ranks (species, genus): `keep 5 c-2`. Using the same entry but instead removing the last word in the taxonomy (strain information): `keep 5 s-1`.
* `manual`: Allows manual input from the user of a taxonomy to use for the cluster.
* `remove`: Removes entries from a cluster in order to calculate a new representative taxonomy using all entries which were not removed. Removing a single entry is done using `remove 5`, removal of several entries is done using `remove 5 7-10 15`, which removes the entries at index 5, 7, 8, 9, 10 and 15.

The manual review step can also be skipped using `--exclude_all_flags` which auto excludes all clusters which are flagged.

### Clustering loop

After manual review is completed a loop of processing output files and then using them for further clustering is done, at sequence identity below 100% 'tree_label' files are created which contain all cluster labels and how they relate to each other, in lower sequence identity these labels contain the full tree up to 100% sequence identity label. At every step 'final_repr' files are created containing all clusters (singletons and those with multiple entries) with their respective representative taxonomy.

### Creation of the MetaxaQR database

The MetaxaQR database files are created using intermediary files, all representative taxonomy files are combined to create the 'final_repr' file. The 'final_label_tree' is created using all 100% sequence identity labels in the 'label_tree' from the 50% sequence identity cluster and finally the 'final_centroids' file is the 'final_centroid' file created during the 100% sequence identity cluster.



## 6. Documentation: '-a', '--addseq'

'Addseq' adds new entries to a finished MetaxaQR database, using the VSEARCH 'search' function. This compares the sequences from the new entries against the clustered output of the MetaxaQR database at 100% sequence identity level. If a match is found the matching % is used to retrieve taxonomy information for the match at all lower sequence identities, keeping the taxonomy of the new entry for the matching % and up, all new matches are then added to the MetaxaQR database files. For example: new_entry matches old_entry at 94% identity, the taxonomy from the new_entry is used at 95-100%, the taxonomy for the old_entry at identities 50-94% is used, new labels are created for the higher identities and these are combined to update the MetaxaQR database files.



## 7. License information

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program, in the file named 'LICENSE'. If not, see <https://www.gnu.org/licenses/>.

Copyright (C) 2020-2021 Sebastian Wettersten
