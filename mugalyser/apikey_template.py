MEETUP_API_KEY=""

import os

def get_meetup_key( default=MEETUP_API_KEY ):
    return os.getenv( "MEETUP_API_KEY", default )