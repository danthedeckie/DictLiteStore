#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf_8')

from DictLiteStore import DictLiteStore

c = {'title':'complex','dict':{'this is a dict of dicts key':'with still good data'},
    'numbers':42,'lists':[1,1,2,3,5,8,13]}

d = {'not':'a','normal':'table'}
#d = {'title':'foo', 'data':'bar', 'name with space':'should work.',u'Ονομα':u'Αυτο unicode ειναι!'}

e = {'title':'this is invalid data for json','splat':lambda x: x+x}

silly = {'title':'silly','data':'also silly'}
x = []
with DictLiteStore('x.db') as s, open('f.txt','w') as f:

    s.store(c)
    s.store(d)
    s.store(e)
    s.store(silly)

    s.update({'title':'SILLY'}, False, ('title','==','silly'), ('elphant','==','here'))

    print 'retreving data:'
    x = s.get()

    print 'dumping SQL:'

    print u'\n'.join([unicode(x) for x in s.db.iterdump()])
