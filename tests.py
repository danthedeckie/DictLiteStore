#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Tests for DictLiteStore.
# Requires 'nose' testing framework.
# 'pip install nose' should get it for you,
# and then run 'nosetests' in this directory.
# or 'nosetests -d' to get more debugging info.


from DictLiteStore import DictLiteStore

###########################################
#
# Two boilerplate removal functions for later:
#
###########################################

def store_and_get(d):
    ''' stores a dictionary in a :memory: / default DictLiteStore,
        and returns the first row of querying that table. '''

    with DictLiteStore() as s:
        s.store(d)
        dd = s.get()

        assert len(dd) == 1

        return dd[0]

def store_and_compare(original, result=False):
    ''' stores a dictionary, retrieves it again,
        and compares with an expected result. '''
    retrieved = store_and_get(original)

    if not result:
        assert retrieved == original
    else:
        assert retrieved == result

#########################################
#
# Very simple store and return tests for basic data types.
#
#########################################

def test_text_only():
    a = {'row1':'data1', 'row2':'data2'}
    store_and_compare(a)

def test_unicode_text():
    a = {'rowενα':u'πραγμα', 'rowδυο':'älles güt'}
    store_and_compare(a)

def test_int():
    a = {'row1': 42}
    store_and_compare(a)

def test_float():
    a = {'row1': 3.14 }
    store_and_compare(a)

def test_list():
    a = {'row1':['this','is','a','list']}
    store_and_compare(a)

def test_unicode_list():
    a = {'row1':['αὐτο','είναι','εναν', 'unicode', 'list']}
    store_and_compare(a)

def test_dict():
    a = {'row1':{'subdict':'value'}}
    store_and_compare(a)

def test_function():
    a = {'row1':'should work', 'row2': map}
    b = {'row1':'should work', 'row2': '<built-in function map>'}
    store_and_compare(a, b)

def test_class():

    c = object()

    a = {'row1': c }

    b = store_and_get(a)
    assert b['row1'].startswith('<object object at')

##########################################
#
# OK. We've passed basic sanity tests,
# let's try doing more interesting tests.
#
##########################################
