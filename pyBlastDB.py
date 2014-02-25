#!/usr/bin/env python

#@author: Philipp Sehnert
#@contact: philipp.sehnert[a]gmail.com

# IMPORTS
import sys, os
from argparse import ArgumentParser
from src.ftp_functions import ftp_functions
from src.utils import create_folder, check_db_type, check_executable
from src.db_creation import DBCreation

# GLOBAL VARIABLES
DB_OUT = None
DB_TYPE = None
DB_NAME = None
PARSE_SEQIDS = True
CLEAN = False

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
DOWNLOAD_FOLDER = 'sources'
# location of output db
DB_OUT = 'db_out'
ROOT_DIR = os.getcwd() + os.sep + DOWNLOAD_FOLDER

# SELECT sources for database creation
SOURCES = [BACTERIA, BACTERIA_DRAFT, PLASMIDS, VIRUSES, FUNGI, FUNGI_DRAFT]

# DEBUG
DEBUG = False
    
def main(argv = None):

    # Setup argument parser
    parser = ArgumentParser(description = '%s -- create actual bacteria databases from NCBI Sources' % 
                            (os.path.basename(sys.argv[0])),
                            epilog = 'created by Philipp Sehnert',
                            add_help = True)
    parser.add_argument('--version', action = 'version', version = '%s 1.0' % 
                        (os.path.basename(sys.argv[0])))
    parser.add_argument("-type", dest = "type", default = 'nucl', 
                        choices = {'nucl','prot'},  help = "set type of blastdb")
    parser.add_argument('-metacv', dest = 'metacv', action = 'store_true',
                        default = False, help = 'create metacv database')
    parser.add_argument('-exe', dest = 'exe', 
                        help = "if not installed, specify path to executable of 'makeblastdb' or 'metacv'")
    parser.add_argument('-name', dest = 'name', default = 'bacterial', required = True,
                        help = 'outname for the databases')
    parser.add_argument('-parse_seqids', dest = 'parse_seqids', action = 'store_false', default = True,
                        help = 'Remove duplicated GI numbers from downloaded files and run "makeblastdb" with -parse_seqids statement ')
    # Process arguments
    args = parser.parse_args()
    DB_TYPE = args.type
    METACV = args.metacv
    DB_NAME = args.name  
    EXECUTABLE = args.exe
    PARSE_SEQIDS = args.parse_seqids
    
    if __name__ == '__main__':
        # check for protein or nucleotide database
        DB_TYPE = check_db_type(METACV, DB_TYPE)
        # verify executable for external scripts
        EXECUTABLE = check_executable(EXECUTABLE, METACV)
        # create dir for sources
        create_folder(DOWNLOAD_FOLDER)
        # init FTP functions
        ftp = ftp_functions(FTP_SERVER, FTP_ROOT, DOWNLOAD_FOLDER, DEBUG)
        # connect to Blast FTP Server 
        ftp.connect()
        ftp.go_to_root()
        # start Downloading
        for ftp_folder in SOURCES:
            sys.stdout.write("Downloading files from %s \n" % (ftp_folder))
            ftp.download_folder(ftp_folder, DB_TYPE)
        # close ftp connection
        ftp.close()
        # run external database creation scripts
        DBCreate = DBCreation(DB_OUT, DOWNLOAD_FOLDER, DB_TYPE, PARSE_SEQIDS, DEBUG, EXECUTABLE)
        if METACV:
            DBCreate.set_METACV(True)
            # select the subfolder for MetaCV database
            DBCreate.createMetaCVDB(DB_NAME, ['Bacteria', 'Bacteria_DRAFT'])
        else:
            DBCreate.set_METACV(False)
            DBCreate.createBlastDB(DB_NAME)     
  
sys.exit(main())

