# -*- coding: utf-8 -*-
import random
import json
import datetime
import re

scrutins_by_id = cache.disk('scrutins_by_id',lambda: dict((s['scrutin_id'],s) for s in mdb.scrutins.find()), time_expire=3600)
deputesFI = cache.disk('deputesFI',lambda: mdb.deputes.find({'groupe_abrev':'FI'}).distinct('depute_shortid'),time_expire=3600)
def index():
    redirect(URL('fiche'))

    
def fiche():
    shortid = request.args(0)
    tab = request.args(1) if request.args(1) in ['votes','presentation','interventions'] else 'presentation'
    depute = mdb.deputes.find_one({'depute_shortid':shortid})
    if not depute:
        depute = mdb.deputes.find_one({'depute_shortid':deputesFI[int(random.random()*len(deputesFI))]})
    else:
        obsass_log('fiche',shortid)
    if request.args(1)=='data':
        return BEAUTIFY(depute.keys())
    
    votes = list(mdb.votes.find({'depute_uid':depute['depute_uid']}).sort('scrutin_num',-1))
    votes_cles = list(mdb.votes.find({'depute_uid':depute['depute_uid'],'scrutin_num':{'$in':scrutins_cles.keys()}},{'scrutin_num':1,'vote_position':1,'scrutin_dossierLibelle':1}).sort('scrutin_num',-1))
    from collections import OrderedDict
    s_cles = OrderedDict()
    for v in votes_cles:
        v.update(scrutins_cles[v['scrutin_num']])
        if not v['theme'] in s_cles:
            s_cles[v['theme']] = []
        s_cles[v['theme']].append(v)
    dates = {}
    weeks = {}
    for v in votes:
        pdat =  datetime.datetime.strptime(v['scrutin_date'],'%d/%m/%Y')
        wdat = pdat.strftime('%Y-S%W')
        sdat = pdat.strftime('%Y-%m-%d')
        if not wdat in weeks.keys():
            weeks[wdat] = {'e':0,'n':0}

        if not sdat in dates.keys():
            dates[sdat] = {'e':0,'n':0}
        weeks[wdat]['n']+= 1
        dates[sdat]['n']+= 1
        weeks[wdat]['e']+= 1 if v['vote_position']!='absent' else 0
        dates[sdat]['e']+= 1 if v['vote_position']!='absent' else 0
        
    resp = dict(dates=sorted([{"date": dat,"pct":round(float(v['e'])/v['n'],3)} for dat,v in dates.iteritems()],key=lambda x:x['date']),
                weeks=sorted([{"week": w,"pct":100*round(float(v['e'])/v['n'],2)} for w,v in weeks.iteritems()],key=lambda x:x['week']),
                tab=tab,votes_cles=s_cles,
                **depute)
    
    #response.headers["Access-Control-Allow-Origin"] = '*'
    #response.headers['Access-Control-Max-Age'] = 86400
    #response.headers['Access-Control-Allow-Headers'] = '*'
    #response.headers['Access-Control-Allow-Methods'] = '*'
    #response.headers['Access-Control-Allow-Credentials'] = 'true'
    return resp 

def ajax_votes():
    nb = 25
    page = int(request.args(0) or 2)-2
    depute_uid = request.vars.get('depute_uid',None);
    search = request.vars.get('search','').decode('utf8')
    skip = nb*page
    vote_filter = {'depute_uid':depute_uid}
    if not depute_uid:
        return ''
    if search:
        s_ids = []
        regx = re.compile(search, re.IGNORECASE)
        for s_id,s in scrutins_by_id.iteritems():
            repl = regx.subn('<high>'+search+'</high>',s['scrutin_desc'])
            if repl[1]:
                s['scrutin_desc'] = repl[0]
                s_ids.append(s_id)
        vote_filter['scrutin_id'] = {'$in':s_ids}
    votes = list(mdb.votes.find(vote_filter).sort('scrutin_num',-1).skip(skip).limit(nb))
    for v in votes:
        v.update(scrutins_by_id[v['scrutin_id']])
    return dict(votes=votes, next=(nb == len(votes)))

def ajax_itvs():
    nb = 25
    page = int(request.args(0) or 2)-2
    depute_uid = request.vars.get('depute_uid',None);
    search = request.vars.get('search','').decode('utf8')
    skip = nb*page
    itv_filter = {'depute_uid':depute_uid}
    if not depute_uid:
        return ''
    if search:
        regx = re.compile(search, re.IGNORECASE)
        itv_filter['itv_contenu_texte']=regx
    itvs = list(mdb.interventions.find(itv_filter).sort([('itv_date',-1),('session_id',1),('itv_n',1)]).skip(skip).limit(nb))
    if search:
        for itv in itvs:
            itv['itv_contenu']=regx.sub('<high>'+search+'</high>',itv['itv_contenu'])
    
    return dict(itvs=itvs, next=(nb == len(itvs)))
