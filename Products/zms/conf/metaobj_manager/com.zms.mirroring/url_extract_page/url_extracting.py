## params: self, content_url, content_node, force

from bs4 import BeautifulSoup
import hashlib
import datetime
import re
import requests

def cache_data_by_sql(self, extract={}):
    # SQLITE: SAVE/CACHE ATTRIBUTE VALUES
    lang = self.REQUEST.get('lang','ger')
    self.url_extract.sql_upsert(
        zms_id = self.getId(),
        client_id = self.getHome().getId(),
        change_dt = extract['content_datetime'],
        lang = lang,
        content_md5 = extract['content_md5'],
        content_datetime = extract['content_datetime'],
        content_cache = extract['content_cache']
    )
    return True


def gt(dt_str):
    ### How to convert Python's .isoformat() string back into datetime object
    ### https://stackoverflow.com/questions/28331512
    dt, _, us = dt_str.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)


def url_extracting(self, content_url, content_node, force=False):
    now = datetime.datetime.now()
    now_iso = now.isoformat()
    meta_type = self.meta_type

    extract = {
            'content_md5':'',
            'content_datetime':'',
            'content_cache':''
        }
    
    res = self.url_extract.sql_select(zms_id=self.getId())
    if len(res)>0:
        extract['content_md5']=res[0]['content_md5']
        extract['content_datetime']=res[0]['content_datetime']
        extract['content_cache']=res[0]['content_cache']
        dt_cached = gt(res[0]['content_datetime'])
    else:
        dt_cached = now

    # Check MD5/Refresh Content Once a Day or on Force
    if force or ( (now - dt_cached).days > 0 ) or len(res)==0:
        baseurl = re.compile(r'(https:\/\/(.*?)\/)').match(content_url)[0]
        proxies = {
            'http': self.getConfProperty('HTTP.proxy', self.getConfProperty('HTTPS.proxy',None)),
            'https':  self.getConfProperty('HTTPS.proxy', self.getConfProperty('HTTP.proxy',None)),
        }
        if proxies['http'] is not None:
            html = requests.get(content_url, proxies=proxies, verify=False).text
        else: 
            html = requests.get(content_url).text
        soup = BeautifulSoup(html, features='lxml')
        content = str(soup.select_one(content_node))
        md5 = hashlib.md5(content.encode()).hexdigest()

        md5_prev = extract['content_md5'] 
        extract['content_md5'] = md5
        extract['content_datetime'] = now_iso
        if force:
            extract['html'] = html

        if md5 != md5_prev:
            # Fix URLs in Content
            for attr in ['src','srcset','href']:
                content = content.replace('%s="/'%attr,'%s="%s'%(attr,baseurl))
            extract['content_cache'] = content
            # Save Cache On MD5-Diff
            cache_data_by_sql(self, extract=extract)
        else:
            self.url_extract.sql_update_datetime(zms_id=self.getId())

    return extract