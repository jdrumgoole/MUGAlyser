'''
Created on 22 Nov 2016

@author: jdrumgoole
'''
from pprint import pprint
def coroutine(func):
    def start( *args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr

    return start

def printCount( iterator, format_type=None, printFunc=pprint  ):
    count = 0
    for i in iterator :
        count = count + 1
        if format_type is None:
            printFunc( i )
        else:
            printFunc( i, format_type  )
    print( "Total: %i" % count )