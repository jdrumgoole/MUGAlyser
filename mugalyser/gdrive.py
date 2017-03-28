'''
Created on 24 Mar 2017

@author: jdrumgoole
'''

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/drive.metadata.readonly'


homedir=os.getenv( "HOME")

CLIENT_SECRET_FILE = os.path.join(  homedir, 'pydrive_auth.json' )

class GDrive( object ):
    
    def __init__(self, application_name = "gdrive", client_secret_file=CLIENT_SECRET_FILE, credentials_dir=".credentials" ):
        self._client_secret_file = client_secret_file
        self._application_name = application_name
        self._scopes = 'https://www.googleapis.com/auth/drive.file'
        home_dir = os.path.expanduser('~')
        self._credential_dir = os.path.join(home_dir, credentials_dir )
        self._credentials_dir = credentials_dir
        if not os.path.exists( self._credential_dir):
            os.makedirs( self._credential_dir)
        self._credential_path = os.path.join( self._credential_dir,
                                              self._application_name + ".json" )
        
        self._secret_path = os.path.join( self._credential_dir, "pydrive_auth.json")
        
        self._credentials = None
        self._http = None
        self._service = None
        self.get_credentials()
        
    def get_credentials( self ):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
    
        store = Storage(self._credential_path)
        self._credentials = store.get()
        if not self._credentials or self._credentials.invalid:
            flow = client.flow_from_clientsecrets( self._secret_path, self._scopes )
            flow.user_agent = self._application_name
            self._credentials = tools.run_flow(flow, store )
            
        self._http = self._credentials.authorize(httplib2.Http())
        self._service = discovery.build('drive', 'v2', http=self._http)
        return self._credentials

    def upload_csvFile( self, folder_id, source_filename, target_filename=None ):
        return self.upload_file( folder_id, source_filename, 
                                 source_mimetype="text/csv", 
                                 target_mimetype="application/vnd.google-apps.spreadsheet", 
                                 target_filename=target_filename )
        
    def upload_file( self,  folder_id, source_filename, source_mimetype, target_mimetype, target_filename=None ):
        
        if target_filename is None :
            target_filename = os.path.basename( source_filename )
            target_filename = os.path.splitext( target_filename )[0]
            
        file_metadata = {
          'title' : target_filename,
          'mimeType' : target_mimetype,
          'parents': [{ 'id': folder_id }]
        }
        media = MediaFileUpload( source_filename,
                                 mimetype= source_mimetype,
                                 resumable=True)
        
        file_obj = self._service.files().insert(body=file_metadata,
                                                media_body=media,
                                                fields='id').execute()
    
        return ( target_filename, file_obj.get( "id"))
    
        #print( 'File ID: %s' % file_obj.get( "id"))

    def service(self):
        return self._service
