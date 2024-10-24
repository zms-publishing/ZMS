## params: self

import hashlib
import datetime
import re

def gt(dt_str):
    ### How to convert Python's .isoformat() string back into datetime object
    ### https://stackoverflow.com/questions/28331512
    dt, _, us = dt_str.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)


def register_teaser( self ):
    now = datetime.datetime.now()
    now_iso = now.isoformat()
    zmscontext = self
    lang = self.REQUEST.get('lang','ger')
    html = zmscontext.getBodyContent(self.REQUEST) 
    if self.isActive(self.REQUEST):
        zmscontext.teaser_registry.sql_upsert(
            zms_id = zmscontext.getId(),
            client_id = zmscontext.getHome().getId(),
            uuid = zmscontext.get_uid(),
            change_dt = zmscontext.getLangFmtDate(zmscontext.attr('change_dt'), lang=lang, fmt_str='%Y-%m-%dT%H:%M:%S'),
            lang = lang,
            content_md5 = hashlib.md5(html.encode()).hexdigest(),
            content_datetime = now_iso,
            content_cache = html
        )
    return html