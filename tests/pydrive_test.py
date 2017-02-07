'''
Created on 23 Jan 2017

@author: jdrumgoole
'''
from pydrive import auth
from pydrive.drive import GoogleDrive
from argparse import ArgumentParser
import pprint
import json

if __name__ == '__main__':
    
    parser = ArgumentParser()
    
    parser.add_argument( "--config", default="pydrive_auth.json", help="Configuration file" )
    
    args = parser.parse_args()
    gauth = auth.GoogleAuth()
    
    gauth.LoadClientConfigFile( args.config )
    


    drive = GoogleDrive(gauth)
    
    
    files = drive.ListFile()
    
    for i in files:
        s = json.dumps( i )
        #pprint.pprint( s )
        
        for j in i:
            pprint.pprint( j["title"] )

        
    file1 = drive.CreateFile({'title': 'Hello-gdrive.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1.SetContentString('Hello World!') # Set content of the file from given string.
    file1.Upload()
    
    file2 = drive.CreateFile( )