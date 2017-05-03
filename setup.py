'''
Created on 30 Sep 2016

@author: jdrumgoole
'''
from setuptools import setup, find_packages
from mugalyser.version import __version__, __programName__
import os

pyfiles = [ f for f in os.listdir( "." ) if f.endswith( ".py" ) ]

    
setup(
    name = __programName__,
    version = __version__,
    
    author = "Joe Drumgoole",
    author_email = "joe@joedrumgoole.com",
    description = "MUGAlyser - a script to extract data from Meetup into a MongoDB database",
    long_description =
    '''
MUGLyser uses the meetup API to capture data into a MongoDB Database. The 
app/mugalyser_main.py program reads this data via the API. You will need a meetup API
key to read this data. If you have a Meetup pro account you can use the --pro option. 
You can analyse the data with apps/mug_analytics_main.py
''',

    license = "AGPL",
    keywords = "Meetup MUGS MongoDB API",
    url = "https://github.com/jdrumgoole/MUGAlyser",
    
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',


        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7' ],
   
    install_requires = [ "requests", "pymongo", "mongodb_utils", "nose" ],
       
    packages = find_packages(),
    
    scripts  = [ "bin/getstats.sh",
                 "bin/makeapikeyfile_main.py",
                 "bin/meetup_info_main.py",
                 "bin/mug_analytics_main.py",
                 "bin/mug_db_setup.py",
                 "bin/mugalyser_main.py",
                 "bin/muginfo_main.py",
                 "bin/mugs.sh",
                 "bin/pugs.sh",
                 "bin/range_query.sh",
                 "bin/run_prog.sh",
                 "bin/update_atlas.sh" ],

    test_suite='nose.collector',
    tests_require=['nose'],
)
