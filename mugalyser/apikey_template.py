MEETUP_API_KEY="AAAA"

import os

def get_meetup_key( default=MEETUP_API_KEY ):
    key = os.getenv( "MEETUP_API_KEY", default )
    if ( key == "AAAA" ):
        raise ValueError( "Invalid API key for meetup : %s" % key )
    else:
        return key
