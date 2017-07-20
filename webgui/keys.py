import os
import sys

skey = os.urandom(16).encode('hex')
email = raw_input("Gmail: ")
passw = raw_input("Gmail pass: ")

with open("keys.txt", "w") as o:
	o.write(skey + "\n")
	o.write(email + "\n")
	o.write(passw)

x = ""
with open("keys.txt", "r") as f:
	for line in f:
		x+=line.strip("\n")
	print x

