# DictLiteStore alpha
# WORK IN PROGRESS

A Very simple module for storing schemaless / quasi-random dictionaries into a
sqllite store. All values within the dict are stored as json values in the database,
but the keys are mapped into table columns, So you can query things , while
it's still very easy to parse.

When you try to add a dict which has keys which *aren't* in the table
already, it will automatically add those columns.

So a dict:

```python
{'author': 'dan',
 'project': 'DictLiteStore',
 'categories': ['python', 'dict', 'persistance']
}
```

becomes in the database:

```
AUTHOR | PROJECT          | CATEGORIES
"dan"    "DictLiteStore"    ['python', 'dict', 'persistance']
```

This is quite cool, as you can then use regular SQL to query stuff.


```sql
SELECT * FROM 'dict_store' WHERE 'author' == '"dan"'
```

for instance. (Note the quotes around the query value.)  There is a
simple wrapper around the sql select function that you can use if you
don't want to run type sql yourself. See the Usage section below.

Since the data is in json form, even for lists (like categories) you
can fairly easily query it too.  Search for all rows with 'python' in
categories, say.  Sqllite full-text searches are reasonably fast.
You don't get the performance benefits of one-to-many relationship
queries, but if you're in a performance critical environment, you
should probably be looking at a 'real' SQL server anyway.

When the data is returned from sqllite, if you use the
'select' function in the DictLiteStore module, it will re-convert
jsonified values (say that 'categories' list) back into a python
list.  This is quite useful. :-)

DictLiteStore is initially just an experiment for a later part of marlinespike
cacheing system, but as a stand-alone module, could also be pretty useful.


##Usage:

```python

foo = {'title':'Foo the first','dict':'Bar Bar Bar'}
with DictLiteStore('data.db','table_of_random_stuff') as bucket:
    bucket.store(foo)

```

Now the dictionary 'foo' is stored as a row in data.db
You can either use SQLlite queries directly to access the data,
or there is a very simple select wrapper which can be helpful for simple
stuff:

```python
bucket.select(('title','LIKE','%Foo%'))
```
returns
```python
[{'title':'Foo the first','dict':'Bar Bar Bar'}]
```

To update the table, you also use the update() method:

```python
bucket.update({'title':'updated title'})
```

would update *all* rows to have the new title.  We can use the 'where' clause
like in select to limit the damage:

```python
bucket.update({'title':'updated title'},
    True,
    ('title','==','old title'))
```

What's that random 'True' there for, you want to know?

The update method needs to know if you want it to write the dict (insert it)
into the table if the where clause fails.  If you want to ONLY update, and not
insert if there is no matching row, then run update like this:

```python
bucket.update({'title':'updated title'},
    False,
    ('title','==','old title'))
```



## Notes:

- All data is serialised into json before writing, and deserialised on the way out.
  This means strings do get extra quotes around them.  There could be a way to do this better,
  but I'm not quite sure of the most efficient. (Try and deserialise, if it doesn't work,
  leave as string?  Too many false positives, I'd have thought...)
- All non-jsonable data is stringified first, and then json'd.
- Currenly very little error-checking happens.  Before production, this needs
  a lot of shoring-up around the edges.
- I need to do some performance experiments!  How well does this actually work, speed wise?
