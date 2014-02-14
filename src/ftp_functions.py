import sys, os, tarfile
from ftplib import FTP
from src.utils import *
from src.exceptions import ConnectionException, FtpPathException, FtpIndexException, FtpDownloadException

class ftp_functions:
    '''provide all needed functions for interacting with the ftp backend'''
    
    FTP_SERVER = ''
    FTP_ROOT = ''
    CONNECTION = ''
    UP = "../"
    DOWNLOAD_FOLDER = ''
    DEBUG = False
    
    def __init__(self, FTP_SERVER, FTP_ROOT, DOWNLOAD_FOLDER, DEBUG):
        self.FTP_SERVER = FTP_SERVER
        self.FTP_ROOT = FTP_ROOT
        self.DOWNLOAD_FOLDER = DOWNLOAD_FOLDER
        self.DEBUG = DEBUG
        
    def get_connection(self):
        return self.CONNECTION   
    
    def set_connection(self, connection):
        self.CONNECTION = connection

    def connect(self):
        '''wrapper to open connection as anonymus user on a FTP server'''
        try: 
            ftp = FTP(self.FTP_SERVER)
            ftp.login()
            sys.stdout.write("CONNECTED TO %s \n" % (self.FTP_SERVER))
            self.set_connection(ftp)
        except:
            raise ConnectionException(self.FTP_SERVER)
    
    def go_to_root(self):
        '''navigate to the starting point on ftp server site '''
        try: 
            self.get_connection().cwd(self.FTP_ROOT)
            # only for debug mode
            if self.DEBUG: sys.stdout.write("\nloc: "+ self.get_connection().pwd() + "\n")
        except:
            raise FtpPathException(self.FTP_ROOT)
    
    def go_down(self, folder):
        '''move to specific folder on ftp site'''
        try:
            self.get_connection().cwd(folder)
            # only for debug mode
            if self.DEBUG: sys.stdout.write("\nloc: "+ self.get_connection().pwd() + "\n")
        except:
            raise FtpPathException(folder)

    def go_up(self):
        '''move one level up in ftp file tree'''
        try:
            self.get_connection().cwd(self.UP)
            # only for debug mode
            if self.DEBUG: sys.stdout.write("\nloc: "+ self.get_connection().pwd() + "\n")
        except:
            raise FtpPathException(self.UP)
    
    def ls(self):
        '''wrapper to get a list of all items on current file level'''
        return self.get_connection().nlst() 
    
    def close(self):
        self.get_connection().close()
        
    # generate index of ftp folders
    def get_folder_index(self, folder):
        '''generate a list of all subfolders (without single files)'''
        dirs = []
        try: 
            sys.stdout.write("Identify folders for Downloading ... \n")
            self.get_connection().dir("", dirs.append)
            dirs = [x.split()[-1] for x in dirs if x.startswith("d")]
            sys.stdout.write("Found %d folders\n" % (len(dirs)))
            return dirs if self.DEBUG is False else dirs[:10]
        except: 
            raise FtpIndexException(self.FTP_ROOT)
    
    def get_file_index(self, db_type):
        '''generate a list of all files matching "nucl" or "prot" conditions'''
        return select_files(self.ls(), db_type)
    
    def is_actual(self, local, remote,):
        '''determine if local timestamp is newer or equal to remote timestamp'''
        return True if get_local_timestamp(local + os.sep + remote) >= get_remote_timestamp(remote, self.get_connection()) else False

    # download a folder with all subfolder from ftp source    
    def download_folder(self, remote_folder, db_type):
        '''download a folder with all subfolders and matching files from ftp site'''
        local = self.DOWNLOAD_FOLDER + os.sep + remote_folder
        # go to remote dir
        self.go_down(remote_folder)
        # get list of subfolder
        folder_list = self.get_folder_index(remote_folder)
        # only for cmd output 
        downloaded = actual = all = 0
        # init progressbar
        total = float(len(folder_list))
        count = float(downloaded + actual)
        update_progress(count)
    
        # loop over folder in remote_dir
        for item in folder_list:
            # create local folder
            local_folder = local + os.sep + item
            create_folder(local_folder)
            # go down in ftp file structure and get a list of matching files
            self.go_down(item)            
            file_list = self.get_file_index(db_type)
            # update cmd values
            all += len(file_list)
            # update progressbar
            count += float(1 / total)
            update_progress(count)
            # loop over files
            for x in file_list:
                # test timstamps
                if not self.is_actual(local_folder, x):
                    self.download_file(local_folder, x)
                    downloaded += 1
                else:
                    actual += 1    
            # go up file structure
            self.go_up()
        # write status information to stdout
        sys.stdout.write("\nDownloaded: %d Actual: %d Total: %d \n\n" % 
                        (downloaded, actual, all))
        # go up in file structure to root dir
        self.go_up()

        
    def download_file(self, local_folder, item):
        '''download and extract a single file from ftp source'''
        # specify save location
        local_file = local_folder + os.sep + item
        try: 
            # open local file stream
            f = open(local_file, "wb")
            # copy remote stream to local stream
            self.get_connection().retrbinary("RETR " + item, f.write)
            f.close()
        except: 
            raise FtpDownloadException(item)
        # check endings of files for typical compressing endings   
        if is_compressed(local_file):
            # extract *.tgz files
            if is_tgz(local_file):
                extract_tar(local_file, local_folder)
            # unpack gunzip files and ignore *.tar.gz (because of metacv db creation)
            elif is_gz(local_file):
                extract_gz(local_file)
        else: 
            pass

    def get_gi_map(self, gi_map):
        '''download gi_taxid_prot.dmp.gz from ncbi server and extract the complete file'''
        local_version = self.DOWNLOAD_FOLDER + os.sep + gi_map
        # test for actual or existing file
        if not os.path.exists(local_version) or not self.is_actual(self.DOWNLOAD_FOLDER, gi_map):
            try:
                sys.stdout.write("Download %s from %s ...\n" % (gi_map, self.FTP_SERVER))
                # download file
                f = open(local_version, "wb")
                self.get_connection().retrbinary("RETR " + gi_map, f.write)
                f.close()
            except:
                raise FtpDownloadException(gi_map)
        else:
            sys.stderr.write('\n%s is actual!\n' % (gi_map))

        # extract file, if no extracted content exists
        if not os.path.exists(str.strip(local_version,'.gz')):
            extract_gz(local_version, self.DOWNLOAD_FOLDER)
        return os.path.abspath(str.strip(local_version,'.gz'))
        
    
    def get_taxdump(self, taxdump):
        '''download taxdump.tar.gz from ncbi server and extract needed files'''
        local_taxdump = self.DOWNLOAD_FOLDER + os.sep + taxdump
        # test for actual or existing file
        if not os.path.exists(local_taxdump) or not self.is_actual(self.DOWNLOAD_FOLDER, taxdump):
            try:
                sys.stdout.write("Download %s from %s ...\n" % (taxdump, self.FTP_SERVER))
                # download file
                f = open(local_taxdump, "wb")
                self.get_connection().retrbinary("RETR " + taxdump, f.write)
                f.close()
            except:
                raise FtpDownloadException(taxdump)
        else:
            sys.stderr.write('\n%s is actual!\n' % (taxdump))
        # extract parts of files , if no extracted content exists
        if not os.path.exists(self.DOWNLOAD_FOLDER +  os.sep + 'names.dmp'):
            try: 
                with tarfile.open(local_taxdump) as tar:
                    # extract only names.dmp and nodes.dmp from taxdump
                    for tarinfo in tar:
                        if tarinfo.name in 'names.dmp':
                            tar.extract(tarinfo, self.DOWNLOAD_FOLDER)
                        if tarinfo.name in 'nodes.dmp':
                            tar.extract(tarinfo, self.DOWNLOAD_FOLDER)
                    tar.close()
            except:
                raise ExtractionException(taxdump)
        return [os.path.abspath(self.DOWNLOAD_FOLDER + os.sep + 'names.dmp'), 
                os.path.abspath(self.DOWNLOAD_FOLDER + os.sep + 'nodes.dmp')]
    
    def get_idmapping(self, idmapping):
        '''download idmapping.dat.gz from uniprot server and extract the complete file'''
        local_idmapping = self.DOWNLOAD_FOLDER + os.sep + idmapping
        # test for actual or existing file
        if not os.path.exists(local_idmapping) or not self.is_actual(self.DOWNLOAD_FOLDER, idmapping):
            try:
                sys.stdout.write("Download %s from %s ...\n" % (idmapping, self.FTP_SERVER))
                # download file
                f = open(local_idmapping, "wb")
                self.get_connection().retrbinary("RETR " + idmapping, f.write)
                f.close()
            except:
                raise FtpDownloadException(idmapping)
        else:
            sys.stderr.write('\n%s is actual!\n' % (idmapping))

        # extract file, if no extracted content exists
        if not os.path.exists(str.strip(local_idmapping,'.gz')):
            try:
                extract_gz(local_idmapping, self.DOWNLOAD_FOLDER)
            except:
                raise ExtractionException(idmapping)
        return os.path.abspath(str.strip(local_idmapping,'.gz')) 
