import sys, os
import subprocess
import shlex
import fileinput
from src.utils import check_type, create_folder, whereis
from src.exceptions import BlastDBException, MultiFastaException, MetaCVException
from src.ftp_functions import ftp_functions

class DBCreation:
    '''class for database creation functionalities - contains functions to generate multifasta 
    files from downloaded content and run external scripts from the software suits blast and 
    metacv for creation of the databases'''

    DB_OUT = None
    DOWNLOAD_FOLDER = None
    BLAST_MF = None
    METACV_MF = None
    DB_TYPE = None
    PARSE_SEQIDS = True
    METACV = False
    DEBUG = False
    EXECUTABLE = None
    
    def __init__(self, DB_OUT, DOWNLOAD_FOLDER, DB_TYPE, PARSE_SEQIDS, DEBUG, EXECUTABLE):
        self.DB_OUT = DB_OUT
        self.DOWNLOAD_FOLDER = DOWNLOAD_FOLDER
        self.DB_TYPE = DB_TYPE
        self.BLAST_MF = DOWNLOAD_FOLDER + os.sep + 'blast.multi.fasta'
        self.METACV_MF = DOWNLOAD_FOLDER + os.sep + 'metacv.multi.fasta'
        self.PARSE_SEQIDS = True
        self.EXECUTABLE = EXECUTABLE
        self.DEBUG = DEBUG

    def set_METACV(self, var):
        self.METACV = var

    def get_METACV(self):
        return self.METACV

    def get_local_index(self, subfolder):
        '''generate an index of all local files needed for multifasta creation'''
        filelist = []
        # generate a list of all files contained in selected folders 
        for folder in subfolder:
            for dir, subdir, filename in os.walk(self.DOWNLOAD_FOLDER + os.sep + folder):
                for item in filename:
                    if str(item).endswith(check_type(self.DB_TYPE)):
                        filelist.append(dir + os.sep + item)
        # check the found files for duplicated GI Numbers                
        if self.PARSE_SEQIDS or self.METACV:
            file_list = {}
            #self.get_taxid_index()
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
        ''' generate a multifasta file from downloaded content, that will be input
        file for the external database creation scripts'''
        
        # get a list of all suitable input files
        fasta_list = self.get_local_index(subfolder)
        try:
            sys.stdout.write("Create Input File ...\n")
            # open the multifasta file
            with open(self.BLAST_MF,'w') as fout:
                # open every file in fasta_list and write the content to multifasta file
                for line in fileinput.input(fasta_list):
                    fout.write(line)
                    # return file location
            return self.BLAST_MF
        except:
            raise MultiFastaException()
           
    def createMetaCV_MF(self, subfolder):
        # get a list of all suitable input files
        fasta_list = self.get_local_index(subfolder)
        
        # try:
        #      sys.stdout.write("Create Input File ...\n")
        #     with open(self.METACV_MF,'w') as fout:
        #         #update_progress(count)
        #         for line in fileinput.input(fasta_list):
        #             fout.write(line)
        #     return self.METACV_MF
        # except:
        #     raise MultiFastaException()

    def get_parse_seqids_stmt(self):
        ''' test for parse_seqids argument and return the correct stmt'''
        if self.PARSE_SEQIDS:
            return '-parse_seqids'
        else:
            return None

    def createBlastDB(self, name):
        ''' wrapper for 'makeblastdb' script of the blast software suit'''
        # create output folder
        create_folder(self.DB_OUT)
        # select all downloaded folders as input for multifasta file creation
        subfolder = '.'
        # create multifasta file as input for 'makeblastdb'
        multi_fasta = self.createBlast_MF(subfolder)
        try: 
            sys.stdout.write("Create BlastDB ...\n")
            # run 'makeblastdb'
            p = subprocess.Popen(shlex.split("%s -in %s -dbtype %s -input_type %s -title %s -out %s %s" 
                                    % (self.EXECUTABLE, 
                                        multi_fasta, 
                                        self.DB_TYPE, 
                                        'fasta', 
                                        name, 
                                        self.DB_OUT + os.sep + name, 
                                        self.get_parse_seqids_stmt())),
                                    stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            p.wait()
            # print statistics 
            sys.stdout.write("Creation of %s BlastDB successfull!%s\nDatabase Location: %s\n" % 
                (self.DB_TYPE, p.stdout.read(), self.DB_OUT + os.sep + name))
        except: 
            raise BlastDBException()

    def createMetaCVDB(self, name):     
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

        ncbi = ftp_functions(ncbiFTP, taxonomy, self.DOWNLOAD_FOLDER, self.DEBUG)
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
        create_folder(self.DB_OUT)
        multi_fasta = self.createMetaCV_MF(subfolder)

        # try: 
        #     sys.stdout.write("Create MetaCV DB ...\n")
        #     os.chdir(self.METACV_DB_OUT)
        #     p = subprocess.Popen(shlex.split("%s formatdb %s %s %s" 
        #                                     % ('self.EXECUTABLE,
        #                                        '../'+multi_fasta,
        #                                        ' '.join(map(str,additional_files)), 
        #                                        name)))
        #     p.wait()
        # except: 
        #     MetaCVException()

