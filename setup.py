'''
Created on 30 Sep 2016

@author: jdrumgoole
'''
from setuptools import setup
import os

pyfiles = [ f for f in os.listdir( "." ) if f.endswith( ".py" ) ]

setup(
    name = "MUGAlyser",
    version = "0.6",
    
    author = "Joe Drumgoole",
    author_email = "joe@joedrumgoole.com",
    description = "MUGAlyser - a script to extract data from Meetup into a MongoDB database",
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
        'License :: OSI Approved :: AGPL',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7' ],
   
    install_requires = [ "requests", "pymongo", "nose" ],
       
    packages = [ "mugalyser"],
    
    package_data={
        'sample': ['MUGS'],
    }
)