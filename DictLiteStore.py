#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
DictLiteStore.py
(C) 2012 Daniel Fairhead

This library is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

DictLiteStore

A Very simple module for storing schemaless / quasi-random dictionaries into a
sqllite store. All values are stored as json in the database, which means it's
still very easy to parse & query.

Usage:

>>> foo = {'title': 'Foo the first', 'dict': 'Bar Bar Bar'}
>>> with DictLiteStore('data.db', 'table_of_random_stuff') as bucket:
>>>     bucket.store(foo)
1

Now the dictionary 'foo' is stored as a row in data.db
You can either use SQLlite queries directly to access the data,
or there is a very simple select wrapper which can be helpful for simple
stuff:

>>> bucket.get(('title', '==', 'Foo the first'))
[{'title':'Foo the first','dict':'Bar Bar Bar'}]

or more realistically:

>>> bucket.get(('title', 'LIKE', NoJSON('%Foo%')))
[{'title':'Foo the first','dict':'Bar Bar Bar'}]

(Note the NoJSON wrapper, which allows the Querystring to go through unharmed.)


"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sqlite3 as lite
try:
    import simplejson as json
except ImportError:
    import json

import logging

log = logging.getLogger(__name__) #pylint: disable=invalid-name
log.addHandler(logging.NullHandler())

