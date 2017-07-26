'''
Created on 4 Oct 2016

@author: jdrumgoole
'''
# -*- coding: utf-8 -*-

from mugalyser.mongodb import MUGAlyserMongoDB
from mugalyser.audit import Audit
from mugalyser.analytics import MUG_Analytics
from flask import Flask, jsonify, request, session, redirect, url_for, send_file, Response
from flask.templating import render_template
from pymongo import MongoClient
from cgi import escape
from hashlib import sha512
from os import urandom
from datetime import datetime
from OpenSSL import SSL

import time
import os
import re
import webbrowser

context = SSL.Context(SSL.SSLv23_METHOD)
cer = os.path.join('/home/ec2-user/*.joedrumgoole.com.ssl/joedrumgoole.com.crt')
key = os.path.join('/home/ec2-user/*.joedrumgoole.com.ssl/*.joedrumgoole.com.key')

DEBUG = False

if not os.path.isfile('keys.txt') or os.stat('keys.txt').st_size == 0:
    print "Please run web_setup.py first"
    exit()

import send_email

app = Flask(__name__)

with open('keys.txt', 'r') as f:
    skey = f.readline().strip("\n")
    app.config['SECRET_KEY'] = skey
with open('uri.txt', 'r') as f:
    uri=f.readline().strip("\n")

try:
    print "Connecting to database..."
    mdb = MUGAlyserMongoDB(uri = uri)

except Exception as e:
    print "URI isn't valid, trying to run on localhost now"
    mdb = MUGAlyserMongoDB()

auditdb = Audit( mdb )
an = MUG_Analytics(mdb)
membersCollection = mdb.membersCollection()
proMemCollection = mdb.proMembersCollection()
groupCollection = mdb.groupsCollection()
proGrpCollection = mdb.proGroupsCollection()
eventsCollection = mdb.pastEventsCollection()
currentBatch = auditdb.get_last_valid_batch_id()

connection = mdb.client()
db = connection.MUGS
userColl = db.users
resetColl = db.resets

@app.before_request    #somehow works to redirect all http requests to https
def secure_redirect():
    pass

@app.errorhandler(404)
def not_found(error):
    if not verify_login():
        return redirect(url_for('show_login'))
    return render_template('404.html', error = error), 404

def verify_login():
    if 'username' not in session:
        return False
    return True

def create_account(user, password, email):
    salt = urandom(16).encode('hex')
    verify = urandom(16).encode('hex')
    hashPwd = sha512(password + salt).hexdigest()
    if email is not None:
        send_email.send(email, user, verify, "Signup")
        userColl.insert({'_id': user, 'salt': salt, 'pass': hashPwd, 'email': email, 'signup_date' : datetime.utcnow(), 
            'signup_ip' : request.remote_addr, 'reset_ip': '', 'verified': verify, 'last_login': datetime.utcnow()})
    else:
        userColl.update({'_id': user}, {"$set": {'salt': salt, 'pass': hashPwd, 'reset_ip': request.remote_addr, 'last_login': datetime.utcnow()}})
    if userColl.find_one({'_id':user})['verified'] == True:
        session['username'] = user

def get_group_list():
    cur = proGrpCollection.find( { "batchID" : currentBatch, "group.name": {"$ne": "Meetup API Testing Sandbox"}}, 
                                              { "_id"           : 0, 
                                                "group.name" : 1,
                                                "group.member_count" : 1}).sort([("group.member_count", -1)])
    groupl = [{'Name' : d["group"]["name"]} for d in cur]
    return groupl

def get_batch_list():
    batchIDs = auditdb.getBatchIDs()

    batchIDList = [d for d in batchIDs]
    batchIDList = list(set(batchIDList))  #removes duplicates 

    return batchIDList
     
@app.route('/')
def index():
    if 'username' in session:
        return render_template("index.html", user = session['username'], batch = auditdb.get_last_valid_batch_id(), groupn = len(get_group_list()))
    return redirect(url_for('show_login'))

@app.route('/groups')
def groups():
    if not verify_login():
        return redirect(url_for('show_login'))
    curGroups = proGrpCollection.find( { "batchID" : currentBatch}, 
                                      { "_id"           : 0, 
                                        "group.name" : 1,
                                        "group.member_count": 1,
                                        "group.average_age": 1 }).sort([("group.member_count", -1)])
    
    output = []
    for d in curGroups:
        output.append( [d["group"]["name"], "{:,}".format(d["group"]["member_count"]), round(d["group"]["average_age"], 2)])
        
    return render_template("groups.html", groups = output)

