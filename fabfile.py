# -*-python-*-

from fabric.api import run, env, local,cd

import os

from mugalyser.apikey import MEETUP_API_KEY, PASSWD

env.hosts = ['ec2-52-50-135-182.eu-west-1.compute.amazonaws.com']
env.user = 'ec2-user'
home = os.getenv( "HOME" )
env.key_filename = os.path.join( home, "Documents", "jdrumgoole-vosa-eu.pem" )

instance_id = "i-08ec12f4af8554243"

print( "using PEM file '%s' :" % env.key_filename ) 


ATLAS_PRIMARY= "mugalyser-shard-00-00-ffp4c.mongodb.net"


def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

def start_instance():
    local( "aws ec2 start-instances --instance-id %s" % instance_id )
    local( "aws wait instance-running --instance-ids %s" % instance_id )
    
def stop_instance():
    local( "aws ec2 stop-instances --instance-id %s" % instance_id )
    

def update() :
    run( "sudo yum update" )

def gitpull() :
    with cd( "GIT/MUGAlyser" ) :
        run( "git pull" ) 
    
def gitclone() :
    run( "mkdir -p GIT" )
    with cd( "GIT" ) :
        run( "git clone https://github.com/jdrumgoole/MUGAlyser.git" )
        
def apikey():
    with cd( "GIT/MUGAlyser/mugalyser") :
        run( "python makeapikeyfile_main.py " + MEETUP_API_KEY )
        
def mugs():
    with cd( "GIT/MUGAlyser/mugalyser") :
        run("python mugalyser_main.py --replset MUGAlyser-shard-0 --host %s --username jdrumgoole --ssl --password %s --mugs all" % ( ATLAS_PRIMARY, PASSWD ))
        
def attendees():
    with cd( "GIT/MUGAlyser/mugalyser") :
        run("python mugalyser_main.py --replset MUGAlyser-shard-0 --host %s --username jdrumgoole --ssl --password %s --attendees all" % ( ATLAS_PRIMARY, PASSWD ))     
    
