#!/usr/bin/env python
# 
# ensembl_feature_lenghs.py
#
#  currently this scans one local subdirectory of ensemble data file (ie for
#  one organism) and prints out lines of
#
#            organism  feature    length
#
#

import os
import re
import sys
import pprint
import gzip
from   Bio      import Entrez, SeqIO
from   numpy    import median, mean, max

max_depth = 3


                            ###############
                            # Subroutines #
                            ###############

def dprint( x ):     # debug print
#    print( x )
    pass
    
# User should modify this regular expression match routine to return
# True if the file name is one of the desired data file types

reg = None

def  is_data_file( file ):

    global reg

    if reg == None:
        reg = re.compile( "\.dat\.gz$" )

    if reg.search( file ):
        return( True )
    else:
        return( False )

def  identify_data_files( files ):

    return( filter( is_data_file, files ) )


# name is orgname
# dirname is directory name.  (might be the same as orgname)

def  process( name, dirname ):
    dprint( "processing files for {0} in dir {1}".format( name, dirname ) )

    files = identify_data_files( os.listdir( dirname ) )
    dprint( files )

    for file in files:
        fpath = os.path.join( dirname, file )
        dprint( "processing file {0} ...".format( fpath ) )
        f = gzip.open( fpath, "r" )
        
        for rec in SeqIO.parse( f, "genbank"):
            for feature in rec.features:
                flen = feature.__len__()
                print "{0}\t{1}\t{2}".format( name, feature.type, flen )
        
        f.close()


                            ################
                            # Main program #
                            ################


if ( len( sys.argv ) < 2 ):
    print "Must specify directory on command line"
    sys.exit( 1 )

process( sys.argv[1], sys.argv[1] )

dprint( "Program ends." )



