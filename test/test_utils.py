from argschema import utils
import pytest
import operator

def test_merge_value_add():
    a = {'key':['a']}
    b = {'key':['b']}
    c=utils.merge_value(a,b,'key')
    assert(len(c)==2)

def test_merge_value_subtract():
    a = {'key':10}
    b = {'key':2}
    c=utils.merge_value(a,b,'key',operator.sub)
    assert(c==8)

def test_merge_value_fail():
    a = {'key':5}
    b = {}
    with pytest.raises(Exception):
        c=utils.merge_value(a,b,'key')

def test_smart_merge():
    a = {'a':5,'b':8}
    b = {'a':10}
    c = utils.smart_merge(a,b)
    assert(c['a']==10)
    assert(c['b']==8)

def test_smart_merge_same():
    a = {'a':3,'b':8}
    b = {'a':3}
    c = utils.smart_merge(a,b)
    assert(c['a']==3)
    assert(c['b']==8)

def test_smart_merge_add():
    a = {'a':[1],'b':8}
    b = {'a':[2]}
    c = utils.smart_merge(a,b,merge_keys=['a'])
    assert(len(c['a'])==2)
    assert(1 in c['a'])
    assert(2 in c['a'])

def test_smart_merge_not_none():
    a = {'a':1,'b':8}
    b = {'a':None}
    c = utils.smart_merge(a,b,merge_keys=['a'])
    assert(c['a']==1)

def test_smart_merge_none():
    a = {'a':1,'b':8}
    b = {'c':None}
    c = utils.smart_merge(a,b,merge_keys=['a'],overwrite_with_none=True)
    assert(c['c'] is None)

def test_smart_merge_nested():
    a = {'a':1,'b':{'c':4}}
    b = {'b':{'c':5,'d':9}}
    c = utils.smart_merge(a,b)
    assert(c['a']==1)
    assert(c['b']['c']==5)
    assert(c['b']['d']==9)
