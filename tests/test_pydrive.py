'''
Created on 23 Jan 2017

@author: jdrumgoole
'''
from pydrive import auth
from pydrive.drive import GoogleDrive
from argparse import ArgumentParser
import pprint
import json
import os

def listFile( f  ):
    return f[ 'title']

def listFolder( drive, f ):
    return {"id":f['id'],
            "title":f['title'], 
            "list" : listTree( drive, f[ 'id'] ) }
                               
def listTree(drive, parent):

    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if f['mimeType']=='application/vnd.google-apps.folder': # if folder
            yield listFolder( drive, f )
            #yield {"id":f['id'],"title":f['title'],"list": yield ListFolder(f['id'])}
        else:
            yield listFile( f )
  
if __name__ == '__main__':
    
    parser = ArgumentParser()
    
    home = os.getenv( "HOME" )
    credential_path = os.path.join( home, "pydrive_auth.json")
    parser.add_argument( "--config", default=credential_path, help="Configuration file" )
    
    args = parser.parse_args()
    gauth = auth.GoogleAuth()
    
    gauth.LoadClientConfigFile( args.config )

    drive = GoogleDrive(gauth)
    
    
    #files = drive.ListFile( {'q': "'root' in parents and trashed=false and name = 'Pangea'"})
    #files = drive.ListFile( {'q':"'root' in parents and name=Pangea"})
    #googleapiclient.errors.HttpError: <HttpError 400 when requesting https://www.googleapis.com/drive/v2/files?q=%27root%27+in+parents+and+name%3DPangea&alt=json returned "Invalid query">

    #files = drive.ListFile( {'q':"'root' in parents" }) # and name=Pangea"})
    #works
    
    #files = drive.ListFile( {'q':"'root' in parents and name = 'Pangea'"})
    #googleapiclient.errors.HttpError: <HttpError 400 when requesting https://www.googleapis.com/drive/v2/files?q=%27root%27+in+parents+and+name+%3D+%27Pangea%27&alt=json returned "Invalid query">
    
    files = listTree( drive, 'root' )
    for i in files:
        #s = json.dumps( i )
        pprint.pprint( i )
        
#         for j in i:
#             pprint.pprint( j )

        
    file1 = drive.CreateFile({'title': 'Hello-gdrive.txt'})  # Create GoogleDriveFile instance with title 'Hello.txt'.
    file1.SetContentString('Hello World!') # Set content of the file from given string.
    file1.Upload()
    
    file2 = drive.CreateFile( )