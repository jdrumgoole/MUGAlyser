'''
Created on 1 Nov 2016

@author: jdrumgoole
'''
import logging
from version import __programName__
            
class Feedback(object):
    '''
    classdocs
    '''

    def __init__(self ):
        '''
        Constructor
        '''
        self._report = self.report()
        self._report.next()
        
    def report(self):
        while True:
            line = (yield)
            if line is None:
                break
            else:
                logging.info( line )
                #print( line )
                
    def output(self, line ):

        logging.info( line )
        
    