@app.route( "/members/<int:pg>", methods = ['POST', 'GET'])
def members(pg):
    if not verify_login():
        return redirect(url_for('show_login'))
    query = "N0NE"
    interest = "nothing."
    output = []
    if request.method == 'POST':
        try: 
            query = escape(request.form.get('query'))
        except:
            pass
        regquery = re.compile(query, re.IGNORECASE)
        if request.form.get('int') != "nothing." and request.form.get('int') != "":
            interest = escape(request.form.get('int')).replace(" ", "")
            ilist = interest.split(",")
            pipeline = [
                {"$match":
                    {"batchID": currentBatch,
                    "member.name" : regquery}
                },
                {"$unwind": "$member.topics"},
                {"$group":
                    {
                    "_id": {"ID" :"$member.id", "name": "$member.name"},
                    "ints":
                        {"$push": "$member.topics.urlkey"}
                    }
                },
                {"$project":{
                    "ints": 1,
                    "_id": 1,
                    "isSub" : {"$setIsSubset" :[ilist, "$ints"] }
                    }
                },
                {
                "$match":{
                    "isSub": True
                    }
                }
            ]
            cursor = membersCollection.aggregate(pipeline)
            # print cursor.count()
            # for i in cursor:
            #     print i
            output = [i['_id']['name'] for i in cursor]
        else:
            output = membersCollection.find({"batchID": currentBatch, "member.name" : regquery}, { "_id" :0, "member.name" : 1 }).distinct("member.name")
            #[pg * 1000: 1000 + (pg*1000)]
            # for i in cursor:
            #     output.append( i ) 
    else:
        curs = membersCollection.find({"batchID": currentBatch, "member.name": { "$exists": True}}, { "_id" :0, "member.name" : 1}).sort("member.name", -1).distinct("member.name")
        output =  curs[pg * 1000: 1000 + (pg*1000)]
        # output =[]
        # for i in cursor:
        #     output.append( i )
    return render_template("members.html", members = output, cur = pg, query = query, filt = interest)

@app.route("/graph/yearly")
def graph_yearly():
    if not verify_login():
        return redirect(url_for('show_login'))
    now = datetime.now()
    curYear = int(now.year)
    dates = [i for i in range(2009, curYear + 1)]
    output = []
    events = {}
    # for year in dates:
    pipeline = [
        {"$match": {"batchID": currentBatch}},
        {"$project":
            {
               "year": { "$year": "$event.time" },
               "yesrsvp" : "$event.yes_rsvp_count"
            }
        },
        {"$match": {"year": {"$in": dates}}},
        {"$group": {"_id": "$year", "total_rsvp": {"$sum": "$yesrsvp"}, "numevents": {"$sum": 1}}}
    ]
    eCurs = eventsCollection.aggregate(pipeline)
    # doc = eCurs.next()
    # output.append({'Year' : year, 'Total RSVP': doc['total_rsvp']})
    # events[year] = doc['numevents']
    for doc in eCurs:
        year = doc['_id']  
        output.append({'Year' : year, 'Total RSVP': doc['total_rsvp']})
        events[year] = doc['numevents']
    return render_template("graphyearly.html", groups = output, events = events)

