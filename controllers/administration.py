# -*- coding: utf-8 -*-
# essayez quelque chose comme

def updateLogs():
    from geoip import geolite2
    import pycountry
    for l in mdb.logs.find({'geoip':None}):
        match = geolite2.lookup(l['client'])
        pays = ""
        if match:
            country = match.country
            if country:
                pays = pycountry.countries.get(alpha_2=country).name
        mdb.logs.update({'_id':l['_id']},{'$set':{'geoip':pays}})

def logs():
    updateLogs()
    return dict(logs=mdb.logs.find().sort('date',-1).limit(1000))
