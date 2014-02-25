# pyBlastDB

`pyBlastDB` is a tiny little program to automatically download complete directory trees from [NCBI ftp server](ftp://ftp.ncbi.nih.gov/genomes/) and generate a suitable blast database from the downloaded content. It is capable to generate nucleotide and protein blast databases from `fasta` content. Other file formats will not be provided at the moment.  

Also `pyBlastDB` can generate an actual database for [MetaCV](http://metacv.sourceforge.net/), based on actual protein datasets on NCBI file server. 

### Requirements

* python >= 2.7
* ncbi blast+ >= 2.2.27
* MetaCV >= 2.2.9

### Usage
```
python pyBlastDB.py [-h] [--version] [-type {nucl,prot}] [-metacv] [-exe EXE]
                    -name NAME [-parse_seqids]

  -h, --help         show this help message and exit
  --version          show program's version number and exit
  -type {nucl,prot}  set type of blastdb
  -metacv            create metacv database
  -exe EXE           if not installed, specify path to executable of
                     'makeblastdb' or 'metacv'
  -name NAME         outname for the databases
  -parse_seqids      Remove duplicated GI numbers from downloaded files and
                     run "makeblastdb" with -parse_seqids statement
```

### Examples

Download nucleotide datasets from [NCBI ftp server](ftp://ftp.ncbi.nih.gov/genomes/) and create a nucleotide blast database.
```bash
python pyBlastDB.py -type nucl -name bacterial -parse_seqids
```

Download protein datasets from [NCBI ftp server](ftp://ftp.ncbi.nih.gov/genomes/) and create a MetaCV database (without functional annotation).
```bash
python pyBlastDB.py -metacv -name bacterial
```

### Adjust download Parameters

In the main script `pyBlastDB.py` following values can be adjusted to fit change the downloadable content. The variables for FTP sources can be customized for personal use. Over the _sources_ list the selection for the database creation can be adjusted. 

```python
# FTP Sources
FTP_SERVER = 'ftp.ncbi.nih.gov' 
FTP_ROOT = 'genomes/'
BACTERIA = 'Bacteria'
BACTERIA_DRAFT = 'Bacteria_DRAFT'
PLASMIDS = 'Plasmids/'
VIRUSES = 'Viruses/'
FUNGI = 'Fungi/'
FUNGI_DRAFT = 'Fungi_DRAFT/'
HUMAN_BICROBIOM = 'HUMAN_MICROBIOM/Bacteria/'

# location for downloaded content
DOWNLOAD_FOLDER =  'sources'
# location of output db
DB_OUT = 'db_out'

# SELECT sources for database creation
SOURCES = [BACTERIA, BACTERIA_DRAFT, PLASMIDS, VIRUSES, FUNGI, FUNGI_DRAFT]
```



