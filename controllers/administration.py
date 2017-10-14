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
    return BEAUTIFY(mdb.groupes.find_one()['stats'])
    #return BEAUTIFY(list(mdb.presences.find({'depute_id':'m.jeanlucmelenchon'})))
    # presences / depute
    pgroup = {}
    pgroup['n'] = {'$sum':1}
    pgroup['_id'] = { 'depute_id':'$depute_id', 'etat':'$presence_etat'}
    pipeline = [{'$group':pgroup}]
    presences_deputes = {}
    for p in mdb.presences.aggregate(pipeline):
        depid = p['_id']['depute_id']
        etat = p['_id']['etat']
        if not depid in presences_deputes.keys():
            presences_deputes[depid]={'present':0,'absent':0,'excuse':0}
        presences_deputes[depid][etat] += p['n']
    
    # presences / par groupe
    pgroup = {}
    pgroup['n'] = {'$sum':1}
    pgroup['_id'] = { 'groupe':'$groupe_abrev', 'etat':'$presence_etat'}
    pipeline = [{'$group':pgroup}]
    presences_groupes = {}
    for p in mdb.presences.aggregate(pipeline):
        groupeabrev = p['_id']['groupe']
        etat = p['_id']['etat']
        if not groupeabrev in presences_groupes.keys():
            presences_groupes[groupeabrev]={'present':0,'absent':0,'excuse':0}
        presences_groupes[groupeabrev][etat] += p['n']
    
    
    return json.dumps(presences_groupes)
    
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
