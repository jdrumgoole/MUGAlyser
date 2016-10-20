# -*-python-*-

from fabric.api import *

import os

env.hosts = ['ec2-52-50-135-182.eu-west-1.compute.amazonaws.com']
env.user = 'ec2-user'
home = os.getenv( "HOME" )
env.key_filename = os.path.join( home, "Documents", "jdrumgoole-vosa-eu.pem" )

print( "using PEM file '%s' :" % env.key_filename ) 

def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

def update() :
    run( "sudo yum update" )

def gitpull() :
    with cd( "GIT/MUGAlyser" ) :
        run( "git pull" ) 
    
def gitclone() :
    run( "mkdir -p GIT" )
    with cd( "GIT" ) :
        run( "git clone https://github.com/jdrumgoole/MUGAlyser.git" ) 
    
