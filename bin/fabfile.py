# -*-python-*-

from fabric.api import run, env, local, cd, sudo

import os
import json

from mugalyser.apikey import get_meetup_key

# ["ec2-52-31-4-148.eu-west-1.compute.amazonaws.com"]
env.user = 'ec2-user'
home = os.getenv( "HOME" )
env.key_filename = os.path.join( home, "Documents", "jdrumgoole-vosa-eu.pem" )

if env.has_key( "instance_id" ) :
    instance_id = env.instance_id 
else:
    instance_id = "i-0600d15742f2bc599"


print( "using PEM file '%s' :" % env.key_filename ) 
print( "using instance ID: '%s'" % instance_id )

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
    local( "aws ec2  wait instance-stopped --instance-ids %s" % instance_id )

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
    with cd( "GIT" ) :
        run( "git clone https://github.com/jdrumgoole/mongodb_utils.git" )
        
def apikey():
    get_dns_name()
    with cd( "GIT/MUGAlyser/mugalyser") :
        run( "python makeapikeyfile_main.py %s" % get_meetup_key())
        
def get_data():
    get_dns_name()
    with cd( "GIT/MUGAlyser/bin") :
        run("sh atlasrun.sh" )
     
def prepare():
    start_instance()
    get_dns_name()   

def process_batch():
    update()
    gitpull()
    get_data()
    stop_instance()
    
def get_mongo():
    run( "wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-amazon-3.4.3.tgz")
    run( "tar xzvf mongodb-linux-x86_64-amazon-3.4.3.tgz")
    run( "sudo mkdir -p /usr/local")
    run( "sudo rm -rf /usr/local/mongodb-linux-x86_64-amazon-3.4.3")
    run( "sudo mv mongodb-linux-x86_64-amazon-3.4.3 /usr/local" )
    run( "sudo rm -rf /usr/local/mongodb" )
    run( "sudo ln -s /usr/local/mongodb-linux-x86_64-amazon-3.4.3 /usr/local/mongodb")
