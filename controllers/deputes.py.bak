# -*- coding: utf-8 -*-
# essayez quelque chose comme
import re
import json

mdb = client.obsass

# cache
CACHE_EXPIRE = 3600
cache_groupes = cache.disk('groupes', lambda: [(g['groupe_abrev'],g['groupe_libelle']) for g in mdb.groupes.find()], time_expire=CACHE_EXPIRE)
cache_regions = cache.disk('regions',lambda: sorted([(r,r) for r in mdb.deputes.distinct('depute_region')],key=lambda x:x), time_expire=CACHE_EXPIRE)
cache_ages = cache.disk('ages',lambda: sorted([(a,a) for a in mdb.deputes.distinct('depute_classeage')],key=lambda x:x), time_expire=CACHE_EXPIRE)
cache_csp = cache.disk('csp',lambda: sorted([(c,c) for c in mdb.deputes.distinct('depute_csp')],key=lambda x:x), time_expire=CACHE_EXPIRE)
# ---------------------------------
# Page députés
# ---------------------------------

def index():
    groupe = request.vars.get('gp','ALL')
    tri = request.vars.get('tr','depute_nom_tri')
    direction = int(request.vars.get('di',1))
    text = request.vars.get('txt',"")
    region = request.vars.get('rg',"")
    top = request.vars.get('top',"")

    groupes = cache_groupes
    regions = cache_regions
    tris_liste = [('depute_nom_tri','Tri par nom'),
            ('stats.positions.exprimes','Tri par participation'),
            ('stats.positions.dissidence','Tri par Opposition à son groupe'),
            ('stats.compat.FI','Tri par FI-Compatibilité'),
            ('stats.compat.REM','Tri par EM-Compatibilité'),
            ('stats.nbitvs',"Tri par nombre d'interventions"),
            ('stats.nbmots',"Tri par nombre de mots"),
            ('depute_circo_id',"Tri par circonscription")]
    tops = [('top10part','Top 10 Participation'),
            ('top10diss','Top 10 Opposition à son groupe'),
            ('top10compFI','Top 10 FI-Compatible'),
            ('top10compREM','Top 10 EM-Compatible'),
            ('top10itvs','Top 10 Interventions'),
            ('top10mots','Top 10 Mots'),
            ('flop10part','Flop 10 Participation'),
            ('flop10diss','Flop 10 Opposition à son groupe'),
            ('flop10compFI','Flop 10 FI-Compatible'),
            ('flop10compREM','Flop 10 EM-Compatible'),
            ('flop10itvs','Flop 10 Interventions'),
            ('flop10mots','Flop 10 Mots'),
            ]
    return locals()

def ajax():
    # ajouter des index (aux differentes collections)
    nb = 25
    minpart_top = 30
    page = int(request.args(0) or 2)-2
    groupe = request.vars.get('gp','ALL')
    tri = request.vars.get('tr','depute_nom_tri')
    direction = int(request.vars.get('di',1))
    text = request.vars.get('txt','').decode('utf8')
    region = request.vars.get('rg',None)
    top = request.vars.get('top',None)

    tops_sorts = {'part':'stats.positions.exprimes',
                  'diss':'stats.positions.dissidence',
                  'itvs':'stats.nbitvs',
                  'mots':'stats.nbmots',
                  'compFI':'stats.compat.FI',
                  'compREM':'stats.compat.REM'}

    filter = {'depute_actif':True}


    if text:
        regx = re.compile(text, re.IGNORECASE)
        filter['depute_nom'] = regx
    if groupe and groupe!='ALL':
        filter['groupe_abrev'] = groupe
    if region and region!='ALL':
        filter['depute_region'] = region

    if top:
        rtop = re.match(r'(top|flop)(\d+)([a-z]{4})([A-Z]*)',top)
        if rtop:
            tf,n,typ,gp = rtop.groups()
            nb = int(n)
            page = 0
            direction = -1 if tf=='top' else 1
            tri = tops_sorts[typ+gp]
            filter = {'$and':[ {'stats.positions':{'$ne':None}},filter ]}
            if gp:
                filter['$and'].append({'groupe_abrev':{'$ne':gp}})
    skip = nb*page
    deputes = list(mdb.deputes.find(filter).sort([(tri,direction)]).skip(skip).limit(nb))

    return dict(deputes=deputes, tri = tri, skip = skip, next=((nb == len(deputes)) and not top ))


