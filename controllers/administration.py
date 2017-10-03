# -*- coding: utf-8 -*-
# essayez quelque chose comme
import json
def getPrivate():
    name = request.args(0)
    import os
    f = open(os.path.join(request.folder,'private','data',name))
    response.headers['ContentType'] ="application/octet-stream";
    response.headers['Content-Disposition']="attachment; filename="+name
    
    return response.stream(f,chunk_size=4096)

    
def updateElectionTour():
    mdb.deputes.update_one({'depute_shortid':'anneblanc'},{'$set':{'depute_election.adversaires':[{'nom':"M. André AT (retiré)",'voix':0}]}})
    mdb.deputes.update_many({'depute_election.adversaires.0': { "$exists": False } }, {'$set':{'depute_election.tour':1}})
    mdb.deputes.update_many({'depute_election.adversaires.0': { "$exists": True } }, {'$set':{'depute_election.tour':2}})
def test():
    #return BEAUTIFY(mdb.deputes.find_one({'depute_uid':'PA719684'}))
    gp_abrevs = mdb.groupes.distinct('groupe_abrev')
    pgroup = dict((g+'_pour',{'$sum':'$depute_compat.'+g+'.pour'}) for g in ['FI','REM'])
    pgroup.update(dict((g+'_total',{'$sum':'$depute_compat.'+g+'.total'}) for g in ['FI','REM']))
    pgroup['_id'] = {'groupe':'$groupe_abrev'}
    pipeline = [
        {"$group": pgroup },
    ]
    compats = {}
    
    for cpt in mdb.deputes.aggregate(pipeline):
        gp = cpt['_id']['groupe']
        _comp = {}
        for g in ['FI','REM']:
            _comp[g] = {'pour':cpt[g+'_pour'],'total':cpt[g+'_total']}
        compats[gp] = _comp
    return BEAUTIFY(compats)
    return BEAUTIFY(mdb.scrutins.find_one({'scrutin_id':'15_87'}))
    
def error():
    1/0
def updateLogs():
    from geoip import geolite2
    import pycountry
    from user_agents import parse
    for l in mdb.logs.find({'$or':[{'geoip':None},{'agent_pretty':None}]}):
        match = geolite2.lookup(l['client'])
        pays = ""
        if match:
            country = match.country
            if country:
                pays = pycountry.countries.get(alpha_2=country).name
        agent_pretty = str(parse(l['agent']))
        mdb.logs.update({'_id':l['_id']},{'$set':{'geoip':pays,'agent_pretty':agent_pretty}})

def logs():
    updateLogs()
    return dict(logs=mdb.logs.find().sort('date',-1).limit(200))
