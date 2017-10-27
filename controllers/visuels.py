# -*- coding: utf-8 -*-
# essayez quelque chose comme
from base64 import b64encode
import requests
import json
import os
import re
import datetime
nuances = dict([('DIV', 'Divers'), ('ECO', 'Ecologiste'), ('EXG', 'Extrème gauche'), ('FN', 'Front National'), ('DVD', 'Divers droite'), ('FI', 'La France insoumise'), ('LR', u'Les Républicains'), ('COM', u'Parti communiste fran\xc3\xa7ais'), ('REM', u'La République en marche'), ('SOC', 'Parti socialiste'), ('DLF', 'Debout la France'), ('DVG', 'Divers gauche'), ('EXD', 'Extrème droite'), ('REG', u'Régionalistes'), ('UDI', u'Union des Démocrates et Indépendants'), ('MDM', 'Modem'), ('RDG', 'Parti radical de gauche')])

visuels_defs = {'participationscrutins20': {
                         'nom':'Participation au scrutins publics < 20%',
                         'collection':'deputes',
                         'key':'depute_shortid',
                         'match':{'$and':[{'depute_actif':True},{'stats.positions.exprimes':{'$lt':20}}]},
                         'fields':[('nom','depute_nomcomplet'),('groupe','groupe_libelle'),('participation','stats.positions.exprimes')],
                         'visuel':'test2',
                         'visuel_data':{'groupe':'depute_groupe',
                                        'nom':'depute_nom',
                                        'prenom':'depute_prenom',
                                        'photo':'depute_photo',
                                        'pct':'depute_pctexprime',
                                        'symbol':('symbol_vote',{'color':'#82cde2','tx':354,'ty':150,'scale':0.4})
                                        },
                         }
                }
               
def generer():
    visuel_def = visuels_defs['participationscrutins20']
    choix = list(mdb[visuel_def['collection']].find(visuel_def['match']))
    return dict(visuel=visuel_def,choix=choix)

def test():
    return BEAUTIFY(mdb.deputes.find_one())
    return BEAUTIFY(list(mdb.deputes.find({'$and':[{'depute_actif':True},{'stats.positions.exprimes':{'$lt':20}}]},{'stats.nbmots':1})))

def get_vdata(source,key,**args):
    if key=='depute_groupe':
        groupe_abrev = source['groupe_abrev']
        if groupe_abrev == 'NI':
            groupe_abrev = source['depute_election']['nuance']
            groupe_lib = nuances[groupe_abrev]
        else:
            groupe_lib = source['groupe_libelle'].split(':')[0].strip()
        depart = source['depute_departement_id'] if source['depute_departement_id'][0]!='0' else source['depute_departement_id'][1:]
        groupe = u"Député %s (%s) - %s" % (groupe_lib,groupe_abrev,depart)
        return groupe
    elif key=='depute_photo':
        path = os.path.join(request.folder, 'static/images/deputes/%s.jpg' % source['depute_id'])
        content = open(path).read()
        #content =requests.get('http://www2.assemblee-nationale.fr/static/tribun/15/photos/'+depute['depute_uid'][2:]+'.jpg').content
        photo = b64encode(content)
        return photo
    elif key=='depute_nom':
        return source['depute_hatvp'][0]['nom']
    elif key=='depute_prenom':
        return source['depute_hatvp'][0]['prenom']
    elif key=='depute_pctexprime':
        return ("%d%%" % round(source['stats']['positions']['exprimes'],0)).replace('.',',')
    elif key[:7]=='symbol_':
        symbol = key.split('_')[1]
        return XML(response.render('svg/symbols/%s.svg' % symbol, **args))

def getvisuel(name,key):
    visuel_def = visuels_defs[name]
    source = mdb[visuel_def['collection']].find_one({visuel_def['key']:key})
    params = {}
    for k,v in visuel_def['visuel_data'].iteritems():
        if isinstance(v,tuple):
            params[k] = get_vdata(source,v[0],**v[1])
        else:
            params[k] = get_vdata(source,v)
    svg = svgvisuel(visuel_def['visuel'],date=datetime.datetime.now().strftime('%d/%m/%Y'),**params)
    data = str(svg)
    w,h = re.search(r'viewBox="0 0 ([0-9\.]+) ([0-9\.]+)"',data).groups()
    w = float(w)
    h = float(h)
    coef = float(h/w)
    return dict(data=svg,coef=coef)

def index():
    from base64 import b64encode
    import requests
    import os
    depute = request.args(0)
    tweet = (request.args(1)=='tweet')
    hasard = False
    if not depute:
        hasard = True
        deputes = list(mdb.deputes.find({'$and':[{'depute_actif':True},{'stats.positions.exprimes':{'$lt':20}}]}))
        import random
        depute = deputes[random.randint(0,len(deputes)-1)]['depute_shortid']
    return dict(tweet=tweet,visuel=getvisuel('participationscrutins20',depute),id=depute,hasard=hasard)


def getimage(deputeid,w,h):
    
    from selenium import webdriver
    
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true']) # or add to your PATH
    driver.set_window_size(w,h)# optional
    driver.get(URL('index',args=[deputeid,'tweet'],scheme=True, host=True))
    data = driver.get_screenshot_as_png()
    return data

def tweeter():
    from TwitterAPI import TwitterAPI
    api = TwitterAPI('Ym8iy6cdZcr00D3cQ4I3nH6M5', 'OOMiTg1ezrX6aY8w5N6UMKMZe9BgmJLT6udnjfTEZ6NBOvlblm','3434108799-IzoPtfb1jPnMkStVZyDaDJ2Fa8iiBijfJMnNF99', 'MiMOaX9D8CYH7nIWPbJjlYgGHSUGTmKpwVH9FdV0GC6Rj')
    id = request.args(0)
    w = request.args(1)
    h = request.args(2)
    depute = mdb.deputes.find_one({'depute_shortid':id})
    data = getimage(id,w,h)
    r = api.request('statuses/update_with_media', {'status':'post'}, {'media': data})
    if r.status_code == 200:
        picurl = r.json()['extended_entities']['media'][0]['display_url']
        import urllib
        twitter = [ c['lien'] for c in depute['depute_contacts'] if c['type']=='twitter' ]
        twitter = twitter[0].split('/')[-2] if twitter else ''

        params = urllib.urlencode({'text':'---Votre message---   '+twitter+'   '+picurl})
        redirect('https://twitter.com/intent/tweet?'+params)
   
    #r = api.request('statuses/update_with_media', {'status':message},{'media[]':data})
    #redirect('https://twitter.com/orochvilato?lang=fr')
    return BEAUTIFY(r.json())
    


def download():
    from base64 import b64encode
    import os
    depid = request.args(0)
    width = request.args(1)
    height = request.args(2)
    if width:
        data = getimage(depid,int(width),int(height))
        compl = "%sx%s" % (width,height)
        ext = 'png'
    else:
        visuel = getvisuel('participationscrutins20',depid)
        data = str(visuel['data'])
        compl = ""
        ext = "svg"
        
    from cStringIO import StringIO
    response.headers['ContentType'] ="application/octet-stream";
    response.headers['Content-Disposition']="attachment; filename="+depid+compl+"."+ext

    return response.stream(StringIO(data),chunk_size=4096)
