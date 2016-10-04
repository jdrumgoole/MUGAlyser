'''
Created on 4 Oct 2016

@author: jdrumgoole
'''

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import AuditDB
from flask import Flask
app = Flask(__name__)

mdb = MUGAlyserMongoDB()
auditdb = AuditDB( mdb )

@app.route('/')
def index():
    return 'Index Page'

@app.route('/groups')
def groups():
    groupCollection = mdb.groupsCollection()
    auditCollection = auditdb.auditCollection()
    
    #db.audit.find( { "batchID" : { "$exists" : 1  }}, { "end" : 1 }).sort( { "end" : -1 } ).pretty()

    curBatch = auditCollection.find_one( { "name" : "Current Batch" } )
    curGroups = groupCollection.find( { "batchID" : curBatch["ID"]}, 
                                      { "_id"           : 0, 
                                        "group.urlname" : 1 })
    
    output = ""
    for d in curGroups:
        for k,v in d.iteritems() :
            output = output + " " + str( k ) + ":" + str( v )  + "<br>"
        
    return output

@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id