import boto3

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
sender = "mugs@mugs.com"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
awsregion = "us-east-1"

# The subject line for the email.
subject = "MUGAlyser Password Reset"

# The character encoding for the email.
charset = "UTF-8"

# Create a new SES resource and specify a region.
client = boto3.client('ses',region_name=awsregion)

# Try to send the email.
def send(recipient, user, ID):
    htmlbody = "<p> Hey " + user + ", <p>click here to reset your password: <p><a href='http://127.0.0.1:5000/resetpw/" + ID + "'></a><p><b>Please note that password request links expire 24 hours after creation.</b>"
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
                        'Data': ID,
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