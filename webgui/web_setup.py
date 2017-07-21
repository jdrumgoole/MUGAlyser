import os
import sys
import smtplib

host = "smtp.gmail.com"
port = 465

skey = os.urandom(16).encode('hex')
email = raw_input("Gmail: ")
passw = raw_input("Gmail pass: ")

try:  
    server = smtplib.SMTP_SSL(host, port)
    server.ehlo()
    server.login(email, passw)
    server.close()
except Exception as e:
    print "Error: ", e
    exit()

with open("keys.txt", "w") as o:
	o.write(skey + "\n")
	o.write(email + "\n")
	o.write(passw)

