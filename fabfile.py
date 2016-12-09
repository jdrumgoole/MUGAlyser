# -*-python-*-

from fabric.api import run, env, local,cd, sudo

import os
import json

from mugalyser.apikey import get_meetup_key, get_mugalyer_passwd

 # ["ec2-52-31-4-148.eu-west-1.compute.amazonaws.com"]
env.user = 'ec2-user'
home = os.getenv( "HOME" )
env.key_filename = os.path.join( home, "Documents", "jdrumgoole-vosa-eu.pem" )

instance_id = "i-08ec12f4af8554243"

print( "using PEM file '%s' :" % env.key_filename ) 


ATLAS_PRIMARY= "mugalyser-shard-00-00-ffp4c.mongodb.net"
PASSWD = ""

def local_uname():
    local('uname -a')

def remote_uname():
    get_dns_name()
    run('uname -a')

def describe_instance():
    local( "aws ec2 describe-instances --instance-ids %s" % instance_id )
    
def get_dns_name():
    if len( env.hosts ) == 0 :
        info = local( "aws ec2 describe-instances --instance-ids %s" % instance_id, capture=True )
        #print( "--%s--" % info )
        instance_info = json.loads( info )
        env.hosts=[]
        env.hosts.append( instance_info["Reservations"][0]["Instances"][0]["PublicDnsName"] )
        print( "Host: %s" % instance_info["Reservations"][0]["Instances"][0]["PublicDnsName"])
        
        with open( "ec2.out", "w" ) as ec2file :
            ec2file.write(instance_info["Reservations"][0]["Instances"][0]["PublicDnsName"] )
            ec2file.write( "\n")
        
    
def start_instance():
    local( "aws ec2 start-instances --instance-id %s" % instance_id )
    local( "aws ec2  wait instance-running --instance-ids %s" % instance_id )
    get_dns_name()
    
def stop_instance():
    local( "aws ec2 stop-instances --instance-id %s" % instance_id )

def update() :
    #get_dns_name()
    print( "hosts ---> '%s'" % env.hosts )
    sudo('yum -y update', shell=False)
    #run( "sudo yum -y update" )

def gitpull() :
    with cd( "GIT/MUGAlyser" ) :
        run( "git pull" ) 
    
def gitclone() :
    get_dns_name()
    run( "mkdir -p GIT" )
    with cd( "GIT" ) :
        run( "git clone https://github.com/jdrumgoole/MUGAlyser.git" )
        
def apikey():
    get_dns_name()
    with cd( "GIT/MUGAlyser/mugalyser") :
        run( "python makeapikeyfile_main.py %s %s" % ( get_meetup_key(), get_mugalyer_passwd()))
        
def get_data():
    get_dns_name()
    with cd( "GIT/MUGAlyser/mugalyser") :
        run("atlasrun.sh" )
        

def process_batch():
    start_instance()
    get_dns_name()
    update()
    gitpull()
    get_data()
    stop_instance()
    
def test_batch():
    get_dns_name()
    update()
    gitpull()
    get_data()
    stop_instance()
    
get_dns_name()