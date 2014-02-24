# pyBlastDB

### Description

### Requirements

* python >= 2.7
* ncbi blast+ >= 2.2.27
* MetaCV >= 2.2.9

### Usage
```bash
python pyBlastDB.py [-h] [--version] [-type {nucl,prot}] [-metacv] [-exe EXE]
                    -name NAME [-parse_seqids] [-clean]

pyBlastDB.py -- create actual bacteria databases from NCBI Sources

optional arguments:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  -type {nucl,prot}  set type of blastdb
  -metacv            create metacv database
  -exe EXE           if not installed, specify path to executable of
                     'makeblastdb' or 'metacv'
  -name NAME         outname for the databases
  -parse_seqids      Remove duplicated GI numbers from downloaded files and
                     run "makeblastdb" with -parse_seqids statement
  -clean             Delete downloaded and created files after database
                     creation? [default: False]
```