@app.route("/graph", methods=['POST', 'GET'])
def graph():
    if not verify_login():
        return redirect(url_for('show_login'))

    if request.method == 'GET' or request.form.get('res'):  #sets options to default values
        curbat = session['batch'] = currentBatch
        curGroup = session['group'] = "None"
        amt = session['amount'] = 0
        country = session['country'] = "None"
    else:
        curbat = request.form.get('bat')
        curGroup = request.form.get('grp')
        amt = request.form.get('amt')
        country = request.form.get('country')

        if curbat is None:
            curbat = session['batch']
        else:
            session['batch'] = curbat
            country = session['country'] = "None"

        if curGroup is None:
            curGroup = session['group']
        else:
            session['group'] = curGroup
            country = session['country'] = "None"
        
        if amt is None:
            amt = session['amount']
        else:
            session['amount'] = int(amt)
            country = session['country'] = "None"

        if country is None:
            country = session['country']
        else:
            session['country'] = country

    output = []

    if curGroup == 'None' and country == 'None':
        groupCurs = groupCollection.find( { "batchID" : int(curbat), "group.name": {"$ne": "Meetup API Testing Sandbox"}, "group.members" : {"$exists" : True}}, 
                                          { "_id"           : 0, 
                                            "group.name" : 1,
                                            "group.members" : 1}).sort([("group.members", -1)]).limit(int(amt))
        output = [{'Name' : d["group"]["name"], 'Count': d["group"]["members"]} for d in groupCurs]
        # print output

    if country in ['EU', 'US', 'ALL']:
        groupList = an.get_group_names(country)
        # print groupList
        pipeline = [
            {"$match": {"group.members" : {"$exists" : True}, "group.urlname": {"$in" : groupList}}},
            {"$project":
                {
                   "group.name" : 1,
                   "group.members" : 1,
                   "timestamp" : 1
                }
            },
            {"$group": {"_id": "$group.name"}}
        ]
        groupCurs = groupCollection.aggregate(pipeline)
        print "Group is", groupCurs.next()
    elif curGroup != 'None':
        # groupCurs = proGrpCollection.find( {"group.name": curGroup}, 
        #                           { "_id"           : 0, 
        #                             "group.name" : 1,
        #                             "group.member_count" : 1,
        #                             "timestamp" : 1})
        # # print datetime.utcfromtimestamp(groupCurs.next()["timestamp"])
        # output = [{'Name' : d["group"]["name"], 'Count': d["group"]["member_count"], 'Time': d["timestamp"]} for d in groupCurs]
        groupCurs = groupCollection.find( {"group.name": curGroup, "group.members" : {"$exists" : True}}, 
                                  { "_id"           : 0, 
                                    "group.name" : 1,
                                    "group.members" : 1,
                                    "timestamp" : 1})
        # print datetime.utcfromtimestamp(groupCurs.next()["timestamp"])
        output = [{'Name' : d["group"]["name"], 'Count': d["group"]["members"], 'Time': d["timestamp"]} for d in groupCurs]

    # groupl = get_group_list()
    # batchl = get_batch_list()
    # print "------------\n", output
    return render_template("graph.html", groups = output, grouplist = get_group_list(), batches = get_batch_list(), curbat = int(curbat), curamt = int(amt), curgroup = curGroup, country = country)

@app.route("/graph/batch", methods=['POST', 'GET'])
def graph_batch():
    if not verify_login():
        return redirect(url_for('show_login'))

    pipeline = [
        {"$group": {"_id": "$batchID", "total_members": {"$sum": "$group.member_count"}}}
    ]

    groupCurs = proGrpCollection.aggregate(pipeline)
    output = [{'Batch' : d['_id'], 'Count': d['total_members']} for d in groupCurs]

    return render_template("graphbatch.html", members = output)
@app.route('/user/<member>')
def get_member(member):
    # show the user profile for that user
    if not verify_login():
        return redirect(url_for('show_login'))
    member = membersCollection.find_one({"member.name" : member, "batchID" : currentBatch }, { "_id":0})
    return render_template("user.html", user = member)

@app.route('/signup')
def show_signup():
    if verify_login():   #if user is already logged in, redirects them to index
        return redirect(url_for('index'))
    return render_template("signup.html")

@app.route('/signup', methods = ['POST'])
def get_signup():
    if verify_login():   #if user is already logged in, redirects them to index
        return redirect(url_for('index'))
    user = escape(request.form.get('username'))
    password = escape(request.form.get('password'))
    vpassword = escape(request.form.get('verify'))
    email = user + '@mongodb.com'

    userreg = re.compile(user, re.IGNORECASE)

    if userColl.find({'_id':userreg}).count() != 0 or len(user) < 1:  #checks if username is in use already, prevents empty username
        return render_template("signup.html", error = "User with that name already exists. Please try a different name.")
    if '@' in user:
        return render_template("signup.html", error = "The @ symbol is not allowed. Please try a different name.")
    if re.search(r"\s", user):
        return render_template("signup.html", error = "Whitespace is not allowed. Please try a different name.")
    if userColl.find({'email':email}).count() != 0:                #checks if email is in use
        return render_template("signup.html", username = user, error = "That email is already in use. Please try a different name.")
    # if not email.endswith(('mongodb.com', '10gen.com')):
    #     return render_template("signup.html", username = user, error = "Invalid email address.")
    if len(password) < 5:                                          #only permits passwords over 4 characters
        return render_template("signup.html", username = user, error = "Passwords must be over 4 characters long")
    if vpassword != password:                                      #checks if password and verification match
        return render_template("signup.html", username = user, error = "Passwords don't match")

    create_account(user, password, email)
    print "Account created with username", user
    return """
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <a href="/">Home</a>
    <h4> Signup email sent! Please check your inbox.</h4>
    """

