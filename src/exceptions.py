import sys

class ConnectionException(Exception):

    def __init__(self, item):
        sys.stderr.write("Connection to %s failed!\n" % (item))
        sys.exit(1)
        
class FtpPathException(Exception):

    def __init__(self, item):
        sys.stderr.write("\nError: Could not find %s\n" % (item))
        
class FtpIndexException(Exception):

    def __init__(self, item):
        sys.stderr.write("\nError: Index generation failed for %s\n" % (item))
        return []
    
class FtpDownloadException(Exception):

    def __init__(self, item):
        sys.stderr.write("\nError: download of file %s not sucessfull!\n" % (item))
        
class ExtractionException(Exception):

    def __init__(self, item):
        sys.stderr.write("\nError: Extraction of %s failed!" % (item))
        
class MultiFastaException(Exception):

    def __init__(self):
        sys.stderr.write("\nError: Combining sequences failed!\n")
        sys.exit(1)
        
class BlastDBException(Exception):

    def __init__(self):
        sys.stderr.write("\nError: Creation of BlastDB failed!\n") 
        sys.exit(1)

class MetaCVException(Exception):

    def __init__(self):
        sys.stderr.write("\nError: Creation of MetaCV DB failed!\n")
        sys.exit(1)
        
class PathException(Exception):

    def __init__(self, item):
        sys.stderr.write("Error: No executable found for %s!\nPlease use -e/--exe argument or check path" % (item))
        sys.exit(1)

class ActualException(Exception):

    def __init__(self, item):
        sys.stderr.write('\n%s is actual!\n' % (item))