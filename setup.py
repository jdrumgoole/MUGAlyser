'''
Created on 30 Sep 2016

@author: jdrumgoole
'''
from setuptools import setup, find_packages
from shutil import copyfile

copyfile( "README.md", "README")

setup(
    name = "MUGAlyser",
    version = "0.5",
    packages = find_packages(),
    
    author = "Joe Drumgoole",
    author_email = "joe@joedrumgoole.com",
    description = "MUGAlyser - a script to extract data from Meetup into a MongoDB database",
    license = "AGPL",
    keywords = "Meetup MUGS MongoDB API",
    url = "https://github.com/jdrumgoole/MUGAlyser"
)