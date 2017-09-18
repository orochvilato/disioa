# -*- coding: utf-8 -*-
import random
deputesFI = cache.ram('deputesFI',lambda: mdb.deputes.find({'groupe_abrev':'FI'}).distinct('depute_shortid'),time_expire=3600)
def index():
    shortid = request.args(0)
    depute = mdb.deputes.find_one({'depute_shortid':shortid}) or mdb.deputes.find_one({'depute_shortid':deputesFI[int(random.random()*len(deputesFI))]})
    itvs = sorted(list(mdb.interventions.find({'depute_uid':depute['depute_uid']})),key=lambda x:(x['itv_date'],-x['itv_n']),reverse=True)
    votes = list(mdb.votes.find({'depute_uid':depute['depute_uid']}).sort('scrutin_num',-1))
    scrutins = dict((s['scrutin_id'],s) for s in mdb.scrutins.find({'scrutin_id':{'$in':[v['scrutin_id'] for v in votes]}}))
    for v in votes:
        v.update(scrutins[v['scrutin_id']])
    return dict(itvs=itvs,votes=votes,**depute)
