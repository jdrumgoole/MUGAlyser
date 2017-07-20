import smtplib  
import email.utils
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.

sender = "ari.benderlong@10gen.com"
sendername = "MUGAlyser"

# The subject line for the email.
subject = "MUGAlyser Password Reset"

# The character encoding for the email.
charset = "UTF-8"

host = "smtp.gmail.com"
port = 465

smtp_username = "ari.benderlong@10gen.com"

smtp_password = "ujkxxepwuqqewiof"

f = os.popen('ifconfig en0')
local_ip=f.read().split("inet ")[1].split(" ")[0]

msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = email.utils.formataddr((sendername, sender))

# Try to send the email.
def send(recipient, user, ID):
    msg['To'] = email.utils.formataddr((user, recipient))
    html = "Hey " + user + ", <p>Please click <a href='http://" + local_ip + ":5000/resetpw/"  + ID + "'>here</a> to reset your password. <p><p><b>Please note that password request links expire 24 hours after creation.</b><img src = 'http://" + local_ip + ":5000/pixel.gif' width='1' height='1'></img>"
    text = ID
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:  
        server = smtplib.SMTP_SSL(host, port)
        server.ehlo()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipient, msg.as_string())
        server.close()
    except Exception as e:
        print "Error: ", e
    else:
        print "Email sent!"