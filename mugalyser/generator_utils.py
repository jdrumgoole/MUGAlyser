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

def printCount( iterator, printfunc=None ):
    count = 0
    for i in iterator :
        count = count + 1
        if printfunc is None:
            pprint( i )
        else:
            printfunc( i )
    print( "Total: %i" % count )