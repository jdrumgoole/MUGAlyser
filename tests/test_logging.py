import logging

if __name__ == "__main__":
    print( "Start")
    logger = logging.getLogger( "test" )
    logger.setLevel( logging.DEBUG )
    fh = logging.FileHandler( "test.log" )
    sh = logging.StreamHandler()
    fh.setLevel( logging.DEBUG )
    sh.setLevel( logging.DEBUG )
    fh.setFormatter( logging.Formatter( "%(asctime)s - %(name)s - %(levelname)s - %(message)s" ))
    sh.setFormatter(  logging.Formatter( "%(asctime)s - %(name)s - %(levelname)s - %(message)s" ))
    
    logger.addHandler( sh )
    logger.addHandler( fh )
    
    logger.info( "Logging to  meetuprequests.log and stdout" )
    print( "end")