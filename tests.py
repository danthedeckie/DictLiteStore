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
        and returns all rows in that table '''

    with DictLiteStore() as s:
        s.store(d)
        dd = s.get()

        assert len(dd) == 1

        return dd

def store_and_compare(original, result=False):
    ''' stores a dictionary, retrieves it again,
        and compares with an expected result. '''
    retrieved = store_and_get(original)[0]

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
    a = {'col1':'data1', 'col2':'data2'}
    store_and_compare(a)

def test_unicode_text():
    a = {'colενα':u'πραγμα', 'colδυο':'älles güt'}
    store_and_compare(a)

def test_int():
    a = {'col1': 42}
    store_and_compare(a)

def test_float():
    a = {'col1': 3.14 }
    store_and_compare(a)

def test_list():
    a = {'col1':['this','is','a','list']}
    store_and_compare(a)

def test_unicode_list():
    a = {'col1':['αὐτο','είναι','εναν', 'unicode', 'list']}
    store_and_compare(a)

def test_dict():
    a = {'col1':{'subdict':'value'}}
    store_and_compare(a)

def test_function():
    a = {'col1':'should work', 'col2': map}
    b = {'col1':'should work', 'col2': '<built-in function map>'}
    store_and_compare(a, b)

def test_class():

    c = object()

    a = {'col1': c }

    b = store_and_get(a)[0]
    assert b['col1'].startswith('<object object at')

##########################################
#
# OK. We've passed basic sanity tests,
# let's try doing more interesting tests.
#
##########################################

# some generic data:
ROW1 = {'col1':'data1', 'col2':'data2'}
ROW2 = {'col3':'data3', 'col4':'data4'}
# a generic update:
UPDATE1 = {'col1':'UPDATED'}
# a generic WHERE clause, which matches ROW1
GOODWHERE = ('col1','==','data1')
# a generic WHERE clause, which doesn't match
BADWHERE = ('col1','==','bogus')

# a couple of boilerplate reduction functions:

def copy_change(original, updates):
    # I suspect there is a standard library function for this.
    new = original.copy()
    new.update(updates)
    return new

# And the update tests:

def test_multiple_rows_same_columns():
    with DictLiteStore() as s:
        s.store(ROW1)
        s.store(ROW1)

        c = s.get()

        assert c == [ROW1, ROW1]

def test_rows_with_different_columns():

    with DictLiteStore() as s:
        s.store(ROW1)
        s.store(ROW2)

        c = s.get()

        assert c[0] == ROW1
        assert c[1] == ROW2


def test_update_all_rows_with_one_entry():

    post_update = copy_change(ROW1, UPDATE1)

    with DictLiteStore() as s:
        s.store(ROW1)

        s.update(UPDATE1)

        from_db = s.get()

        assert from_db[0] == post_update


def test_update_all_rows_with_multiple_entries():

    post_update_a = copy_change(ROW1, UPDATE1)
    post_update_b = copy_change(ROW2, UPDATE1)

    with DictLiteStore() as s:
        s.store(ROW1)
        s.store(ROW2)

        s.update(UPDATE1)

        from_db = s.get()

        assert from_db[0] == post_update_a
        assert from_db[1] == post_update_b


def test_update_single_row():

    post_update_a = copy_change(ROW1, UPDATE1)

    with DictLiteStore() as s:
        s.store(ROW1)
        s.store(ROW2)

        s.update(UPDATE1, False, GOODWHERE)

        from_db = s.get()

        assert from_db[0] == post_update_a
        assert from_db[1] == ROW2

def test_update_fallbackto_insert():

    with DictLiteStore() as s:
        s.store(ROW1)

        s.update(UPDATE1, True, BADWHERE)

        from_db = s.get()

        assert from_db[0] == ROW1
        assert from_db[1] == UPDATE1


def test_update_fallbackto_nothing():

    with DictLiteStore() as s:
        s.store(ROW1)

        s.update(UPDATE1, False, BADWHERE)

        from_db = s.get()

        assert len(from_db) == 1
        assert from_db[0] == ROW1

def test_update_empty_table():
    with DictLiteStore() as s:
        s.update(UPDATE1, False, BADWHERE)

        from_db = s.get()

        assert from_db == []

def test_update_empty_table_fallbackto_insert():
    with DictLiteStore() as s:
        s.update(UPDATE1, True, BADWHERE)

        from_db = s.get()

        assert from_db == [UPDATE1]

# 'Bad Names' (for columns) tests:

def test_various_badnames():
    a = {'"col1':'data1', 'col2':'data2'}
    store_and_compare(a)

    a = {'"':'data1', 'col2':'data2'}
    store_and_compare(a)

    a = {'""':'data1', 'col2':'data2'}
    store_and_compare(a)

    a = {'\"':'data1', 'col2':'data2'}
    store_and_compare(a)

    a = {'(':')'}
    store_and_compare(a)

    a = {'\'':'data1'}
    store_and_compare(a)

    a = {';':'data1'}
    store_and_compare(a)

# TODO:
# - test writing to a file.
# - test a different table name.
# - test deletion
# - test custom SQL schema databases.
