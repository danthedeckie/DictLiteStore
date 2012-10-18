#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
DictLiteStore.py
(C) 2012 Daniel Fairhead

A Very simple module for storing schemaless / quasi-random dictionaries into a
sqllite store. All values are stored as json in the database, which means it's
still very easy to parse & query.

Usage:

>>> foo = {'title':'Foo the first','dict':'Bar Bar Bar'}
>>> bucket = DictLiteStore('data.db','table_of_random_stuff')
>>> bucket.store(foo)
1

Now the dictionary 'foo' is stored as a row in data.db
You can either use SQLlite queries directly to access the data,
or there is a very simple select wrapper which can be helpful for simple
stuff:

>>> bucket.select(('title','LIKE','%Foo%'))
[{'title':'Foo the first','dict':'Bar Bar Bar'}]


"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sqlite3 as lite
import json

# These are the allowed operators for select()
_where_operators = [
    '||',
    '*','/','%',
    '+','-',
    '<<','>>','&', '|',
    '<','<=','>','>=',
    '=','==','!=','<>','IS','IS NOT','IN','LIKE','GLOB','MATCH','REGEXP']

def clean(unclean):
    ''' Makes a string safe (and unicode) to use as
        a column name in a SQLlite query '''
    return unicode(unclean.replace('"','""'))

def cleanq(unclean):
    ''' Cleans a string, and sticks quotes around it, for use in 
        SQLlite queries. '''
    return u'"' + unicode(unclean.replace('"','""')) + u'"'


class DictLiteStore(object):

    def __init__(self, db_name=":memory", table_name=u"def"):
        self.db_name = db_name
        self.table_name = clean(table_name)

    def __enter__(self):
        self.db = lite.connect(self.db_name)
        self.db.row_factory = lite.Row
        self.cur = self.db.cursor()

        self.cur.execute(u"CREATE TABLE IF NOT EXISTS \"{0}\"(Id INT)".format(self.table_name))
        self.db.commit()

        self.sql_columns = []

        # Get current columns:
        self.cur.execute(u"PRAGMA table_info(\"{0}\")".format(self.table_name))

        # Add them to the sql_columns list:
        for row in self.cur.fetchall()[1:]:
            self.sql_columns.append(row[1])

        return self

    def __exit__(self, exptype, expvalue, exptb):
        self.db.commit()
        self.db.close()

    def store(self, doc):
        '''
        Store a dictionary (doc) in the database.
        Update the table columns as needed.
        '''
        columns = []
        data_spaces = []
        for _k,v in doc.items():
            # Clean the key:
            k = clean(_k)
            # If needed, add a new column to the self.db:
            if not k in self.sql_columns:
                sql = u"ALTER TABLE \"{0}\" " \
                      u"ADD COLUMN \"{1}\"".format(self.table_name, k)
                self.cur.execute(sql)
                self.sql_columns.append(k)
            # Add this item to the list of stuff to commit:
            columns.append(u'"' + k + u'"')
            data_spaces.append(u'?')
        # Commit new columns:
        self.db.commit()

        # Prepare the data for writing.
        # *NOTE* this is lossy.  Un-jsonable data will simply
        #        be dropped into it's string version!
        safe_values = []
        for x in doc.values():
            safe_values.append(json.dumps(x, default=lambda x:unicode(x), ensure_ascii=False ))


        # Now finally add the data into the database:
        sql = u"INSERT INTO \"{0}\"({1}) VALUES({2})".format( \
                    self.table_name, \
                    u','.join(columns), \
                    u','.join(data_spaces))
        self.cur.execute(sql, safe_values)



    def select(self, *args, **vargs):
        ''' A wrapper around sqllite select (makes things a little safer,
            and simpler)

            Usage:

            >>> select(('title','LIKE','%foo%'), order='mtime')
            [ {'title': 'posts', 'other': 'are', 'data': 'returned'},
              {'title': 'here', 'other': 'as', 'rows': 'a'},
              {'title': 'list', 'more': 'of', 'stuff': 'dicts'} ]

        '''
        # Work around python not liking *args before named args.
        _options = {u'order': u'mtime'}
        _options.update(vargs)

        ####
        # Sanitize column names and operators:
        ####

        # collection boxes:
        where_clauses = []
        sql_values = []

        # work through inputs, sanitize 'em and put them in the collection:
        for (col, operator, value) in args:
            if not operator in _where_operators:
                raise KeyError, 'Invalid operator ({0})'.format(operator)
            where_clauses.append(u' '.join([cleanq(col), unicode(operator), u'(?)']))
            sql_values.append(value)

        # Prepare the query:
        sql = u'SELECT * FROM \"{0}\" {1} {2} ORDER BY ?'.format( \
            self.table_name, \
            u'WHERE' if len(args) != 0 else u'', \
            u' AND '.join(where_clauses))
        # Order by value gets tacked on the end:
        sql_values.append(cleanq(_options[u'order']))

        # Run the query, and parse the result(s).
        data = [dict(x) for x in self.cur.execute(sql, sql_values).fetchall()]
        for doc in data:
            for k,v in doc.items():
                if v == None:
                    del doc[k]
                else:
                    doc[k] = json.loads(v)

        # Return the newly parsed data:
        return data
