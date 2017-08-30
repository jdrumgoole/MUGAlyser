'''
Created on 28 Jun 2017

@author: jdrumgoole
'''

import logging


class Logger(object):
    '''
    Logging class that encapsulates logging interface
    '''


    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    
    def __init__(self, logger_name, log_level = None):
        self._logger = logging.getLogger( logger_name )
        self._log_level = Logger.LoggingLevel( log_level )
        if log_level :
            self._logger.setLevel( log_level )
        else:
            self._logger.setLevel( logging.INFO )
        
        self.add_stream_handler(log_level)
        
    @staticmethod
    def formatter():
        return logging.Formatter( Logger.format_string )
        
        
    def add_stream_handler(self, log_level = None ):
        sh = logging.StreamHandler()
        sh.setFormatter( Logger.formatter())
        if log_level :
            sh.setLevel( log_level )
        else:
            sh.setLevel( logging.INFO )
        self._logger.addHandler( sh )
        return self._logger
        
    def add_file_handler(self, logfile_name, log_level= None ):
        fh = logging.FileHandler( logfile_name )
        fh.setFormatter( Logger.formatter())
        if log_level :
            fh.setLevel( log_level )
        else:
            fh.setLevel( logging.INFO )
        self._logger.addHandler( fh )
        return self._logger
    
    def log(self):
        return self._logger
    
    @staticmethod 
    def LoggingLevel( level="WARN" ):

        loglevel = None
        if level == "DEBUG" :
            loglevel = logging.DEBUG 
        elif level == "INFO" :
            loglevel = logging.INFO 
        elif level == "WARNING" :
            loglevel = logging.WARNING 
        elif level == "ERROR" :
            loglevel = logging.ERROR 
        elif level == "CRITICAL" :
            loglevel = logging.CRITICAL
            
        return loglevel 