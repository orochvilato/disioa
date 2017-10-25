# -*- coding: utf-8 -*-
# essayez quelque chose comme
import random
import json
import datetime
import re


def index():
    redirect(URL('fiche'))
def fiche():
    abrev = request.args(0)
    tab = request.args(1) if request.args(1) in ['votes','presentation','interventions'] else 'presentation'
    groupe = mdb.groupes.find_one({'groupe_abrev':abrev})
    if not groupe:
        groupe = mdb.groupes.find_one({'groupe_abrev':'FI'})
    else:
        obsass_log('groupe',abrev)

    #votes = list(mdb.votes.find({'depute_uid':depute['depute_uid']}).sort('scrutin_num',-1))
    votes = []   
    president = [ m['uid'] for m in groupe['groupe_membres'] if m['actif']==True and m['qualite']==u'Président']
    president = mdb.deputes.find_one({'depute_uid':president[0]},{'depute_nom':1,'depute_shortid':1}) if president else None
    del groupe['_id']
    del president['_id']
    return dict(tab=tab, president = president,
                **groupe)

def ajax_votes():
    nb = 25
    page = int(request.args(0) or 2)-2
    groupe_abrev = request.vars.get('groupe_abrev',None);
    search = request.vars.get('search','').decode('utf8')
    skip = nb*page
    scrutin_filter = {}
    if not groupe_abrev:
        return ''
    if search:
        regx = re.compile(search, re.IGNORECASE)
        scrutin_filter['scrutin_desc']=regx
    scrutins = list(mdb.scrutins.find(scrutin_filter).sort('scrutin_num',-1).skip(skip).limit(nb))

    if search:
        for s in scrutins:
            s['scrutin_desc']=regx.sub('<high>'+search+'</high>',itv['scrutin_desc'])

    return dict(scrutins=scrutins, groupe=groupe_abrev, next=(nb == len(scrutins)))

def ajax_itvs():
    nb = 25
    page = int(request.args(0) or 2)-2
    groupe_abrev = request.vars.get('groupe_abrev',None);
    search = request.vars.get('search','').decode('utf8')
    skip = nb*page
    itv_filter = {'groupe_abrev':groupe_abrev}
    if not groupe_abrev:
        return ''
    if search:
        regx = re.compile(search, re.IGNORECASE)
        itv_filter['itv_contenu_texte']=regx
    itvs = list(mdb.interventions.find(itv_filter).sort([('itv_date',-1),('session_id',1),('itv_n',1)]).skip(skip).limit(nb))
    if search:
        for itv in itvs:
            itv['itv_contenu']=regx.sub('<high>'+search+'</high>',itv['itv_contenu'])
    
    return dict(itvs=itvs, next=(nb == len(itvs)))
