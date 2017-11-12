# -*- coding: utf-8 -*-
import datetime
def svgvisuel(visuel,**args):
    return XML(response.render('svg/visuels/%s.svg' % visuel, **args))

def get_visuel(visuel,**args):
    return XML(response.render('visuels/%s.svg' % visuel, **args))

def obsass_log(domaine,page):
    return
    if request.env.REQUEST_SCHEME=='http':
        mdb.logs.insert_one({'date':datetime.datetime.now(),
                             'client':request.client,
                             'agent':request.env.HTTP_USER_AGENT,
                             'referer':request.env.HTTP_REFERER,
                             'page':page,
                             'domaine':domaine})

def getdot(e,k):
    for _k in k.split('.'):
        if _k in e.keys():
            e = e[_k]
        else:
            e = ""
            break
    return e

def svggauge(typeg,pct,unit='%'):
    if typeg=='compfi':
        circlecolor = "#82cde2"
        symbolcolor = "#213558"
        symbol = 'compfi'
        transp = '0.24'
    elif typeg=='compem':
        circlecolor = "#82cde2"
        symbolcolor = "#213558"
        symbol ='compem'
        transp ='0.33'
    elif typeg=='diss':
        circlecolor = "#82cde2"
        symbolcolor = "#213558"
        symbol ='diss'
        transp ='0.23'
    elif typeg=="vote":
        circlecolor = "#82cde2"
        symbolcolor = "#213558"
        symbol ='vote'
        transp ='0.33'
    else:
        circlecolor = "#82cde2"
        symbolcolor = "#213558"
        symbol = typeg
        transp ='0.33'
    return XML(response.render('svg/gauge.svg',color=circlecolor,symbol=XML(response.render('svg/gauge/%s.svg' % symbol, color=symbolcolor)),pct=pct if pct!=None else None,transp=transp,unit=unit))

def svgtop(typet):
    if typet=='top10':
        color = '#27bee0'
        colorlight = '#70cae8'
        label = 'TOP 10'
    elif typet=='top20':
        color = '#f9910b'
        colorlight = '#fcbd58'
        label = 'TOP 20'
    elif typet=='top50':
        color = '#f25a3c'
        colorlight = '#f57a3c'
        label = 'TOP 50'
    return XML(response.render('svg/part-top.svg', color=color, colorlight=colorlight, label=label))


def svgcirco(circo):
    if not circo:
        circo = '013-01'
    dep = circo.split('-')[0]
    circosel = mdb.circonscriptions.find_one({'id':circo})
    if not circosel:
        return XML(response.render('svg/circoworld.svg',dep=dep,circo=circo))
    if circosel['paris']:
        filtre = {'paris':True}
    else:
        filtre = {'dep':dep}
    circos = list(mdb.circonscriptions.find(filtre))
    return XML(response.render('svg/circofrance.svg',dep=dep,circo=circosel,circos=circos))

def hemicycle(place="nope",groupe="",base_url=""):
    return XML(response.render('svg/hemicyclelight.svg',place='p'+(place or 'nope'),groupe=groupe,base_url='/'+base_url))
