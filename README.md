# DictLiteStore alpha initial tests
# WORK IN PROGRESS

An experiment for a later part of marlinespike cacheing.

## Notes:

- All data is serialised into json before writing, and deserialised on the way out.
- All non-jsonable data is stringified first, and then json'd.
- Currenly very little error-checking happens.  Before production, this needs
  a lot of shoring-up around the edges.
