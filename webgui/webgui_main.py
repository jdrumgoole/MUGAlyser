'''
Created on 4 Oct 2016

@author: jdrumgoole
'''

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from flask import Flask, jsonify
from flask.templating import render_template
app = Flask(__name__)

mdb = MUGAlyserMongoDB()
auditdb = Audit( mdb )
membersCollection = mdb.membersCollection()
groupCollection = mdb.groupsCollection()
auditCollection = auditdb.auditCollection()


def currentBatch():
    curBatch = auditCollection.find_one( { "name" : "Current Batch" }, {"_id" : 0 } )
    return jsonify( curBatch )

     
@app.route('/')
def index():
    #return currentBatch()
    return "WIP"

@app.route('/groups')
def groups():

    curBatch = auditdb.currentBatch()
    curGroups = groupCollection.find( { "batchID" : curBatch["ID"]}, 
                                      { "_id"           : 0, 
                                        "group.urlname" : 1 })
    
    output = []
    for d in curGroups:
        output.append( d["group"]["urlname"])
#         for k,v in d.iteritems() :
#             output = output + " " + str( k ) + ":" + str( v )  + "<br>"
        
    return jsonify( output )

@app.route( "/members")
def members():
    
    output =[]
    cursor = membersCollection.find({}, { "_id" :0, "member.name" : 1 }).distinct( "member.name")
    
    count = 0
    for i in cursor:
        count = count + 1
        output.append( i )
        
    return render_template( "index.html", members=output )
    #return jsonify( { "count": count, "members" : output } )
        
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