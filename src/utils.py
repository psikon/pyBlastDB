import sys, os, tarfile, gzip
from datetime import datetime
from src.exceptions import ExtractionException, PathException

def check_type(var):
    '''check needed type of file for database creation'''
    return 'fna' if var in 'nucl' else 'faa'


def check_db_type(METACV, db_type):
    '''check type of database'''
    return 'prot' if METACV else db_type
        

def is_compressed(filename):
    '''check if file is compressed'''
    return True if filename.endswith('gz') else False

def extract_tar(item, path):
    '''extract all items from .tgz compressed files'''
    try: 
        tar = tarfile.open(item)
        tar.extractall(path)
        tar.close()
    except:
        raise ExtractionException(item)

def extract_gz(item, path):
    '''extract all items from .gz compressed files'''
    try: 
        local = open('.'.join(item.split('.')[0:len(item.split('.'))-1]), 'wb')
        z = gzip.open(item,'r')
        local.write(z.read())
        z.close()
        local.close()  
    except: 
        raise ExtractionException(item)
        
def create_folder(directory):
    '''create a folder if not existing'''
    if not os.path.exists(directory):
        os.makedirs(directory)

def select_files(file_list, db_type):
    '''select from a list of files all files matching "db_type"'''
    pattern = check_type(db_type)
    matchedFiles = []
    for filename in file_list:
        if pattern in filename:
            matchedFiles.append(filename)
    return matchedFiles

def update_progress(progress):
    '''create and update a progressbar with ASCII symbols for cmd output'''
    barLength = 100 
    status = ""
    # update progress
    if isinstance(progress, int):
        progress = float(progress)
    # something goes wrong
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    # progress finished
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    # draw progressbar
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "="*block + " "*(barLength-block), round(progress*100,2), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def get_local_timestamp(item):
    '''get timestamp of a local file and format it to a suitable time string'''
    return str(datetime.fromtimestamp(os.path.getmtime(item)).strftime("%Y-%m-%d %H:%M:%S")) if os.path.exists(item) else 0

def get_remote_timestamp(item, connection):
    '''get timestamp for a remote file and format it to a suitable time string'''
    timestamp = connection.sendcmd('MDTM '+ item)                      
    return  str(datetime.strptime(timestamp[4:], "%Y%m%d%H%M%S"))

def is_tgz(item):
    '''check file for .tgz ending'''
    return True if str(item).endswith('tgz') else False

def is_gz(item):
    '''check file for .gz ending, ignoring .tar.gz files'''
    return True if str(item).endswith('gz') and not str(item).endswith('tar.gz') else False   

def check_executable(executable, metacv):
    '''find path of executable for 'makeblastdb' or 'metacv' if not specified'''
    # check path given by arguments
    if executable:
        if os.path.exists(executable) and not os.path.isdir(executable):
            return executable
        else: 
            PathException(executable)
    # else find executable for 'makeblastdb'
    elif not metacv:
        return whereis('makeblastdb') if whereis('makeblastdb') else PathException('makeblastdb')
    # else find executable for 'metacv'
    else: 
        return whereis('metacv') if whereis('metacv') else PathException('metacv')

def whereis(program):
    ''' find the executable path for a given program'''
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
           not os.path.isdir(os.path.join(path, program)):
            return os.path.join(path, program)
    return None
