#!/usr/bin/env python
# 
# ensembl_ftp_crawler.py
#
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
#       is_desired_file()
#   and
#       process()
#
#   to be modified for different uses.


import os
from ftplib import FTP

max_depth = 3
base_site = "ftp.ensemblgenomes.org"
base_dir = "pub/release-37/plants/genbank/"

                            ###############
                            # Subroutines #
                            ###############

# open, login in and cd to remote directory.
#  if subdir is given it is concatenated to basedir for cd

def open_ftp_link( subdir = None):
    ftp = FTP( base_site )
    ftp.login()
    remdir = base_dir
    if  subdir != None:
        remdir = os.path.join( base_dir, subdir )  # hope this works for ftp!
    ftp.cwd( remdir )
    return ftp


def  find_data_files

# 
# this returns a list of paths which are verified subdirectories
# 
def  find_subdirectories( path, contents ):

    ftp = open_ftp_link( path )
    subdirs = []
    for file in contents
        print "checking if {0} is a subdir".format( file )
        try:
            ftp.cwd( file )
            subdirs.append( fpath, os.path.join( path, file ) ]
            ftp.cwd( '..' )
        except ftplib.error_perm:
             print "{0} is not a directory".format( dr )
    ftp.close()
    return( subdirs )

def  process( path, files ):
    print "processing files in path {0}".format( path )
    print files
    print "end processing"

def crawl( files, pathl=[] ):
    if ( len( path ) > max_depth ):
        for d in files:
            dpath = op.path.join( path, d )
            print [ d, dpath ]
            ftp = open_ftp_link( dpath )
            contents = ftp.nlst()
            ftp.close()
            print contents
            data_files = find_data_files( contents )
            if len( data_files ) > 0:
                process( dpath, data_files )
            else:
                subdirs = find_subdirectories( dpath, contents )
                for sd in subdirs:
                    dpath = path
                    dpath.append( sd )
                    ftp2 = open_ftp_link( dpath )
                    sub_contents = ftp2.nlst()
                    ftp2.close()
                    crawl( sub_contents, depth+1 )


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
files = ftp.nlst()
ftp.close()

crawl( files )

 
print "Program ends."   


