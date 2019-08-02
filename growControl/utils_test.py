'''
Tests for utils file
'''
from growControl.utils import CircularBuffer


def nums_close(a,b,tol=1e-6):
    '''
    Test if 2 values are withing a specified tolerance
    '''
    if abs(a-b) <tol:
        return True
    else:
        return False

def list_close(a,b,tol=1e-6):
    '''
    Element wise testing of 2 lists to see if the values are close
    '''
    for c,d in zip(a,b):
        if not nums_close(c,d,tol):
            return False
    return True

def test1():
    a = CircularBuffer(length=4)
    for ii in range(10):
        a.update(ii)    
    assert list_close(a.data,[8,9,6,7]),"CircularBuffer test1: Updates internal data incorrectly"
    assert nums_close(a.sum,30), "CircularBuffer test1: Incorrect sum"
    assert nums_close(a.average,7.5), "CircularBuffer test1: Incorrect Average"

test1()     
