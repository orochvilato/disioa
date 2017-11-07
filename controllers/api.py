# -*- coding: utf-8 -*-
# essayez quelque chose comme

import json
import re
import random

deputefields = ['depute_uid','depute_id','depute_shortid','depute_region','depute_departement','depute_departement_id',
                'depute_csp',
                'depute_circo','depute_nom','depute_contacts','groupe_abrev','groupe_libelle',
                'depute_election','depute_profession','depute_naissance','depute_suppleant',
                'depute_actif','depute_mandat_debut','depute_mandat_fin','depute_mandat_fin_cause',
                'depute_bureau','depute_mandats','depute_autresmandats','depute_collaborateurs',
                'depute_hatvp','depute_nuages','depute_place','stats']

deputesfields = ['depute_uid','depute_id','depute_shortid','depute_region','depute_departement','depute_departement_id',
                 'depute_csp','depute_contacts','depute_suppleant'
                'depute_circo','depute_nom','groupe_abrev','groupe_libelle',
                'depute_profession','depute_naissance','depute_actif','depute_place','stats']
deputesfields  = deputefields

#scrutins_by_id = cache.disk('scrutins_by_id',lambda: dict((s['scrutin_id'],s) for s in mdb.scrutins.find()), time_expire=3600)
deputesFI = cache.disk('deputesFI',lambda: mdb.deputes.find({'groupe_abrev':'FI'}).distinct('depute_shortid'),time_expire=3600)

def return_json(resp):
    from bson import json_util
    response.headers['Content-Type'] = 'text/json'
    return json_util.dumps(resp)

def depute():
    shortid = request.args(0)
    mfields = dict((f,1) for f in deputefields)
    mfields.update({'_id':False})
    depute = mdb.deputes.find_one({'depute_shortid':shortid},mfields)
    if not depute:
        depute = mdb.deputes.find_one({'depute_shortid':deputesFI[int(random.random()*len(deputesFI))]},mfields)
    else:
        obsass_log('fiche',shortid)

       
    photo_an='http://www2.assemblee-nationale.fr/static/tribun/15/photos/'+depute['depute_uid'][2:]+'.jpg'
    depnumdep = depute['depute_departement_id'][1:] if depute['depute_departement_id'][0]=='0' else depute['depute_departement_id']
    depute_circo_complet = "%s / %s (%s) / %se circ" % (depute['depute_region'],depute['depute_departement'],depnumdep,depute['depute_circo'])

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
                votes_cles=s_cles,
                depute_circo_complet = depute_circo_complet,
                depute_photo_an = photo_an,
                id = depute['depute_shortid'],
                **depute)
    
    return return_json(resp)



from collections import OrderedDict
tri_choices = OrderedDict([('stats.positions.exprimes',{'label':'Participation','classe':'deputes-participation','rank':'exprimes','precision':0,'unit':'%'}),
            ('stats.positions.dissidence',{'label':'Contre son groupe','classe':'deputes-dissidence','rank':'dissidence','precision':0,'unit':'%'}),
            ('stats.compat.FI',{'label':'Compatibilité FI','classe':'deputes-fi','rank':'compatFI','precision':0,'unit':'%'}),
            ('stats.compat.REM',{'label':'Compatibilité EM','classe':'deputes-em','rank':'compatREM','precision':0,'unit':'%'}),
            ('stats.nbitvs',{'label':"Nombre d'interventions",'classe':'deputes-interventions','rank':'nbitvs','precision':0,'unit':''}),
            ('stats.nbmots',{'label':"Nombre de mots",'classe':'deputes-mots','rank':'nbmots','precision':0,'unit':''}),
            ('stats.amendements.rediges',{'label':"Amendements rédigés",'classe':'deputes-mots','rank':'nbamendements','precision':0,'unit':''}),
            ('stats.amendements.adoptes',{'label':"Amendements adoptés (%)",'classe':'deputes-mots','rank':'pctamendements','precision':0,'unit':'%'}),
            ('stats.commissions.present',{'label':"Présence en commission",'classe':'deputes-mots','rank':'pctcommissions','precision':0,'unit':'%'}),
                           
            ('stats.election.inscrits',{'label':"Voix en % des inscrits",'classe':'deputes-pctinscrits','precision':2,'rank':'pctinscrits','unit':'%'}),
            ('stats.election.exprimes',{'label':"Voix en % des votes exprimés",'classe':'deputes-pctexprimes','precision':2,'rank':'pctexprimes','unit':'%'}),
                         
            ('depute_nom_tri',{'label':"Nom",'classe':'','rank':'N/A','unit':''})
            ])
