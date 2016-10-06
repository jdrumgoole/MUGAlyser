'''
Created on 4 Oct 2016

@author: jdrumgoole
'''

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import AuditDB
from flask import Flask, jsonify
app = Flask(__name__)

mdb = MUGAlyserMongoDB()
auditdb = AuditDB( mdb )
membersCollection = mdb.membersCollection()
groupCollection = mdb.groupsCollection()
auditCollection = auditdb.auditCollection()


def currentBatch():
    curBatch = auditCollection.find_one( { "name" : "Current Batch" }, {"_id" : 0 } )
    return jsonify( curBatch )
    
@app.route('/')
def index():
    return currentBatch()

@app.route('/groups')
def groups():
    
    #db.audit.find( { "batchID" : { "$exists" : 1  }}, { "end" : 1 }).sort( { "end" : -1 } ).pretty()

    curBatch = auditCollection.find_one( { "name" : "Current Batch" } )
    curGroups = groupCollection.find( { "batchID" : curBatch["ID"]}, 
                                      { "_id"           : 0, 
                                        "group.urlname" : 1 })
    
    output = []
    for d in curGroups:
        output.append( d["group"]["urlname"])
#         for k,v in d.iteritems() :
#             output = output + " " + str( k ) + ":" + str( v )  + "<br>"
        
    return jsonify( output )

@app.route( "/users")
def users():
    
    output =[]
    cursor = membersCollection.find({}, { "_id" :0, "member.name" : 1 }).distinct( "member.name")
    
    count = 0
    for i in cursor:
        count = count + 1
        output.append( i )
        
    return jsonify( { "count": count, "members" : output } )
        
        
    return "users"
    
@app.route('/user/<member>')
def get_member(member):
    # show the user profile for that user
    
    member = membersCollection.find_one({ "member.name" : member }, { "_id":0 })
    return jsonify( member )

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

if __name__ == "__main__":
    app.run()