# DictLiteStore alpha
# WORK IN PROGRESS

A Very simple module for storing schemaless / quasi-random dictionaries into a
sqllite store. All values are stored as json in the database, which means it's
still very easy to parse & query.

##Usage:

```python

foo = {'title':'Foo the first','dict':'Bar Bar Bar'}
bucket = DictLiteStore('data.db','table_of_random_stuff')
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

This is initially just an experiment for a later part of marlinespike cacheing system,
but as a stand-alone module, could also be pretty useful.

## Notes:

- All data is serialised into json before writing, and deserialised on the way out.
- All non-jsonable data is stringified first, and then json'd.
- Currenly very little error-checking happens.  Before production, this needs
  a lot of shoring-up around the edges.
- I need to do some performance experiments!  How well does this actually work, speed wise?
