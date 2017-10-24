#!/usr/bin/env python
# 
# ensembl_ftp_crawler.py
#
#   This starts at the specified base_dir of the ftp site and will recursively
#   search (down to the specified max_depth) for desired files.  Each
#   remote directory (or subdirectory) is examined for desired files (which
#   match the specified pattern).  If found, they are downloaded into a 
#   local temporary 
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
import tempfile
import re
import shutil
import sys
import pprint
import gzip
from   ftplib   import FTP
from   Bio      import Entrez, SeqIO
from   numpy    import median,mean,max

#
# The idea is to pass these on the command line in some way,
#  either options or a required FTP url or something...
#
base_site = "ftp.ensemblgenomes.org"
base_dir = "pub/release-37/plants/genbank/"
#base_dir = "pub/release-37/fungi/genbank/"
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
            print "feature: {0} mean: {1} median: {2} max: {3}".format(
                   feat, mean( feature_lens_dict[feat] ),
                                median( feature_lens_dict[feat] ),
                                max( feature_lens_dict[feat] ) )
        else:
            print "feature {0} has no lengths".format( feat )
    print("TOTAL FEATURE COUNT " + name + " : " + str(count))

    dprint( "end processing" )


# open, login in and cd to remote directory.
#  if subdir is given it is concatenated to basedir for cd

def open_ftp_link( subdir=None ):
    ftp = FTP( base_site )
    ftp.login()
    remdir = base_dir
    if  subdir != None:
        remdir = os.path.join( base_dir, subdir )  # hope this works for ftp!
    ftp.cwd( remdir )
    return ftp


# 
# this returns a list of contents which are verified subdirectories
# 
def  find_subdirectories( path, contents ):

    ftp = open_ftp_link( path )
    subdirs = []
    for file in contents:
        dprint( "checking if {0} is a subdir".format( file ) )
        try:
            ftp.cwd( file )
            subdirs.append( file )
            ftp.cwd( '..' )
        except ftplib.error_perm:
            print "{0} is not a directory".format( dr )
    ftp.close()
    return( subdirs )


def collect_files( path, files ):
    dprint( "collecting files " )
    dprint( files )
    for file in files:
        ftp = open_ftp_link( path )
        try:
            ftp.retrbinary( "RETR " + file, open( file, "wb" ).write )
        except:
            print "Error retrieving {0} {1}".format( path, file );
        ftp.close()
    dprint( "Files have been collected." )


# Here's the recursive driver    
    
def crawl( files, pathl=[] ):
    dprint( "crawl:" )
    dprint( files )
    dprint( pathl )
    if ( len( pathl ) < max_depth ):
        dpath = ''
        if ( len( pathl ) > 0 ):
            dpath = reduce( os.path.join, pathl )
        
        data_files = identify_data_files( files )
        dprint( "data files:")
        dprint( data_files )
        
        if len( data_files ) > 0:

            # if we have ANY data files, we process them, and don't
            # recurse
            
            local_directory = tempfile.mkdtemp()
            save_dir = os.getcwd()
            os.chdir( local_directory )

            collect_files( dpath, data_files )

            process( pathl[-1], data_files )

            os.chdir( save_dir )
            shutil.rmtree( local_directory )

        else:

            # otherwise we recurse into all the subdirs that we can find.

            subdirs = find_subdirectories( dpath, files )
            dprint( "subdirs:" )
            dprint( subdirs )
            for sd in subdirs:
                dpathl = pathl + [ sd ]
                dpath = reduce( os.path.join, dpathl )

                ftp = open_ftp_link( dpath )
                sub_files = ftp.nlst()
                ftp.close()

                crawl( sub_files, dpathl )


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

ftp = open_ftp_link()
top_level_files = ftp.nlst()
ftp.close()

crawl( top_level_files )

 
print "Program ends."



