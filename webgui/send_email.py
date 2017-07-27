import smtplib  
import email.utils
import os
import signal
import requests
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.

sendername = "MUGAlyser"

# The subject line for the email.
subject = "MUGAlyser Password Reset"

# The character encoding for the email.
charset = "UTF-8"

host = "smtp.gmail.com"
port = 465
bcc = "mugalyser_app_log@10gen.com"
SENT = False

sender = "mugalyser@mongodb.com"
smtp_username = smtp_password = ""


try:
    f = os.popen('ifconfig en0')
    ip = f.read().split("inet ")[1].split(" ")[0]
    print "Running locally on http://"+ ip
except Exception as e:
    ip = requests.get('http://ip.42.pl/raw').text
    print "Running externally on http://"+ ip
msg = MIMEMultipart('alternative')


keys = []
with open("keys.txt", "r") as f:
    for line in f:
        keys.append(line.strip("\n"))

sender = smtp_username = keys[1]
smtp_password = keys[2]


# Try to send the email.
def send(recipient, user, ID = "", type= ""):
    try:
        server = smtplib.SMTP_SSL(host, port)
        server.ehlo()
        server.login(smtp_username, smtp_password)
    except Exception as e:
        print "Error: ", e
    msg['From'] = email.utils.formataddr((sendername, sender))
    msg['To'] = email.utils.formataddr((user, recipient))
    # msg['Bcc'] = email.utils.formataddr(("Logs", bcc))
    text = ID
    if type == "Signup":
        msg['Subject'] = 'MUGAlyser - Verify your account'
        html = "Hey " + user + ", <p>Welcome to MUGAlyser!<p>Please click <a href='http://" + ip + ":5000/verify/"  + ID + "'>here</a> to verify your account"
    else:
        msg['Subject'] = subject
        html = "Hey " + user + ", <p>Please click <a href='http://" + ip + ":5000/resetpw/"  + ID + "'>here</a> to reset your password. <p><p><b>Please note that password request links expire 24 hours after creation.</b><img src = 'http://" + ip + ":5000/pixel.gif' width='1' height='1'></img>"
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    try:
        server.sendmail(sender, [recipient, bcc], msg.as_string())
    except Exception as e:
        print "Error: ", e

    del msg['From']
    del msg['To']
    del msg['Bcc']
    print "Email sent to", recipient
