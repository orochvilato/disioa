#!/home/www-data/web2py/applications/observatoireassemblee/.pyenv/bin/python
# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')

import scrapy
import requests
import json
import re
import datetime

import sys
from string import Template

output_path = sys.argv[1]
params = json.loads(open(output_path+'/'+sys.argv[2]).read())

histcom = params['histo']
currcom = params['current']

from scrapy.crawler import CrawlerProcess

import unicodedata
def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
def normalize(s):
    s = strip_accents(s).replace('&nbsp;','.').replace('mme.','mme').replace('m..','m.').replace(u'\u2019','').replace('&apos;','').replace(u'\xa0','').encode('utf8').replace(' ','').replace("'",'').replace('-','').replace('\x0a','').replace('\xc5\x93','oe').decode('utf8').lower() if s else s
    if len(s)>3:
        s = s.replace('.mme','mme').replace('.m.','m.').replace('mmax','m.max').replace('m.tanisla','m.stanisla')
        if s[0]=='m' and s[:3]!='mme' and s[1]!='.':
            s='m.'+s[1:]
    return s
groupes = {}
commissions = {}
deputes = {}
crs = {}
amendements = []

class commissionsSpider(scrapy.Spider):
    name = "commissions"
    base_url = 'http://www.assemblee-nationale.fr'
    base_url2 = 'http://www2.assemblee-nationale.fr'
    cr_tmpl = Template("/layout/set/ajax/deputes/documents_parlementaires/(offset)/$offset/(id_omc)/$id/(type)/ComptesRendusCommission/(origine)/instance/(type_instance)/an_commission/(instance_leg)/15")
    def start_requests(self):
        request = scrapy.Request(url=self.base_url, callback=self.parse_commissions)
        yield request

    def parse_commissions(self,response):
        import re
        for com in response.xpath('//a[text()[contains(.,"Commissions permanentes")]]/following-sibling::ul/li/a'):
            libelle = com.xpath('text()').extract()[0]
            url = com.xpath('@href').extract()[0]
            id="OMC_PO"+re.search(r'/commissions/(\d+)_tab.asp',url).groups()[0]
            commissions[id]=dict(commission_libelle=libelle,commission_membres=[],commission_membres_ids=[],commission_id=id)
            request = scrapy.Request(self.base_url+url, callback=self.parse_commission)
            request.meta['id'] = id
            yield request

    def parse_commission(self,response):
        id = response.meta['id']
        commissions[id]['commission_libelle_long'] = response.xpath('//div[contains(@class,"titre-bandeau-bleu")]/h1/text()').extract()[0]
        request = scrapy.Request(self.base_url2+'/instances/tableau/'+id+'/null/ajax/1/legislature/15',callback=self.parse_membres)
        request.meta['id'] = id
        crs[id] = {}
        yield request
        cr_url = self.cr_tmpl.substitute(id=id,offset=0)
        request = scrapy.Request(self.base_url2+cr_url,callback=self.parse_compterendus)
        request.meta['id'] = id
        request.meta['offset'] = 0
        yield request

    def parse_compterendus(self,response):
        com_id = response.meta['id']
        offset = response.meta['offset']
        items = response.xpath('//ul[@class="liens-liste"]/li')
        for cr in items:
            cr_id = cr.xpath('@id').extract()[0]
            if not cr_id:
                return
            detail = cr.xpath('ul')[0].xpath('li')
            date_cr = datetime.datetime.strptime(detail[0].xpath('span/text()').extract()[0].strip().replace('1er','1').encode('utf8'),"%d %B %Y")
            if len(detail)>1:
                url_cr = detail[1].xpath('a/@href').extract()[0]
                request = scrapy.Request(url_cr,callback=self.parse_compterendu)
                crs[com_id][cr_id] =  dict(com_id=com_id,cr_id=cr_id,date=date_cr,url=url_cr)
                request.meta['com_id'] = com_id
                request.meta['cr_id'] = cr_id

                yield request

        cr_url = self.cr_tmpl.substitute(id=com_id,offset=offset+10)
        request = scrapy.Request(self.base_url2+cr_url,callback=self.parse_compterendus)
        request.meta['id'] = com_id
        request.meta['offset'] = offset + 10
        yield request


    def parse_compterendu(self,response):
        com_id = response.meta['com_id']
        cr_id = response.meta['cr_id']
        heure = response.xpath('//h1[contains(@class,"SOMseance")]/text()').extract()[0].replace(u'\xa0',' ')
        cr_heure,cr_minute = re.search(r'ance de *(\d+) *heures *(\d*)',heure).groups()
        crs[com_id][cr_id]['date'] = crs[com_id][cr_id]['date'].replace(hour=int(cr_heure),minute=int(cr_minute or 0)).strftime('%Y-%m-%d %H:%M')
        textes = response.xpath('//i[text()[contains(.,"La Commission examine") or contains(.,"texte de la Commission")]]')
        if textes:
            for texte in textes:
                num = re.search(r"texte de la Commission n.*(\d+)",texte.extract())
                if num:
                    num = num.groups()[0]
                    amds = texte.xpath('parent::p/following-sibling::center[1]/table/tr')
                    for amd in amds[1:]:
                        tab = amd.xpath('td/p')
                        def getitem(i):
                            return ''.join(i.xpath('.//text()').extract()).strip()
                        article = getitem(tab[0])
                        amendements.append(dict(commission_id=com_id,
                                                reunion_id=cr_id,
                                                amendement_id="%s_%s_%s_%s" % (com_id,cr_id,num,article),
                                                texte=num,
                                                article=article,
                                                amendement=getitem(tab[1]),
                                                auteur_id=normalize(getitem(tab[2])),
                                                auteur=getitem(tab[2]),
                                                groupe=getitem(tab[3]),
                                                sort=getitem(tab[4])))

        presents = response.xpath(u'//p[i[text()[contains(.,"Présents.")]]]/text()').extract()
        #if presents:
        #    presents = re.search(r'</i>(.*)</p>',presents[0].replace(' M&nbsp;','M.').replace('<br>','').replace('\n','').replace('\r','')).groups()
            
        if presents:
            presents = presents[0].replace('8','').replace('<i>','').replace('</i>.','').replace('</i>','').replace(u'\u2013','').replace('.mme','mme')
            crs[com_id][cr_id]['presents'] = [ normalize(p) for p in presents.split(',')]
                
        excuses = response.xpath(u'//p[i[text()[contains(.,"Excusé")]]]/text()').extract()
        #if excuses:
        #    excuses = re.search(r'</i>(.*)</p>',excuses[0].replace(' M&nbsp;','M.').replace('<br>','').replace('\n','').replace('\r','')).groups()
            
        if excuses:
            excuses = excuses[0].replace('8','').replace('<i>','').replace('</i>.','').replace('</i>','').replace(u'\u2013','').replace('.mme','mme')
            crs[com_id][cr_id]['excuses'] = [normalize(e) for e in excuses.split(',')]


    def parse_membres(self,response):
        id = response.meta['id']
        for m in response.xpath('//table[@class="instance"]/tbody/tr'):
            td = m.xpath('td')
            uid = td[0].xpath('a/@href').extract()[0].split('_')[1]
            depid = normalize(td[0].xpath('a/text()').extract()[0])
            fonction = td[1].xpath('text()').extract()[0].strip() or 'Membre'
            commissions[id]['commission_membres'].append(dict(uid=uid,id=depid,fonction=fonction))
            commissions[id]['commission_membres_ids'].append(depid)



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)','DOWNLOAD_DELAY':0.10
})


