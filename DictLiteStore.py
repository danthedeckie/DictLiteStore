"""
A Very simple module for storing schemaless / quasi-random dictionaries into a
sqllite store.

Usage:

>>> foo = {'title':'Foo the first','dict':'Bar Bar Bar'}
>>> bucket = DictLiteStore('data.db','table_of_random_stuff')
>>> bucket.store(foo)
1

Now the dictionary 'foo' is stored as a row in data.db

>>> bucket.select(('title','LIKE','%Foo%'))
[{'title':'Foo the first','dict':'Bar Bar Bar'}]

Returns things reasonably easily.  For more complex queries, just use sqllite
straight.  Or SQLalchemy or something.

"""

import sqlite3 as lite

# These are the allowed operators for select()
_where_operators = [
    '||',
    '*','/','%',
    '+','-',
    '<<','>>','&', '|',
    '<','<=','>','>=',
    '=','==','!=','<>','IS','IS NOT','IN','LIKE','GLOB','MATCH','REGEXP']


def clean(unclean):
    ''' Makes a string safe to use as a column name in a SQLlite query.'''
    return unclean.translate(None, '\'"`;=!{}[]-+*&^\\%$@()')


class DictLiteStore(object):

    def __init__(self, db_name=":memory:", table_name="def"):
        self.db = lite.connect(db_name)
        self.db.row_factory = lite.Row
        self.cur = self.db.cursor()
        self.table_name = clean(table_name)

        self.cur.execute("CREATE TABLE IF NOT EXISTS {0}(Id INT)".format(self.table_name))
        self.db.commit()

        self.sql_columns = []


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
                sql = "ALTER TABLE {0} " \
                      "ADD COLUMN {1}".format(self.table_name, k)
                self.cur.execute(sql)
                self.sql_columns.append(k)
            # Add this item to the list of stuff to commit:
            columns.append(k)
            data_spaces.append('?')
        # Commit new columns:
        self.db.commit()

        # Now finally add the data into the database:
        sql = "INSERT INTO {0}({1}) VALUES({2})".format( \
                    self.table_name, \
                    ','.join(columns), \
                    ','.join(data_spaces))
        self.cur.execute(sql, [str(x) for x in doc.values()])



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
        _options = {'order': 'mtime'}
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
            where_clauses.append(' '.join([clean(col), operator, '(?)']))
            sql_values.append(value)

        # Prepare the query:
        sql = 'SELECT * FROM {0} {1} {2} ORDER BY ?'.format( \
            self.table_name, \
            'WHERE' if len(args) != 0 else '', \
            ' AND '.join(where_clauses))
        print (sql)
        # Order by value gets tacked on the end:
        sql_values.append(clean(_options['order']))

        # Run the query, and return the result(s).
        return [dict(x) for x in self.cur.execute(sql, sql_values).fetchall()]


