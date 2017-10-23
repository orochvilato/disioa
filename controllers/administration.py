# -*- coding: utf-8 -*-
# essayez quelque chose comme
import json
def tpr():
    return BEAUTIFY(mdb.interventions.find_one({'itv_ctx_n':1}))
def getPrivate():
    name = request.args(0)
    import os
    f = open(os.path.join(request.folder,'private','data',name))
    response.headers['ContentType'] ="application/octet-stream";
    response.headers['Content-Disposition']="attachment; filename="+name
    
    return response.stream(f,chunk_size=4096)

def test2():
    return BEAUTIFY(mdb.deputes.find_one({'depute_id':'m.manuelvalls'}))
    pres = {}
    for d in mdb.deputes.find():
        if not d['groupe_abrev'] in pres.keys():
            pres[d['groupe_abrev']] = dict(present=0,absent=0,excuse=0,total=0)
        if 'depute_presences_commissions' in d.keys():
            for c in d['depute_presences_commissions'].values():
                for p in ('present','absent','excuse'):
                    pres[d['groupe_abrev']][p] += c[p]
                    pres[d['groupe_abrev']]['total'] += c[p]
    tx = {}
    for k in pres.keys():
        tx[k] = round(float(100*pres[k]['present'])/pres[k]['total'],2)
    return BEAUTIFY(tx)
    return "<p>"+"</p><p>".join([";".join(l) for l in liste])+"</p>"
    
def updateElectionTour():
    mdb.deputes.update_one({'depute_shortid':'anneblanc'},{'$set':{'depute_election.adversaires':[{'nom':"M. André AT (retiré)",'voix':0}]}})
    mdb.deputes.update_many({'depute_election.adversaires.0': { "$exists": False } }, {'$set':{'depute_election.tour':1}})
    mdb.deputes.update_many({'depute_election.adversaires.0': { "$exists": True } }, {'$set':{'depute_election.tour':2}})
def test():
    presidents = {}
    membres = {}
    for g in mdb.groupes.find():
        for m in g['groupe_membres']:
            if m['qualite']==u'Président':
                presidents[g['groupe_abrev']] = m['uid']
                break
    #return BEAUTIFY(presidents)
    depute_groupe = dict((d['depute_id'],d) for d in mdb.deputes.find())
    deputes_id = dict((d['depute_uid'],d['depute_id']) for d in mdb.deputes.find({},{'depute_id':1,'depute_uid':1}))
    pgroup = {}
    pgroup['n'] = {'$sum':'$itv_nbmots'}
    pgroup['_id'] = { 'depute_id':'$depute_id'}
    
    pipeline = [{'$match':{'itv_president':False}},{'$group':pgroup}]
    #return json.dumps(list(mdb.interventions.aggregate(pipeline)))
    mots = {}
    for depid,d in depute_groupe.iteritems():
        gp = depute_groupe.get(depid,{'groupe_abrev':None})['groupe_abrev']
        if not gp:
            continue
        sexe = 'F' if depid[0:3]=='mme' else 'H'
        if not gp in membres.keys():
            membres[gp] = {'H':0,'F':0}
        membres[gp][sexe] += 1

    for itv in mdb.interventions.aggregate(pipeline):
        depid = itv['_id']['depute_id']
        gp = depute_groupe.get(depid,{'groupe_abrev':None})['groupe_abrev']
        if not gp or depid==deputes_id.get(presidents.get(gp,None),None):
            continue
        sexe = 'F' if depid[0:3]=='mme' else 'H'
        if not gp in mots.keys():
            mots[gp]={'H':{'mots':0,'vote_expr':0,'vote_tot':0},'F':{'mots':0,'vote_expr':0,'vote_tot':0}}
            
        mots[gp][sexe]['mots'] += itv['n']
        mots[gp][sexe]['vote_expr'] += depute_groupe[depid]['depute_positions']['exprimes']
        mots[gp][sexe]['vote_tot'] += depute_groupe[depid]['depute_positions']['total']
    
    tableau = TABLE(THEAD(TR(*[TH(f) for f in ('Groupe','membres_f','membres_h','mots_f','v_exp_f','v_tot_f','mots_h','v_exp_h','v_tot_h')])),
                    TBODY(*[TR(TD(k),TD(membres[k]['F']),TD(membres[k]['H']),TD(v['F']['mots']),TD(v['F']['vote_expr']),TD(v['F']['vote_tot']),TD(v['H']['mots']),TD(v['H']['vote_expr']),TD(v['H']['vote_tot'])) for k,v in mots.iteritems()]))
    return tableau
    for p in mdb.presences.aggregate(pipeline):
        
        commissionid = p['_id']['commission_id'].split('_')[1]
        etat = p['_id']['etat']
        if not depid in presences_deputes.keys():
            presences_deputes[depid]={}
        if not commissionid in presences_deputes[depid].keys():
            presences_deputes[depid][commissionid] = {'present':0,'absent':0,'excuse':0}
        presences_deputes[depid][commissionid][etat] += p['n']
    
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
    
    
    return json.dumps(presences_deputes)
    
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
