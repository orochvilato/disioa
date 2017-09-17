# -*- coding: utf-8 -*-
import random
deputesFI = cache.ram('deputesFI',lambda: mdb.deputes.find({'groupe_abrev':'FI'}).distinct('depute_shortid'),time_expire=3600)
def index():
    shortid = request.args(0)
    depute = mdb.deputes.find_one({'depute_shortid':shortid}) or mdb.deputes.find_one({'depute_shortid':deputesFI[int(random.random()*len(deputesFI))]})
    return dict(**depute)