tri_items = {'tops': ('stats.positions.exprimes','stats.positions.dissidence','stats.compat.FI','stats.compat.REM','stats.nbitvs','stats.nbmots','stats.amendements.rediges','stats.amendements.adoptes','stats.commissions.present','stats.election.exprimes','stats.election.inscrits'),
             'liste': ('depute_nom_tri','stats.positions.exprimes','stats.positions.dissidence','stats.compat.FI','stats.compat.REM')}    

# ---------------------------------
# Page députés
# ---------------------------------
def deputes():
    func = request.args(0)
    if not func in ['liste','tops','flops']:
        return depute()
    if func=='liste':
        ajx = _ajax('liste')
        return return_json(ajx)
    elif func=='tops':
        return return_json(_ajax('tops'))
    elif func=='flops':
        return return_json(_ajax('flops'))

    return_json([])

def _ajax(type_page):
    # ajouter des index (aux differentes collections)
    
    nb = int(request.vars.get('itemsperpage','15'))
    age = request.vars.get('age',None)
    csp = request.vars.get('csp',None)
    page = int(request.vars.get('page','1'))-1
    groupe = request.vars.get('group',None)
    direction = int(request.vars.get('direction',1))
    text = request.vars.get('query','').decode('utf8')
    region = request.vars.get('region',None)
    top = None if type_page=='liste' else type_page
    tri = request.vars.get('sort','stats.positions.exprimes' if top else 'depute_nom_tri')
    
    
        
    tops_dir = {'stats.positions.exprimes':-1,
                  'stats.positions.dissidence':-1,
                  'stats.nbitvs':-1,
                  'stats.nbmots':-1,
                  'stats.compat.FI':-1,
                  'stats.compat.REM':-1,
                  'stats.amendements.rediges':-1,
                  'stats.amendements.adoptes':-1,
                  'stats.commissions.present':-1,
                  'stats.election.exprimes':-1,
                  'stats.election.inscrits':-1}

    filter = {'$and':[ {'depute_actif':True}]}

    if csp:
        filter['$and'].append({'depute_csp':csp})
    if age:
        filter['$and'].append({'depute_classeage':age})
    if groupe:
        filter['$and'].append({'groupe_abrev':groupe})
    if region:
        filter['$and'].append({'depute_region':region})
    if text:
        regx = re.compile(text, re.IGNORECASE)
        filter['$and'].append({'depute_nom':regx})

    sort = []
    if top:
        direction = tops_dir[tri] * (1 if top=='tops' else -1)
        rank = 'stats.ranks.'+('down' if (tops_dir[tri]==-1 and top=='tops') else 'up')+'.'+tri_choices[tri]['rank']
        #sort += [ ('stats.nonclasse',1),(tri,direction),(rank,tops_dir[tri]*(-1 if top=='top' else 1))]
        sort += [ ('stats.nonclasse',1),(rank,1)]
        filter['$and'].append({tri:{'$ne':None}})
    else:
        sort += [ (tri,direction)]

    skip = nb*page
    deputes_filters = dict((f,1) for f in deputesfields)
    deputes_filters['_id'] = False
    def countItems():
        rcount = mdb.deputes.find(filter,deputes_filters).sort(sort).count()
        skipped = 0
        
        if top:
            cfilter = {'$and':list(filter['$and'])}
            cfilter['$and'][-1] = {tri:{'$eq':None}}
            excount = mdb.deputes.find(cfilter).sort(sort).count()
            if excount>0 and 'stats.compat.' in tri:
                skipped=excount
        
        return {'totalitems':rcount, 'skipped':skipped, 'skippedpct':seuil_compat}
    cachekey= u"dep%s_%s_%s_%s_%s_%s" % (type_page,age,csp.decode('utf8') if csp else csp,groupe,text,region.decode('utf8') if region else region)
    counts = cache.ram(cachekey,lambda:countItems(),time_expire=3600)
    #return json.dumps(counts)
    items = []
   
    for d in mdb.deputes.find(filter,deputes_filters).sort(sort).skip(skip).limit(nb):
        photo_an='http://www2.assemblee-nationale.fr/static/tribun/15/photos/'+d['depute_uid'][2:]+'.jpg'
        depnumdep = d['depute_departement_id'][1:] if d['depute_departement_id'][0]=='0' else d['depute_departement_id']
        depute_circo_complet = "%s / %s (%s) / %se circ" % (d['depute_region'],d['depute_departement'],depnumdep,d['depute_circo'])
        d['depute_photo_an'] = photo_an
        d['depute_circo_complet'] = depute_circo_complet
        d['id'] = d['depute_shortid']
        items.append(d)
    
    import math
    nbpages = int(math.ceil(float(counts['totalitems'])/nb))
    result = dict(nbitems=len(items),nbpages=nbpages, currentpage=1+page,itemsperpage=nb, items=items,**counts)
    return result


