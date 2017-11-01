#!/usr/bin/env python
# 
# ensembl_local_crawler.py   base_dir
#
#   Derived from ensembl_ftp_crawler, but works on a local directory tree
#   thats been downloaded via ftp_save_crawler.py
#   
#   This starts at the specified base_dir of  and will recursively
#   search (down to the specified max_depth) for desired files.  Each
#   remote directory (or subdirectory) is examined for desired files (which
#   match the specified pattern).  If found, they are analyzed.  
#
#   Its assumed that each directory corresponds to an organism, so all
#   processing is done at once on all the organism files collected.
#
#   *Only if no desired files are found*, is the directory is then examined 
#   for subdirectories, which are then recursively processed.
#
#   The intent is for the function and procedures
#   
#       is_data_file()
#   and
#       process()
#
#   to be modified for different uses.
#
# Caveats and TODOs - too many to list - no error handling to speak of for
# one thing
#

import os
import re
import sys
import pprint
import gzip
from   Bio      import Entrez, SeqIO
from   numpy    import median, mean, max

#
# The idea is to pass these on the command line in some way,
#  either options or a required FTP url or something...
#
max_depth = 3


                            ###############
                            # Subroutines #
                            ###############

def dprint( x ):     # debug print
    #print( x )
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

# User should modify this routine for analyzing the file for one
# organism (subdirectory)
#
# Currently, this uses Jason Baumohls GBFF feature counting code,
#  modified to handle multiple gzipped files, and count max feature
#  length 

def  process( name, files ):
    dprint( "processing files for {0}".format( name ) )
    dprint( files )

    contig_count = 0
    count = 0
    feature_count_dict = dict()
    feature_lens_dict = dict()       # for mean, median, max

    for file in files:
        dprint( "processing file {0} ...".format( file ) )
        f = gzip.open( file, "r" )
        
        for rec in SeqIO.parse( f, "genbank"):
            contig_count += 1
            for feature in rec.features:
                flen = feature.__len__()
                if feature.type in feature_count_dict:
                    feature_count_dict[feature.type] += 1
                    feature_lens_dict[feature.type].append( flen )
                else:
                    feature_count_dict[feature.type] = 1
                    feature_lens_dict[feature.type] = []
                count += 1
        
        f.close()

    print("TOTAL CONTIG COUNT " + name + " : "  + str(contig_count))
    #pprint.pprint(feature_count_dict)
    for feat in sorted( feature_lens_dict ):
        if  len( feature_lens_dict[feat] ) > 0:
            print "feature: {0} count: {1} mean: {2} median: {3} max: {4}".format(
                   feat, feature_count_dict[feat],
                          mean( feature_lens_dict[feat] ),
                                median( feature_lens_dict[feat] ),
                                max( feature_lens_dict[feat] ) )
        else:
            print "feature: {0} count: {1} has no lengths".format( 
                   feat, feature_count_dict[feat] )
    print("TOTAL FEATURE COUNT " + name + " : " + str(count))

    dprint( "end processing" )




# 
# this returns a sublist of files which are subdirectories
# 
def  identify_subdirectories( files ):

    return( filter( os.path.isdir, files ) )
 



# Here's the recursive driver    
    
def crawl( dir, pathl=[] ):
    dprint( "crawl: {0}".format( dir ) )
    dprint( pathl )

    if len( pathl ) < max_depth:
        save_dir = os.getcwd()
        os.chdir( dir )

        files = os.listdir( "." )
        data_files = identify_data_files( files )
        dprint( "data files:" )
        dprint( data_files )
        
        #dpath = ''
        #if ( len( pathl ) > 0 ):
        #    dpath = reduce( os.path.join, pathl )
        
        if len( data_files ) > 0:

            # if we have ANY data files, we process them, and don't
            # recurse

            process( dir, data_files )

        else:

            # otherwise we recurse into all the subdirs that we can find.

            subdirs = identify_subdirectories( files )
            dprint( "subdirs:" )
            dprint( subdirs )

            for sd in subdirs:
                crawl( sd, pathl + [ dir ] )

        os.chdir( save_dir )


                            ################
                            # Main program #
                            ################

# Collect organism sub-directory list
#  (which is also going to include non-organism subdirectories - we'll
#   have to deal with those later)
#
# Because the processing of the files can take a while, to prevent timeouts
# on the FTP connection, we always open a new collection, fetch, and then 
# close when that's completed.
#

if len( sys.argv ) < 2:
    print "must specify a base_dir"
    sys.exit( 1 )

crawl( sys.argv[1] )

 
print "Program ends."



