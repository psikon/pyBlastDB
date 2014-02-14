import sys, os
import subprocess
import shlex
import fileinput
from src.utils import check_type
from src.exceptions import BlastDBException, MultiFastaException, MetaCVException
from src.ftp_functions import ftp_functions

class DBCreation:
    
    BLAST_DB_OUT = ''
    METACV_DB_OUT = ''
    DOWNLOAD_FOLDER = ''
    BLAST_MF = ''
    METACV_MF = ''
    DB_TYPE = ''
    PARSE_SEQIDS = True
    METACV = False
    DEBUG = False
    
    def __init__(self, BLAST_DB_OUT, METACV_DB_OUT, DOWNLOAD_FOLDER, DB_TYPE, PARSE_SEQIDS,DEBUG):
        self.BLAST_DB_OUT = BLAST_DB_OUT
        self.METACV_DB_OUT = METACV_DB_OUT
        self.DOWNLOAD_FOLDER = DOWNLOAD_FOLDER
        self.BLAST_MF = DOWNLOAD_FOLDER + os.sep + 'blast.multi.fasta'
        self.METACV_MF = DOWNLOAD_FOLDER + os.sep + 'metacv.multi.fasta'
        self.PARSE_SEQIDS = True
        self.DEBUG = DEBUG
        
    def get_DB_TYPE(self):
        return self.DB_TYPE

    def set_DB_TYPE(self, db_type):
        self.DB_TYPE = db_type

    def get_local_index(self, subfolder, db_type):
        filelist = []
        for folder in subfolder:
            for dir, subdir, filename in os.walk(self.DOWNLOAD_FOLDER + os.sep + folder):
                for item in filename:
                    if str(item).endswith(check_type(db_type)):
                        filelist.append(dir + os.sep + item)
        if self.PARSE_SEQIDS or self.MetaCV:
            file_list = {}
            self.get_taxid_index()
            for item in filelist:
                with open(item, 'r') as f:
                    first_line = f.readline().split('|')[1]
                    if not first_line in set(file_list):
                        file_list[first_line] = item  
                    else:
                        if self.DEBUG: sys.stdout.write("Remove GI " + first_line + "\n")
            filelist = file_list.values()
        return filelist
    
    def get_taxid_index(self):
        gi_map_file = self.DOWNLOAD_FOLDER + os.sep + 'gi_taxid_prot.dmp'
        if os.path.exists(gi_map_file):
            gi_map = []
            with open(gi_map_file) as f:
                gi_map.append()
            sys.stderr.out("\nError: file %s not found" % (gi_map_file))
        print gi_map
    # generate a multi fasta file consisting of all single fasta
    # files downloaded by pyBlastDB
    def createBlast_MF(self, subfolder):
        if self.get_DB_TYPE() in ['nucl', 'both']:
            fasta_list = self.get_local_index(subfolder, 'nucl')
        else: 
            sys.stderr.write("\nError: for BlastDB sequences must be nucleotides!\n")
            sys.exit(1)
        
        try:
            sys.stdout.write("Create Input File ...\n")
            with open(self.BLAST_MF,'w') as fout:
                #update_progress(count)
                for line in fileinput.input(fasta_list):
                    fout.write(line)
            return self.BLAST_MF
        except:
            raise MultiFastaException()
            
    def createMetaCV_MF(self, subfolder):
        if self.get_DB_TYPE() in ['prot', 'both']:
            self.METACV = True
            fasta_list = self.get_local_index(subfolder, 'prot')
        else: 
            sys.stderr.write("\nError: for MetaCV DB, sequences must be protein sequences!\n")
            sys.exit(1)

        sys.stdout.write("Create Input File ...\n")
        # try:
        #     with open(self.METACV_MF,'w') as fout:
        #         #update_progress(count)
        #         for line in fileinput.input(fasta_list):
        #             fout.write(line)
        #     return self.METACV_MF
        # except:
        #     raise MultiFastaException()

    # wrapper function for makeblastdb
    def createBlastDB(self, name, output):
        subfolder = '.'
        self.set_DB_TYPE(db_type)
        multi_fasta = self.createBlast_MF()
        try: 
            sys.stdout.write("Create BlastDB ...\n")
            p = subprocess.Popen(shlex.split("%s -in %s -dbtype %s -input_type %s -title %s -out %s -parse_seqids" 
                                    % ('src/makeblastdb', multi_fasta, self.DB_TYPE, 'fasta', name, output + os.sep + name)),
                                    stdout=subprocess.PIPE)
            p.wait()
            sys.stdout.write("Creation of %s BlastDB successfull!\nDatabase Location: %s\n" % (self.DB_TYPE,
                                                                                               self.BLAST_DB_OUT + os.sep + name))
        except: 
            raise BlastDBException()

    def createMetaCVDB(self, db_type, name, DOWNLOAD_FOLDER):     
        # FTP Server URLs
        ncbiFTP = 'ftp.ncbi.nih.gov' 
        uniprotFTP = 'ftp.uniprot.org'
        # FTP Server directories
        taxonomy = '/pub/taxonomy/'
        functional = 'pub/databases/uniprot/current_release/knowledgebase/idmapping'
        ncbi_files = ['gi_taxid_prot.dmp.gz', 'taxdump.tar.gz']
        idmapping = 'idmapping.dat.gz'
        additional_files = []
        subfolder = ['Bacteria','Bacteria_DRAFT']

        self.set_DB_TYPE(db_type)
        ncbi = ftp_functions(ncbiFTP, taxonomy, DOWNLOAD_FOLDER, self.DEBUG)
        ncbi.connect()
        ncbi.go_down(taxonomy)
        for item in ncbi_files:
            if item in ncbi_files[0]:
                additional_files.append(ncbi.get_gi_map(item))
            else:
                [additional_files.append(x) for x in ncbi.get_taxdump(item)]
        ncbi.close()
        
        # uniprot = ftp_functions(uniprotFTP, functional, DOWNLOAD_FOLDER, self.DEBUG)
        # uniprot.connect()
        # uniprot.go_down(functional)
        # additional_files.append(uniprot.get_idmapping(idmapping))
        # uniprot.close()

        multi_fasta = self.createMetaCV_MF(subfolder)

        # try: 
        #     sys.stdout.write("Create MetaCV DB ...\n")
        #     os.chdir(self.METACV_DB_OUT)
        #     p = subprocess.Popen(shlex.split("%s formatdb %s %s %s" 
        #                                     % ('/home/psehnert/workspace/metpipe/ext/metacv/metacv',
        #                                        '../'+multi_fasta,
        #                                        ' '.join(map(str,additional_files)), 
        #                                        name)))
        #     p.wait()
        # except: 
        #     MetaCVException()

