#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Tests for DictLiteStore.
------------------------
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8') # pylint: disable=no-member

import os
import os.path
from dictlitestore import DictLiteStore
import unittest

# pylint: disable=missing-docstring, invalid-name, too-many-public-methods

###########################################
#
# Two boilerplate removal functions for later:
#
###########################################

class Basic(unittest.TestCase):
    def store_and_get(self, d):
        ''' stores a dictionary in a :memory: / default DictLiteStore,
            and returns all rows in that table '''

        with DictLiteStore() as s:
            s.store(d)
            dd = s.get()

            self.assertEqual(len(dd), 1)

            return dd

    def store_and_compare(self, original, result=False):
        ''' stores a dictionary, retrieves it again,
            and compares with an expected result. '''
        retrieved = self.store_and_get(original)[0]

        if not result:
            self.assertEqual(retrieved, original)
        else:
            self.assertEqual(retrieved, result)

#########################################
#
# Very simple store and return tests for basic data types.
#
#########################################

class TestBasicDataTypes(Basic):
    def test_text_only(self):
        a = {'col1':'data1', 'col2':'data2'}
        self.store_and_compare(a)

    def test_unicode_text(self):
        a = {'colενα': u'πραγμα', 'colδυο': 'älles güt'}
        self.store_and_compare(a)

    def test_int(self):
        a = {'col1': 42}
        self.store_and_compare(a)

    def test_float(self):
        a = {'col1': 3.14 }
        self.store_and_compare(a)

    def test_list(self):
        a = {'col1': ['this', 'is', 'a', 'list']}
        self.store_and_compare(a)

    def test_unicode_list(self):
        a = {'col1': ['αὐτο', 'είναι', 'εναν', 'unicode', 'list']}
        self.store_and_compare(a)

    def test_dict(self):
        a = {'col1':{'subdict':'value'}}
        self.store_and_compare(a)

    def test_function(self):
        a = {'col1':'should work', 'col2': map}
        b = {'col1':'should work', 'col2': '<built-in function map>'}
        self.store_and_compare(a, b)

    def test_class(self):

        c = object()

        a = {'col1': c }

        b = self.store_and_get(a)[0]
        self.assertTrue(b['col1'].startswith('<object object at'))

##########################################
#
# OK. We've passed basic sanity tests,
# let's try doing more interesting tests.
#
##########################################

# some generic data:
ROW1 = {'col1': 'data1', 'col2': 'data2'}
ROW2 = {'col3': 'data3', 'col4': 'data4'}

# a generic update:
UPDATE1 = {'col1': 'UPDATED'}

# a generic WHERE clause, which matches ROW1
GOODWHERE = ('col1', '==', 'data1')

# a generic WHERE clause, which doesn't match
BADWHERE = ('col1', '==', 'bogus')

# 'Bad Names' (for columns) tests:

SILLY_COLUMN_NAMES = ('"',      # "
                      '""',     # ""
                      '"col1',  # "col1
                      "'",      # '
                      "''",     # ''
                      '\\',     # \\
                      '(',      # (
                      ';',      # ;
                      'INSERT', # INSERT
                      '==',     # ==
                      '\";',    # \"
                      )

# a boilerplate reduction function:

def copy_change(original, updates):
    ''' makes a copy of dict $original, and updates it with $updates '''
    # I suspect there is a standard library function for this.
    new = original.copy()
    new.update(updates)
    return new

# And the update tests:

class TestUpdates(Basic):
    def test_multiple_rows_same_columns(self):
        with DictLiteStore() as s:
            s.store(ROW1)
            s.store(ROW1)

            c = s.get()

            self.assertEqual(c, [ROW1, ROW1])

    def test_rows_with_different_columns(self):

        with DictLiteStore() as s:
            s.store(ROW1)
            s.store(ROW2)

            c = s.get()

            self.assertEqual(c[0], ROW1)
            self.assertEqual(c[1], ROW2)


    def test_update_all_rows_with_one_entry(self):

        post_update = copy_change(ROW1, UPDATE1)

        with DictLiteStore() as s:
            s.store(ROW1)

            s.update(UPDATE1)

            from_db = s.get()

            self.assertEqual(from_db[0], post_update)


    def test_update_all_rows_with_multiple_entries(self):

        post_update_a = copy_change(ROW1, UPDATE1)
        post_update_b = copy_change(ROW2, UPDATE1)

        with DictLiteStore() as s:
            s.store(ROW1)
            s.store(ROW2)

            s.update(UPDATE1)

            from_db = s.get()

            self.assertEqual(from_db[0], post_update_a)
            self.assertEqual(from_db[1], post_update_b)


    def test_update_single_row(self):

        post_update_a = copy_change(ROW1, UPDATE1)

        with DictLiteStore() as s:
            s.store(ROW1)
            s.store(ROW2)

            s.update(UPDATE1, False, GOODWHERE)

            from_db = s.get()

            self.assertEqual(from_db[0], post_update_a)
            self.assertEqual(from_db[1], ROW2)

    def test_update_fallbackto_insert(self):

        with DictLiteStore() as s:
            s.store(ROW1)

            s.update(UPDATE1, True, BADWHERE)

            from_db = s.get()

            self.assertEqual(from_db[0], ROW1)
            self.assertEqual(from_db[1], UPDATE1)


    def test_update_fallbackto_nothing(self):

        with DictLiteStore() as s:
            s.store(ROW1)

            s.update(UPDATE1, False, BADWHERE)

            from_db = s.get()

            self.assertEqual(len(from_db), 1)
            self.assertEqual(from_db[0], ROW1)

    def test_update_empty_table(self):
        with DictLiteStore() as s:
            s.update(UPDATE1, False, BADWHERE)

            from_db = s.get()

            self.assertEqual(from_db, [])

    def test_update_empty_table_fallbackto_insert(self):
        with DictLiteStore() as s:
            s.update(UPDATE1, True, BADWHERE)

            from_db = s.get()

            self.assertEqual(from_db, [UPDATE1])

    def test_various_badnames_store_get_only(self):
        for x in SILLY_COLUMN_NAMES:

            a = {x:'data1', 'col2':'data2'}
            self.store_and_compare(a)


    def test_various_badname_update(self):
        for x in SILLY_COLUMN_NAMES:

            a = {x:'data1'}
            with DictLiteStore() as s:
                s.store(a)
                s.update({x:'UPDATED'})

                c = s.get()
                self.assertEqual(c, [{x:'UPDATED'}])



class TestUsingFile(unittest.TestCase):
    # Other tests:

    def test_db_file(self):
        # First test it doesn't already exist:
        self.assertEqual(os.path.exists('__test.db'), False)

        # Store some data:
        with DictLiteStore('__test.db') as s:
            s.store(ROW1)
            s.store(ROW2)

        # Should be saved.
        self.assertTrue(os.path.exists('__test.db'))

        # Retreive it again, check it's alright:
        with DictLiteStore('__test.db') as s:
            c = s.get()
            self.assertEqual(c, [ROW1, ROW2])

        # remove it.
        os.remove('__test.db')

        self.assertEqual(os.path.exists('__test.db'), False)

# TODO:
# - test a different table name.
# - test deletion
# - test custom SQL schema databases.


if __name__ == '__main__':
    try:
        import nose
        nose.run()
    except ImportError:
        unittest.main()