# These are the allowed operators for get()
_WHERE_OPERATORS = [  #pylint: disable=invalid-name
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


class NoJSON(unicode):
    ''' a string type, which should *not* be json dumped.  *Very* useful
        for queries '''
    pass

def json_or_raw(text):
    '''
    wrapper make NoJSON objects work easily.
    When the client (to the library) wants to pass something to SQL directly,
    and not have DictLiteStore wrap it in JSON, they use a NoJSON wrapper for
    the text.
    '''
    if isinstance(text, NoJSON):
        return text
    else:
        return json.dumps(text)


def _prepare_values(document):
    '''
    get the values from document, and turn them into safe json strings.
    *NOTE* this is lossy.  Un-jsonable data will simply
           be dropped into it's string version!
    '''
    return [json.dumps(x, default=unicode, ensure_ascii=False) \
         for x in document.values()]


################################################################################


class DictLiteStore(object):
    '''
    A simple(ish) way to store dict-like objects in a SQLite database,
    which can then be queried against.  Useful for caching schemaless data.
    '''

    def __init__(self, db_name=":memory:", table_name=u"def"):
        '''
        Initialise the object, but don't actually open the database
        connection yet.
        '''

        self.db_name = db_name
        self.table_name = clean(table_name)

    def open(self):
        '''
        open the connection to the database.
        if you call this function, remember to close() as well.
        '''

        self.db = lite.connect(self.db_name)
        self.db.row_factory = lite.Row
        self.cur = self.db.cursor()

        self.cur.execute(u'CREATE TABLE IF NOT EXISTS'
                          ' "{0}"(Id INT)'.format(self.table_name))
        self.db.commit()

        self.sql_columns = []

        # Get current columns:
        self.cur.execute(u"PRAGMA table_info(\"{0}\")".format(self.table_name))

        # Add them to the sql_columns list:
        for row in self.cur.fetchall()[1:]:
            self.sql_columns.append(row[1])

    def close(self):
        '''
        commit and close the database connection. if you use
        the 'with DictLiteStore(...) as ...' pattern, you don't need
        to call this.
        '''

        self.db.commit()
        self.db.close()

    def __enter__(self):
        ''' Open the database connection.
            Called in the 'with' pattern. '''
        self.open()
        return self

    def __exit__(self, exptype, expvalue, exptb):
        ''' Close the database connection.
            Called in the 'with' pattern. '''
        self.close()

    def _update_columns(self, document):
        ''' Update the table 'schema' to have any columns which the document
            has, but the table doesn't.
            Returns a list of the columns, quoted and ready to use
            in a query. '''

        columns = []
        for raw_key in document.keys():
            # Clean the key:
            key = clean(raw_key)

            # If needed, add a new column to the self.db:
            if key not in self.sql_columns:
                sql = u"ALTER TABLE \"{0}\" " \
                      u"ADD COLUMN \"{1}\"".format(self.table_name, key)
                self.cur.execute(sql)
                self.sql_columns.append(key)
            # Add this item to the list of stuff to commit:
            columns.append(u'"' + key + u'"')

        # Commit new columns:
        self.db.commit()

        return columns

    def store(self, document):
        '''
        Store a dictionary (doc) in the database.
        Update the table columns as needed.
        '''

        # Prepare the table, and get column names:
        columns = self._update_columns(document)

        # Prepare the data for writing:
        values = _prepare_values(document)

        # Prepare the query:
        sql = self._make_insert(columns)

        # Debug logging...
        log.debug ('SQL: %s DATA: %s', sql, values)

        # Run it!
        self.cur.execute(sql, values)

    def update(self, document, insert=True, *args):
        '''
        Update a row in the database.  If $insert is true,
        then insert the data as a new row, if nothing is updated.
        '''

        assert hasattr(document, 'items')

        # Prepare the table, and get column names:
        columns = self._update_columns(document)

        # Prepare the data for writing:
        values = _prepare_values(document)

        # Prepare the query:
        sql, where_values = self._make_update(columns, args)

        # Debug logging
        log.debug ('SQL: %s, DATA: %s, WHERE: %s', sql, values, where_values)

        self.cur.execute(sql, values + where_values)

        if self.cur.rowcount == 0 and insert:
            # No rows were modifed by query, and the user wants
            # us to insert a row if that's the case.
            sql = self._make_insert(columns)
            self.cur.execute(sql, values)

        return self.cur.rowcount

    def _make_insert(self, columns):
        '''
        Given a simple list of column names,
        return 'INSERT INTO "x"(column_names, etc) VALUES(?, ?)'
        '''

        return u'INSERT INTO "{0}"({1}) VALUES({2})'.format( \
                    self.table_name, \
                    u','.join(columns), \
                    u','.join(len(columns)*u'?'))

    def _make_update(self, columns, where):
        '''
        Given a list of columns, and a DictLiteStore style where clause,
        return ('UPDATE "x" SET a=(?),b=(?),c=(?) WHERE...', where_vals)
        '''

        # x=(?),y=(?),z=(?)
        update_clause = u','.join([c + u'=(?)' for c in columns])

        # WHERE ...
        where_clause, where_values = self._make_where_clause(*where)

        return u'UPDATE "{0}" SET {1} {2}'.format(
            self.table_name,
            update_clause,
            where_clause
            ), where_values

    def _make_where_clause(self, *args):
        '''
        given a list of three-tuples (column_name, operator, value)
        return the valid SQL version of it for use at the end of queries.
        '''

        if len(args) == 0:
            return u'', []

        # collection boxes:
        where_clauses = []
        sql_values = []

        # work through inputs, sanitize 'em and put them in the collection:
        for (col, operator, value) in args:
            if not operator in _WHERE_OPERATORS:
                raise KeyError, 'Invalid operator ({0})'.format(operator)
            where_clauses.append(u' '.join([cleanq(col),
                                            unicode(operator),
                                            u'(?)']))
            if isinstance(value, NoJSON):
                sql_values.append(value)
            else:
                sql_values.append(json.dumps(value))

        return u'WHERE' + u' AND '.join(where_clauses), sql_values

    def _make_order_clause(self, order_input=None):
        '''
        given a list of columns to order by,
        return the correct SQL to add into a query.
        '''

        if not order_input:
            return u''
        if not hasattr(order_input, '__iter__'):
            # probably a string? So stuff it in a tuple.
            order_input = (order_input,)

        order_segments = []
        for order in order_input:
            if len(order) == 2 and (order[1] == u'ASC' or order[1] == u'DESC'):
                log.debug('sorting by %s, %s.', order[0], order[1])
                if order[0] in self.sql_columns:
                    order_segments.append(cleanq(order[0]) + u' ' + order[1])
                else:
                    log.warn('Trying to sort (ORDER), '
                             'but "%s" is not a column.', order[0])
            elif order in self.sql_columns:
                order_segments.append(cleanq(order))

        if not order_segments:
            return u''

        return u'ORDER BY ' + u','.join(order_segments)


    def get(self, *args, **vargs):
        '''
        A wrapper around sqllite SELECT (makes things a little safer,
        and simpler)

        Usage:

        >>> bucket.get(('title','LIKE','%foo%'), order='mtime')
        [ {'title': 'posts', 'other': 'are', 'data': 'returned'},
        {'title': 'here', 'other': 'as', 'rows': 'a'},
        {'title': 'list', 'more': 'of', 'stuff': 'dicts'} ]

        '''
        # Work around python not liking *args before named args.
        _options = {u'order': u'id'}
        _options.update(vargs)

        ####
        # Sanitize column names and operators:
        ####

        where_clause, sql_values = self._make_where_clause(*args)

        # Order by value gets tacked on the end:
        order_clause = self._make_order_clause(_options[u'order'])

        # Prepare the query:
        sql = u'SELECT * FROM \"{0}\" {1} {2}'.format( \
            self.table_name, where_clause, order_clause)


        log.debug ('SQL: %s ; DATA: %s ;', sql, sql_values)
        # Run the query, and parse the result(s).
        data = [dict(x) for x in self.cur.execute(sql, sql_values).fetchall()]
        for document in data:
            log.debug('ROW: %s', document)
            for k, v in document.items():
                if v == None:
                    del document[k]
                else:
                    document[k] = json.loads(v)
        # Return the newly parsed data:
        return data