# Tests
from collections import OrderedDict
tri_choices = OrderedDict([('stats.positions.exprimes',{'label':'Participation','classe':'deputes-participation','rank':'exprimes','unit':'%'}),
            ('stats.positions.dissidence',{'label':'Contre son groupe','classe':'deputes-dissidence','rank':'dissidence','unit':'%'}),
            ('stats.compat.FI',{'label':'FI-Compatibilité','classe':'deputes-fi','rank':'compatFI','unit':'%'}),
            ('stats.compat.REM',{'label':'EM-Compatibilité','classe':'deputes-em','rank':'compatREM','unit':'%'}),
            ('stats.nbitvs',{'label':"Nombre d'interventions",'classe':'deputes-interventions','rank':'nbitvs','unit':''}),
            ('stats.nbmots',{'label':"Nombre de mots",'classe':'deputes-mots','rank':'nbmots','unit':''}),
            ('depute_nom_tri',{'label':"Nom",'classe':'','rank':'N/A','unit':''})
            ])
tri_items = {'tops': ('stats.positions.exprimes','stats.positions.dissidence','stats.compat.FI','stats.compat.REM','stats.nbitvs','stats.nbmots'),
             'liste': ('depute_nom_tri','stats.positions.exprimes','stats.positions.dissidence','stats.compat.FI','stats.compat.REM')}    
top_choices = [('top','Top'),
            ('flop','Flop'),
            ]

def liste():
    params = dict(request.vars)
    return dict(params=params,tris=tri_choices,groupes = cache_groupes,regions = cache_regions, csp=cache_csp, ages=cache_ages)


def ajax_liste():
    return _ajax('liste')

def tops():
    params = dict(request.vars)
    params['top'] = params.get('top','top')

    return dict(params=params,tops=top_choices,tris=tri_choices,groupes = cache_groupes,regions = cache_regions)
def ajax_top():
    return _ajax('tops')


def _ajax(type_page):
    # ajouter des index (aux differentes collections)
    nb = 25
    count = request.vars.get('count',None)
    age = request.vars.get('age',None)
    csp = request.vars.get('csp',None)
    page = int(request.args(0) or 2)-2
    groupe = request.vars.get('gp',None)
    direction = int(request.vars.get('di',1))
    text = request.vars.get('txt','').decode('utf8')
    region = request.vars.get('rg',None)
    top = request.vars.get('top',None)
    tri = request.vars.get('tri','stats.positions.exprimes' if top else 'depute_nom_tri')
    
    tops_dir = {'stats.positions.exprimes':-1,
                  'stats.positions.dissidence':-1,
                  'stats.nbitvs':-1,
                  'stats.nbmots':-1,
                  'stats.compat.FI':-1,
                  'stats.compat.REM':-1 }

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
        direction = tops_dir[tri] * (1 if top=='top' else -1)
        sort += [ (tri,direction),('stats.ranks.'+tri_choices[tri]['rank'],1 if top=='top' else -1)]
    else:
        sort += [ (tri,direction)]

    skip = nb*page
    mreq = mdb.deputes.find(filter).sort(sort)
    if count:
        return json.dumps(dict(count=mreq.count()))
    
    deputes = list(mreq.skip(skip).limit(nb))

    return dict(deputes=deputes, count=count,tri = tri, top=tri_choices[tri], tf=top, skip = skip, next=(nb == len(deputes) ))
