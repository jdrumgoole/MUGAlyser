import os
import sys
import smtplib

if os.path.isfile('keys.txt'):
	print "Keyfile already exists"
	exit()

host = "smtp.gmail.com"
port = 465

skey = os.urandom(16).encode('hex')
email = raw_input("Gmail: ")
passw = raw_input("Gmail pass: ")
uri = raw_input("Complete MongoDB URI: ")
valid = True

try:  
    server = smtplib.SMTP_SSL(host, port)
    server.ehlo()
    server.login(email, passw)
    server.close()
except Exception as e:
    print "Error: ", e
    print "If you are sure your password is correct and have 2FA enabled on your GMail account\nyou might need to generate a special password: https://www.google.com/settings/security/lesssecureapps"
    valid = False


if valid:
	with open("keys.txt", "w") as o:
		o.write(skey + "\n")
		o.write(email + "\n")
		o.write(passw)
	with open("uri.txt", "w") as o:
		o.write(uri)
