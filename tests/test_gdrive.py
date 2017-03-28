'''
Created on 24 Mar 2017

@author: jdrumgoole
'''

from __future__ import print_function
import httplib2
import os
import time

from mugalyser.gdrive import GDrive

    
def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    
    gdrive = GDrive()
    gdrive.get_credentials()
    results = gdrive.service().files().list(maxResults=10).execute()
    items = results.get('items', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['title'], item['id']))

    now =str(int(time.time()))
    
    new_name = now + "_events.csv"
    print( "uploading '%s' -> '%s'" % ( "events.csv", new_name ))
    
    spreadsheet_mime_type = "application/vnd.google-apps.spreadsheet"
    text_mime_type = "text/csv"
    
    gdrive.upload_csvFile( "0By1C8O_N6j4hbUd0cUJfZjAxOUU", "events.csv", now + "_events.csv")
    
if __name__ == '__main__':
    main()