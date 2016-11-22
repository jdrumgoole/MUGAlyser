MEETUP_API_KEY=""
MUGALYSER_PASSWD=""

import os

def get_meetup_key( default=MEETUP_API_KEY ):
    return os.getenv( "MEETUP_AP_KEY", default )

def get_mugalyer_passwd( default=MUGALYSER_PASSWD ):
    return os.getenv( "MUGALYSER_PASSWD", default )