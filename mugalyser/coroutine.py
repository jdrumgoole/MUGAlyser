'''
Created on 22 Nov 2016

@author: jdrumgoole
'''
def coroutine(func):
    def start( *args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr

    return start
