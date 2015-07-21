'''
Created on Jul 3, 2015

@author: maxim
'''

def TreeDictToPlainDict(d, root=True):
    noneKey = 'noneKey271813'
    plain = dict()
    if type(d) == dict:             
        for key, val in d.items():
            for subKey, subVal in TreeDictToPlainDict(val, False).items():
                if not subKey == noneKey: 
                    plain['{dot}{0}{1}'.format(key, subKey, dot='' if root else '.')]=subVal
                else:
                    plain['{dot}{0}'.format(key, dot='' if root else '.')]=subVal
    elif type(d) in (list, tuple):
        for i in range(len(d)):
            for subKey, subVal in TreeDictToPlainDict(d[i], False).items():
                if not subKey == noneKey:
                    plain['{dot}{0}{1}'.format(i, subKey, dot='' if root else '.')] = subVal
                else:
                    plain['{dot}{0}'.format(i, dot='' if root else '.')] = subVal
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

def FirterDictKeys(d, keys):
    return dict(filter(lambda i: i[0] in keys, d.items()))
        