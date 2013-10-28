=============
DictLiteStore
=============

A dynamic-schema sqlite backend for storing python dicts in a queriable
database.

All values within the dict are stored as json values
in the database, but the keys are mapped into table columns, So you can
query things , while it's still very easy to parse.

When you try to add a dict which has keys which *aren't* in the table
already, it will automatically add those columns.

So a dict: ::

    {'author': 'dan',
     'project': 'DictLiteStore',
     'categories': ['python', 'dict', 'persistance']
    }

becomes in the database:


+-----------+---------------------+---------------------------------------+
| AUTHOR    |  PROJECT            |   CATEGORIES                          |
+===========+=====================+=======================================+
| ``"dan"`` | ``"DictLiteStore"`` | ``["python", "dict", "persistance"]`` |
+-----------+---------------------+---------------------------------------+

This is quite cool, as you can then use regular SQL to query stuff. ::

    SELECT * FROM 'dict_store' WHERE 'author' == '"dan"'

for instance. (Note the quotes around the query value.)  There is a
simple wrapper around the sql select function (get) that you can use if you
don't want to run type sql yourself. See the Usage section below.

Since the data is in json form, even for lists (like categories) you
can fairly easily query it too.  Search for all rows with 'python' in
categories, say.  Sqllite full-text searches are reasonably fast.
You don't get the performance benefits of one-to-many relationship
queries, but if you're in a performance critical environment, you
should probably be looking at a 'real' SQL server anyway.

When the data is returned from sqllite, if you use the
'get' function in the DictLiteStore module, it will re-convert
jsonified values (say that 'categories' list) back into a python
list.  This is quite useful. :-)

DictLiteStore was initially just an experiment for a later part of
marlinespike's cacheing system, but as a stand-alone module,
is useful for many data storage systems.

======
Usage:
======

Take a dict of data::

    foo = {'title': 'Foo the first', 'dict':'Bar Bar Bar'}

    with DictLiteStore('data.db', 'table_of_random_stuff') as bucket:
        bucket.store(foo)

Now the dictionary 'foo' is stored as a row in data.db

---------
Retrieval
---------

You can either use SQLlite queries directly to access the data,
or there is a very simple SELECT wrapper which can be helpful for simple
stuff: ::

    bucket.get(('title', '==', 'Foo the first'))

Or using other SQL operators, such as LIKE: ::

    bucket.get(('title', 'LIKE', NoJSON('%Foo%')))

(The NoJSON wrapper stops DictLiteStore from trying to be clever and JSON escaping
the `%Foo%` string into `"%Foo%"`, which in this instance might actually work, but
can be puzzling and annoying.)

Both of those queries return ::

    [{'title':'Foo the first','dict':'Bar Bar Bar'}]

You can also query the database yourself directly if you want with normal SQL: ::

    SELECT * from "table_of_random_stuff" WHERE "title" == '"Foo the first"';

--------
Updating
--------

To update the table, you also use the update() method: ::

    bucket.update({'title':'updated title'})

would update *all* rows to have the new title.  We can use the 'where' clause
like in get to limit the damage: ::

    bucket.update({'title': 'updated title'},
                  True,
                  ('title', '==', 'old title'))

What's that random 'True' there for, you want to know?

The update method needs to know if you want it to write the dict (insert it)
into the table if the where clause fails.  If you want to ONLY update, and not
insert if there is no matching row, then run update like this: ::

    bucket.update({'title':'updated title'},
                  False,
                  ('title','==','old title'))

----------
JSON Lists
----------

One useful feature of going through JSON, is that all items in a list get stored
comma (and quote) separated.  So, say you're storing a bunch of tags on a document: ::

    bucket.store({'title': 'Why is Juggling fun?',
                  'content': 'blah blah',
                  'tags': ['juggling', 'hobbies', 'fun stuff', 'etc']})

You can then search specific tags, using the `'LIKE'` operator, and NoJSON, as before: ::

    return bucket.get(('tags', 'LIKE', NoJSON('%"' + tagname + '"%'))

Obviously, this is nothing like as fast or scalable as doing "real SQL" using cross
reference tables and so on.  However, for the small, light, dirt-quick-and-easy projects
DictLiteStore is intended for, it should be fine.

======
Notes:
======

* All data is serialised into json before writing, and deserialised on the way out.
  This means strings do get extra quotes around them.  There could be a way to do this better,
  but I'm not quite sure of the most efficient. (Try and deserialise, if it doesn't work,
  leave as string?  Too many false positives, I'd have thought...)
* All non-jsonable data is stringified first, and then json'd.
* Currenly very little error-checking happens.  Before production, this needs
  a lot of shoring-up around the edges.
* I need to do some performance experiments!  How well does this actually work, speed wise?
