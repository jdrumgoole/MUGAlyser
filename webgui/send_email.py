import boto3

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
sender = "sender@example.com"

# Replace recipient@example.com with a "To" address. If your account 
# is still in the sandbox, this address must be verified.
recipient = "recipient@example.com"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
awsregion = "us-west-2"

# The subject line for the email.
subject = "Amazon SES Test (SDK for Python)"

# The HTML body of the email.
htmlbody = """<h1>Amazon SES Test (SDK for Python)</h1><p>This email was sent with 
            <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the 
            <a href='https://aws.amazon.com/sdk-for-python/'>AWS SDK for Python (Boto)</a>.</p>"""

# The email body for recipients with non-HTML email clients.  
textbody = "This email was sent with Amazon SES using the AWS SDK for Python (Boto)"

# The character encoding for the email.
charset = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=awsregion)

# Try to send the email.
try:
    #Provide the contents of the email.
    response = client.send_email(
        Destination={
            'ToAddresses': [
                recipient,
            ],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': charset,
                    'Data': htmlbody,
                },
                'Text': {
                    'Charset': charset,
                    'Data': textbody,
                },
            },
            'Subject': {
                'Charset': charset,
                'Data': subject,
            },
        },
        Source=sender,
    )
# Display an error if something goes wrong.	
except Exception as e:
    print "Error: ", e	
else:
    print "Email sent!"