@app.route('/verify/<ID>')
def verify_account(ID):
    if userColl.find_one({'verified':ID}):
        session['username'] = userColl.find_one({'verified': ID})['_id']
        userColl.update({'verified': ID}, {'$set': {'verified': True}})
        return redirect(url_for('index'))
    return """
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <a href="/">Home</a>
    <p>Verify link is invalid (you may have already verified)."""

@app.route('/login')
def show_login():
    if verify_login():   #if user is already logged in, redirects them to index
        return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/login', methods = ['POST'])
def get_login():
    if verify_login():   #if user is already logged in, redirects them to index
        return redirect(url_for('index'))
    user = escape(request.form.get('username'))
    password = escape(request.form.get('password'))

    if userColl.find({'_id':user}).count() == 0: #checks if user exists
        error = "Invalid login"
        return render_template("login.html", login_error = error)

    if userColl.find_one({'_id':user})['verified'] != True:   #has to explicitly check against bool since value may be interpreted as True otherwise
        error = "Account not verified yet. Please check your email"
        return render_template("login.html", login_error = error)

    salt = userColl.find_one({'_id': user})['salt']  #gets the user's salt

    if userColl.find_one({'_id': user}, {'_id': 0, 'pass' : 1})['pass'] != sha512(password + salt).hexdigest():  #salts and hashes password input with the stored salt
        return render_template("login.html", username = user, login_error = "Invalid login")          #and verifies it matches the hash in database

    print "User", user, "logged in"
    userColl.update({'_id': user}, {"$set": {'last_login': datetime.utcnow()}})
    session['username'] = user

    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    if 'username' in session:   #removes user session
        session.pop('username')
    return redirect(url_for('index'))

@app.route('/pixel.gif')   #tracking pixel for emails
def track():   
    print "Email viewed by:", request.headers.get('X-Forwarded-For', request.remote_addr)
    return send_file('static/pixel.gif', mimetype = 'image/gif')

@app.route('/forgotpw', methods = ['GET', 'POST'])
def forgot_pw():
    if request.method == 'GET':
        return render_template('forgotpw.html')
    email = escape(request.form.get('email'))
    if userColl.find({'email':email}).count() == 0: #checks if user with specified email exists
        return render_template('forgotpw.html', email_error = "Can't find that email")
    user = userColl.find_one({'email':email})['_id']
    if resetColl.find({'user': user}).count() != 0: #checks if pending reset already exists, if yes marks it as invalid
        resetColl.remove({'user': user})
    resetID = urandom(16).encode('hex')
    resetColl.insert({'_id': resetID, 'timestamp': datetime.utcnow(), 'user': user})
    # webbrowser.get('open -a /Applications/Google\ Chrome.app %s').open_new_tab('http://127.0.0.1:5000/resetpw/'+resetID)
    send_email.send(email, user, resetID)
    return """
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <a href="/">Home</a>
    <h4> Reset email sent! Please check your inbox.</h4>
    """

@app.route('/resetpw/<ID>')
def show_reset(ID):
    if resetColl.find_one({'_id': ID}):
        return render_template("reset.html", error = "Please enter a new password.")
    return """
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <a href="/">Home</a>
    <p>Reset link is invalid."""
    
@app.route('/resetpw/<ID>', methods = ['POST'])
def reset_pw(ID):
    password = escape(request.form.get('password'))
    vpassword = escape(request.form.get('verify'))
    doc = resetColl.find_one({'_id': ID})
    if len(password) < 5:
        return render_template("reset.html", error = "Passwords must be over 4 characters long")
    if vpassword != password:
        return render_template("reset.html", error = "Passwords don't match")
    if doc:
        user = doc['user']
        create_account(user, password, None)
        resetColl.remove({'_id' : ID})
        return redirect(url_for('index'))
    return """
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <a href="/">Home</a>
    <p>Reset link is invalid."""
if __name__ == "__main__":
    context = (cer, key)
    app.run(host='0.0.0.0', port = 443, debug = DEBUG, threaded = True, ssl_context = context)

