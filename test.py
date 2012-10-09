from DictLiteStore import DictLiteStore

c = {'title':'complex','dict':{'this is a dict of dicts key':'with still good data'},
    'numbers':42,'lists':[1,1,2,3,5,8,13]}

d = {'title':'foo', 'data':'bar'}

e = {'title':'this is invalid data for json','splat':lambda x: x+x}

s = DictLiteStore()

s.store(c)
s.store(d)
s.store(e)

print str(s.select())

print '\n'.join(s.db.iterdump())