process.crawl(commissionsSpider)
process.start() # the script will block here until the crawling is finished
presences = []
for comid in crs.keys():
    for crid in crs[comid].keys():
        datecom = datetime.datetime.strptime(crs[comid][crid]['date'],'%Y-%m-%d %H:%M')
        listep = dict((depid,'present') for depid in crs[comid][crid].get('presents',[]))
        listep.update(dict((depid,'excuse') for depid in crs[comid][crid].get('excuses',[])))
        if histcom.get(comid,None):
            for depid in histcom[comid].keys():
                if not depid in listep.keys():
                    for period in histcom[comid][depid]:
                        debut = datetime.datetime.strptime(period[0],'%d/%m/%Y')
                        fin = datetime.datetime.strptime(period[1],'%d/%m/%Y')
                        if datecom>=debut and datecom<=fin:
                            listep[depid] = "absent"
        for depid in commissions[comid]['commission_membres_ids']:
            if not depid in listep.keys():
                if depid in currcom.keys() and datecom>datetime.datetime.strptime(currcom[depid],'%d/%m/%Y'):
                      listep[depid] = 'absent'
        for depid in listep.keys():
            if len(depid)>7:
                presences.append(dict(
                    presence_id="%s_%s_%s" % (comid,crid,depid),
                    commission_id = comid,
                    reunion_id = crid,
                    presence_date = crs[comid][crid]['date'],
                    presence_etat = listep[depid],
                    depute_id = depid
                ))

import json

with open(output_path+'/presences.json','w') as f:
    f.write(json.dumps(presences))
with open(output_path+'/commissions.json','w') as f:
    f.write(json.dumps(commissions.values()))
with open(output_path+'/amendements.json','w') as f:
    f.write(json.dumps(amendements))
