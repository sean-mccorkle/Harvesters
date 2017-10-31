#!/usr/bin/env python
# 
# ensembl_local_analyzer.py
#
#  currently this scans one subdirectory of ensemble data file (ie for one
#  organism) and prints out lines of
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

    contig_count = 0
    count = 0
    feature_count_dict = dict()
    feature_lens_dict = dict()       # for mean, median, max

    for file in files:
        fpath = os.path.join( dirname, file )
        dprint( "processing file {0} ...".format( fpath ) )
        f = gzip.open( fpath, "r" )
        
        for rec in SeqIO.parse( f, "genbank"):
            contig_count += 1
            for feature in rec.features:
                flen = feature.__len__()
                print "{0} {1} {2}".format( name, feature.type, flen )
                if feature.type in feature_count_dict:
                    feature_count_dict[feature.type] += 1
                    feature_lens_dict[feature.type].append( flen )
                else:
                    feature_count_dict[feature.type] = 1
                    feature_lens_dict[feature.type] = []
                count += 1
        
        f.close()


                            ################
                            # Main program #
                            ################


if ( len( sys.argv ) < 2 ):
    print "Must specify directory on command line"
    sys.exit( 1 )

process( sys.argv[1], sys.argv[1] )

dprint( "Program ends." )



