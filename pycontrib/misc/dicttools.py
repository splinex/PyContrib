'''
Created on Jul 3, 2015

@author: maxim
'''

def TreeDictToPlainDict(d):
    noneKey = 'noneKey271813'
    plain = dict()
    if type(d) == dict:             
        for key, val in d.items():
            for subKey, subVal in TreeDictToPlainDict(val).items():
                if not subKey == noneKey: 
                    plain['/{0}{1}'.format(key, subKey)]=subVal
                else:
                    plain['/{0}'.format(key)]=subVal
    elif type(d) in (list, tuple):
        for i in range(len(d)):
            for subKey, subVal in TreeDictToPlainDict(d[i]).items():
                if not subKey == noneKey:
                    plain['[{0}]{1}'.format(i, subKey)] = subVal
                else:
                    plain['[{0}]'.format(i)] = subVal
    else:
        plain[noneKey] = d
    return plain

def DictListLeveling(l):
    ans = list()
    allKeys = set()
    for d in l:
        allKeys.update(d.keys())
    allKeys = sorted(allKeys)
    for d in l:
        ansD = dict()
        for k in allKeys:
            ansD[k] = d.get(k, None)                
        ans.append(ansD)
    return ans

        