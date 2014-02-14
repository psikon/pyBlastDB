#!/usr/bin/env python

#@author: Philipp Sehnert
#@contact: philipp.sehnert[a]gmail.com

# IMPORTS
import sys, os
from argparse import ArgumentParser
from shutil import rmtree
from src import ftp_functions
from src.ftp_functions import ftp_functions
from src.utils import create_folder
from src.db_creation import DBCreation

# GLOBAL VARIABLES
DB_OUT = ''
DB_TYPE = ''
DB_NAME = ''
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

# Local File Structure
DOWNLOAD_FOLDER =  'test'
ROOT_DIR = os.getcwd() + os.sep + DOWNLOAD_FOLDER
BLAST_DB_OUT = 'blast_db'
METACV_DB_OUT = 'metacv_db'

# SELECT Sources for Databases
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
    parser.add_argument('-t', "--type",dest = "type", required = True, 
                        default = 'both', choices = {'nucl','prot','both'},  
                        help = "set the type of database")
    parser.add_argument('--db', dest = 'database', choices = {'blast','metacv','both'},
                        default = 'both', help = 'what kind of database will be created', 
                        required = True)
    parser.add_argument('-o','--out', dest = 'name', default = 'bacterial', required = True,
                        help = 'outname for the databases')
    parser.add_argument('--parse_seqids',dest= 'parse_seqids', action='store_false', default= True,
                        help = 'Remove duplicated GI numbers from downloaded files and run "makeblastdb" with -parse_seqids statement ')
    parser.add_argument('--clean', dest = 'clean', action = 'store_true', default = False, 
                        help = 'Delete downloaded and created files after database creation? [default: False]')
    # Process arguments
    args = parser.parse_args()
    DB_TYPE = args.type
    DB_OUT = args.database
    DB_NAME = args.name  
    CLEAN = args.clean
    PARSE_SEQIDS = args.parse_seqids
    
    if  __name__ ==  '__main__':
        
        # create dir for sources
        create_folder(DOWNLOAD_FOLDER)
        # init FTP functions
        ftp = ftp_functions(FTP_SERVER, FTP_ROOT, DOWNLOAD_FOLDER, DEBUG)
        # connect to Blast FTP Server 
        ftp.connect()
        ftp.go_to_root()
       
        #start Downloading
        # for ftp_folder in SOURCES:
        #     sys.stdout.write("Downloading files from %s \n" % (ftp_folder))
        #     ftp.download_folder(ftp_folder, DB_TYPE)
        # close ftp connection
        ftp.close()
        #run external database creation scripts
        DBCreate = DBCreation(BLAST_DB_OUT, METACV_DB_OUT, DOWNLOAD_FOLDER, DB_TYPE, PARSE_SEQIDS, DEBUG)
        if DB_OUT in 'blast' or DB_OUT in 'both':
            DBCreate.createBlastDB(DB_NAME, BLAST_DB_OUT)
        elif DB_OUT in 'metacv' or DB_OUT in 'both':           
            create_folder(METACV_DB_OUT)
            DBCreate.createMetaCVDB(DB_TYPE, DB_NAME, DOWNLOAD_FOLDER)
        else:
            sys.stderr.write("Error: No database created!\nPlease check --db argument ")
       
        if CLEAN:
            sys.stdout.write('Remove temporary files ...\n')
            try: 
                shutil.rmtree(DOWNLOAD_DIR, True)
            except: 
                sys.stderr.write("Error: Clean up failed!\n")        
  
sys.exit(main())