def votes():
    nb = int(request.vars.get('itemsperpage','15'))
    page = int(request.vars.get('page','1'))-1
    groupe = request.vars.get('group',None)
    scrutin = request.vars.get('scrutin',None)
    csp = request.vars.get('csp',None)
    age = request.vars.get('age',None)
    search = request.vars.get('query','').decode('utf8')
    region = request.vars.get('region',None)
    depute = request.vars.get('depute',None)
    position = request.vars.get('position',None)
    text = request.vars.get('query','').decode('utf8')
    skip = nb*page
    filters = []
    if position:
        filters.append({'vote_position':position})
    if depute:
        filters.append({'depute_shortid': depute})
    if csp:
        filters.append({'depute_csp':csp})
    if age:
        filters.append({'depute_classeage':age})
    if groupe:
        filters.append({'groupe_abrev':groupe})
    if region:
        filters.append({'depute_region':region})
    if scrutin:
        try:
            scrutin=int(scrutin)
        except:
            pass
        filters.append({'scrutin_num':scrutin})
    if search:
        filters.append({'$text':{'$search':search}})
    if len(filters)==0:
        vote_filter = {}
    elif len(filters)==1:
        vote_filter = filters[0]
    else:
        vote_filter = {'$and':filters}
        
    votes = list(mdb.votes.find(vote_filter).sort('scrutin_num',-1).skip(skip).limit(nb))
    
    def countItems():
        rcount = mdb.votes.find(vote_filter).count()
        return {'totalitems':rcount}
    cachekey= u"vot%s_%s_%s_%s_%s_%s_%s_%s" % (depute,position,scrutin,age,csp.decode('utf8') if csp else csp,groupe,text,region.decode('utf8') if region else region)
    counts = cache.ram(cachekey,lambda:countItems(),time_expire=3600)
    regx = re.compile(search, re.IGNORECASE)
    if search:
        for v in votes:
            repl = regx.subn('<high>'+search+'</high>',v['scrutin_desc'])
            if repl[1]:
                v['scrutin_desc'] = repl[0]

    import math
    nbpages = int(math.ceil(float(counts['totalitems'])/nb))
    result = dict(nbitems=len(votes),nbpages=nbpages, currentpage=1+page,itemsperpage=nb, items=votes,**counts)
    return return_json(result)
