'''
Created on 9 Jun 2017

@author: jdrumgoole
'''
import meetup.api

if __name__ == '__main__':
    client = meetup.api.Client()    
    client.api_key = "3d68251425b622f295c2b6d64796e66"
    
    for i in range( 50 ):
        members = client.GetMembers(group_urlname = "London-MongoDB-User-Group")
        print( members )