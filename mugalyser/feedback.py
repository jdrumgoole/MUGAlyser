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
        self._logger = logging.getLogger( __programName__ )
        
    def report(self):
        while True:
            line = (yield)
            if line is None:
                break
            else:
                self._logger.info( line )
                #print( line )
                
    def output(self, line ):
        #print( "Logging to: %s" % __programName__ )
        #self._report.send( line )
        self._logger.propagate = False
        self._logger.info( line )
        
    
