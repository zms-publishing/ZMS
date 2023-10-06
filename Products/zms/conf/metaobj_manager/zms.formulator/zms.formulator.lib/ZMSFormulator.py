# -*- coding: utf-8 -*-
################################################################################
#
#  Copyright (c) 2017 HOFFMANN+LIEBENBERG in association with SNTL Publishing
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from Zope2.App.startup import getConfiguration
from Products.zms import standard
import time
import requests
from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.dialects.mysql import DATETIME


def ZMSFormulator(self, this):
  return ZMSFormulator_class(this)


class ZMSFormulator_class:

  def __init__(self, this):

    self.this         = this
    self.thisURLPath  = this.absolute_url()
    self.baseURLPath  = this.getDocumentElement().absolute_url()
    self.thisMaster   = this.breadcrumbs_obj_path(True)[0]
    self.GoogleAPIKey = self.this.getConfProperty('Google.API.sitekey.password', self.thisMaster.getConfProperty('Google.API.sitekey.password','no_site_key'))
    self.GoogleAPISec = self.this.getConfProperty('Google.API.secretkey.password', self.thisMaster.getConfProperty('Google.API.secretkey.password','no_secret_key'))
    self.dbconnection = self.this.getConfProperty('ZMSFormulator.dbconnection.password', self.thisMaster.getConfProperty('ZMSFormulator.dbconnection.password','mysql://root@127.0.0.1:3306/zms_forms'))
    self.titlealt     = this.attr('titlealt')
    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.feedbackMsg  = this.attr('feedbackMsg').strip()
    self.options      = this.attr('optionsJS')
    self.onReady      = this.attr('onReadyJS')
    self.onChange     = this.attr('onChangeJS')
    self.noStorage    = this.attr('dataStorageDisabled')
    self.SQLStorage   = this.attr('dataStorageSQL')
    self.sendViaMail  = this.attr('sendViaMail')
    self.mailAddress  = this.attr('sendViaMailAddress').strip()
    self.fromAddress  = this.attr('sendViaMailFrom').strip() == '' and self.this.getConfProperty('ZMSAdministrator.email', self.thisMaster.getConfProperty('ZMSAdministrator.email','')) or this.attr('sendViaMailFrom').strip()
    self.mailTextTo   = this.attr('mailTextTo').strip()
    self.mailTextCc   = None
    self.mailDataIncl = None
    self.replyAddress = None
    self.copyAddress  = None
    self.mailAttchmnt = None
    self.mailFrmt     = this.attr('mailFrmt')
    self.mailFrmtCSS  = this.attr('mailFrmtCSS').strip()
    self.items        = []
    self._data        = {}

    # init _data
    if self.getData() is None:
      raise SystemError('Storage not available')

    # init items
    objs = list(filter(lambda ob: ob.isActive(self.this.REQUEST), self.this.getObjChildren('formulatorItems', self.this.REQUEST, ['ZMSFormulatorItem', 'ZMSTextarea'])))
    for item in objs:
      self.items.append(ZMSFormulatorItem(item))

  def getData(self):

    if self.SQLStorage and not self.noStorage:
      self.engine = create_engine(self.dbconnection + '?charset=utf8mb4')
      metadata = MetaData()
      try:
        self.sqldb = Table(self.this.getId(), metadata, autoload=True, autoload_with=self.engine)
        if 'ZMS_FRM_USR' not in self.sqldb.columns:
          alt = 'ALTER TABLE %s ADD COLUMN `ZMS_FRM_USR` VARCHAR(128) NULL AFTER `ZMS_FRM_URL`;'%self.this.getId()
          try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with self.engine.connect() as conn:
              conn.execute(alt)
          except Exception as e:
            raise e
          finally:
            conn.close()
        if 'ZMS_FRM_UID' not in self.sqldb.columns:
          alt = 'ALTER TABLE %s ADD COLUMN `ZMS_FRM_UID` VARCHAR(128) NULL AFTER `ZMS_FRM_OID`;'%self.this.getId()
          try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with self.engine.connect() as conn:
              conn.execute(alt)
          except Exception as e:
            raise e
          finally:
            conn.close()
      except NoSuchTableError:
        self.sqldb = Table(self.this.getId(), metadata,
                           Column('ZMS_FRM_ITM', BigInteger(), primary_key=True),
                           Column('ZMS_FRM_OID', BigInteger()),
                           Column('ZMS_FRM_UID', String(128)),
                           Column('ZMS_FRM_EID', String(32)),
                           Column('ZMS_FRM_CID', String(32)),
                           Column('ZMS_FRM_FID', String(32)),
                           Column('ZMS_FRM_URL', String(512)),
                           Column('ZMS_FRM_USR', String(128)),
                           Column('ZMS_FRM_MDT', Boolean()),
                           Column('ZMS_FRM_HID', Boolean()),
                           Column('ZMS_FRM_MIN', Integer()),
                           Column('ZMS_FRM_MAX', Integer()),
                           Column('ZMS_FRM_DFT', String(128)),
                           Column('ZMS_FRM_KEY', String(128)),
                           Column('ZMS_FRM_ALT', String(64)),
                           Column('ZMS_FRM_TXT', String(512)),
                           Column('ZMS_FRM_TYP', String(32)),
                           Column('ZMS_FRM_ORD', SmallInteger()),
                           Column('ZMS_FRM_RAW', Text()),
                           Column('ZMS_FRM_RES', Text()),
                           Column('ZMS_FRM_TST', DATETIME(fsp=6)),
                           )
        metadata.create_all(self.engine)
      except:
        return None

      sel = select([
                    self.sqldb.c.ZMS_FRM_TST,
                    self.sqldb.c.ZMS_FRM_KEY,
                    self.sqldb.c.ZMS_FRM_ALT,
                    self.sqldb.c.ZMS_FRM_RES]
                   ).order_by(self.sqldb.c.ZMS_FRM_KEY)
      try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with self.engine.connect() as conn:
          res = conn.execute(sel)
      except Exception as e:
        raise e
      finally:
        conn.close()

      self._data = res

    elif not self.SQLStorage  and not self.noStorage:
      lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
      self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
      data = self.this.attr('_data')
      self._data.update(data)
      self.this.REQUEST.set('lang', lang)

    return self._data

  def clearData(self):

    if self.SQLStorage and not self.noStorage:
      try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with self.engine.connect() as conn:
          res = conn.execute(self.sqldb.delete())
      except Exception as e:
        raise e
      finally:
        conn.close()

      return True
    else:
      self._data.clear()
      zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
      if not zodb.isReadOnly() and not self.noStorage:
        lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
        self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
        self.this.setObjStateModified(self.this.REQUEST)
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
        self.this.commitObj(self.this.REQUEST,forced=True)
        self.this.REQUEST.set('lang', lang)
        return True
      else:
        standard.writeBlock(self.thisMaster, "[ZMSFormulator.clearData] zodb.isReadOnly")
        return False

  def setData(self, receivedData):

    if type(receivedData) is not dict:
      standard.writeError(self.thisMaster, "[ZMSFormulator.setData] unexpected data (not dict)")
      return False

    for timestamp in receivedData:
      for key, val in receivedData[timestamp]:

        # normalize received ZMSFormulatorItem-Key due to arrays/objects
        # fetch matching ZMSFormulatorItem-Obj to retrieve ids and values
        if '[' in key:
          itemkey = key.split('[')[0].upper()
        else:
          itemkey = key.upper()
        if itemkey == 'RECAPTCHA':
          continue
        if itemkey.startswith('TEXTAREA_'):
          continue
        if itemkey == 'LANG':
          continue

        ZMS_FRM_RES = self.this.str_item(val).strip()

        # handle response value for first item found in content model
        item = list(filter(lambda x: standard.id_quote(x.titlealt).upper() == itemkey, self.items))
        if len(item)>0:
          itemobj = item[0]
          if itemobj.type == 'email':
            emailpattern = '^([a-zA-Z0-9_.+-])+\\@(([a-zA-Z0-9-])+\\.)+([a-zA-Z0-9]{2,4})+$'
            if self.this.re_search(emailpattern, ZMS_FRM_RES) is not None:
              self.replyAddress = itemobj.replyToField and ZMS_FRM_RES or None
              self.copyAddress = itemobj.copyToField and ZMS_FRM_RES or None
              self.mailTextCc = itemobj.mailTextCc
              self.mailDataIncl = itemobj.mailDataIncl
        # no matching item found in content model
        else:
          raise ValueError("malformed content model or inexistant model in primary language)")

        if itemobj.type in ['select', 'checkbox', 'multiselect']:
          ZMS_FRM_RES = ZMS_FRM_RES.replace('\n',', ')
          ZMS_FRM_RAW = ', '.join(itemobj.select.splitlines())
        else:
          ZMS_FRM_RAW = itemobj.rawJSON

        # save data as records to SQLDB
        if self.SQLStorage and not self.noStorage:
          modelledData = self.this.JSONEditor(self)

          from datetime import datetime
          ins = self.sqldb.insert().values(
            ZMS_FRM_TST = datetime.fromtimestamp(timestamp),
            ZMS_FRM_RES = ZMS_FRM_RES,
            ZMS_FRM_ORD = 'propertyOrder' in modelledData.JSONDict['properties'][itemkey] and modelledData.JSONDict['properties'][itemkey]['propertyOrder'] or 0,
            ZMS_FRM_OID = int(itemobj.oid[4:]),
            ZMS_FRM_UID = 'uid:' in itemobj.uid and itemobj.uid[4:] or None,
            ZMS_FRM_EID = itemobj.eid[:32],
            ZMS_FRM_CID = itemobj.cid[:32],
            ZMS_FRM_FID = itemobj.fid[:32],
            ZMS_FRM_URL = itemobj.url[:512],
            ZMS_FRM_USR = str(self.this.REQUEST.get('AUTHENTICATED_USER',''))[:128],
            ZMS_FRM_TYP = itemobj.type[:32],
            ZMS_FRM_KEY = key[:128], # put the received key including arrays/objects instead of plain itemobj.titlealt
            ZMS_FRM_ALT = itemobj.title[:64],
            ZMS_FRM_TXT = itemobj.description[:512],
            ZMS_FRM_MDT = itemobj.mandatory,
            ZMS_FRM_HID = itemobj.hidden,
            ZMS_FRM_MIN = itemobj.minimum,
            ZMS_FRM_MAX = itemobj.maximum,
            ZMS_FRM_DFT = itemobj.default[:128],
            ZMS_FRM_RAW = ZMS_FRM_RAW,
            )
          try:
            # Using a with statement ensures that the connection is always released
            # back into the pool at the end of statement (even if an error occurs)
            with self.engine.connect() as conn:
              res = conn.execute(ins)
          except Exception as e:
            raise e
          finally:
            conn.close()

          self._data = res

    if type(self._data) is dict:
      self._data.update(receivedData)

    # save data as dictionary to ZODB
    if not self.SQLStorage and not self.noStorage:
      zodb = getConfiguration().dbtab.getDatabase('/', is_root=1)._storage
      if not zodb.isReadOnly():
        lang = self.this.REQUEST.get('lang', self.this.getPrimaryLanguage())
        self.this.REQUEST.set('lang', self.this.getPrimaryLanguage())
        self.this.setObjStateModified(self.this.REQUEST)
        self.this.attr('_data', self._data)
        self.this.onChangeObj(self.this.REQUEST)
        self.this.commitObj(self.this.REQUEST,forced=True)
        self.this.REQUEST.set('lang', lang)
        return True
      else:
        standard.writeBlock(self.thisMaster, "[ZMSFormulator.setData] zodb.isReadOnly")
        return False

  def receiveData(self, data=None):

    if data is None:
      data = list(self.this.REQUEST.form.items())

    if len(data)>0:

      isOK = False
      error = None
      remVal = []

      for i, item in enumerate(data):
        key, val = item

        # identify response values in received data which should not be stored
        if key == 'reCAPTCHA':
          reCAPTCHA = val
          remVal.append(i)
        if key == 'LANG':
          remVal.append(i)
        if key.startswith('TEXTAREA_'):
          remVal.append(i)
        if key.endswith('[FILEDATA]'):
          if val.strip() != '':
            self.mailAttchmnt = self.mailAttchmnt and (self.mailAttchmnt + val) or val
          remVal.append(i)
        if key.endswith('[FILENAME]'):
          if val.strip() != '':
            self.mailAttchmnt = 'filename:%s;'%val + (self.mailAttchmnt and self.mailAttchmnt or '')

      # Google.API.sitekey.password disabled
      if self.GoogleAPIKey == 'no_site_key':
        isOK = True

      # check if input was sent by a robot
      # hand over response value to reCAPTCHA service by Google
      else:
        url = 'https://www.google.com/recaptcha/api/siteverify'
        val = {'secret' : self.GoogleAPISec,
               'response' : reCAPTCHA}
        verification = requests.post(url, val).json()

        if 'success' in verification:
          isOK = verification['success']
          if not isOK:
            if 'error-codes' in verification:
              error = verification['error-codes']

      if isOK:
        # remove response values identified above from data to be stored
        if len(remVal)>0:
          for i, pos in enumerate(remVal):
            data.pop(pos-i)
        # add current timestamp and store data
        data = {time.time(): data}
        self.setData(data)
        # send data by mail if configured
        if self.sendViaMail == True:
          self.sendData(data)
        return True

      elif error:
        standard.writeError(self.thisMaster, "[ZMSFormulator.receiveData] error occurred while using reCAPTCHA service by Google: %s"%error)
        return False

      else:
        standard.writeError(self.thisMaster, "[ZMSFormulator.receiveData] input by robot detected")
        return False

    else:
      standard.writeError(self.thisMaster, "[ZMSFormulator.receiveData] unexpected data received")
      return False

  def sendData(self, receivedData):

    if self.mailAddress != '':
      msubj = '[%s] Data submitted: %s' % (self.this.getLangStr('TYPE_ZMSFORMULATOR'), self.title)
      mbody = []
      mbody.append(self.title)
      mbody.append('\n')
      base = ''
      href = self.this.getHref2IndexHtml(self.this.REQUEST)
      if self.thisMaster.getConfProperty('ZMS.pathcropping',0)==1:
        base = self.this.REQUEST.get('BASE0','')
      mbody.append(base+href)
      mbody.append('\n\n')

      # [TO] send confirmation mail to form recipient
      mheadTo = {'To': self.mailAddress, 'From': self.fromAddress}
      mtemp = []
      mtemp.append({'text': ''.join(mbody) + self.mailTextTo + '\n\n' + self.printDataRaw(receivedData, frmt='tab'), 'subtype': 'plain'})
      if self.mailFrmt in [True, 1]:
        html = self.printDataPretty(receivedData, ref=''.join(mbody), mailtxt=self.mailTextTo.replace('\r\n', '<br />'))
        mtemp.append({'text': html.replace('\nhttp://','</h1><h3>http://').replace('\nhttps://','</h1><h3>https://').replace('\n\n\n','</h3>'), 'subtype':'html'})

      mbodyTo = mtemp
      if self.replyAddress is not None:
        mheadTo['Reply-To'] = self.replyAddress

      rtn = self.thisMaster.sendMail(mheadTo, msubj, mbodyTo, self.this.REQUEST, self.mailAttchmnt)
      if rtn < 0:
        standard.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail")

      # [CC] send confirmation mail to form sender
      if self.copyAddress is not None:
        mheadCc = {'To': self.copyAddress, 'From': self.fromAddress}
        mtemp = []
        # include sent data
        if self.mailDataIncl in [True, 1]:
          mtemp.append({'text': ''.join(mbody) + self.mailTextCc + '\n\n' + self.printDataRaw(receivedData, frmt='tab'), 'subtype': 'plain'})
          if self.mailFrmt in [True, 1]:
            html = self.printDataPretty(receivedData, ref=''.join(mbody), mailtxt=self.mailTextCc.replace('\r\n', '<br />'))
            mtemp.append({'text': html.replace('\nhttp://', '</h1><h3>http://').replace('\nhttps://', '</h1><h3>https://').replace('\n\n\n', '</h3>'), 'subtype': 'html'})
        # do not include sent data
        else:
          mtemp.append({'text': ''.join(mbody) + self.mailTextCc, 'subtype': 'plain'})
          if self.mailFrmt in [True, 1]:
            html = ''.join(mbody) + '</h3>' + self.mailTextCc.replace('\r\n', '<br />')
            mtemp.append({'text': html.replace('\nhttp://', '</h1><h3>http://').replace('\nhttps://', '</h1><h3>https://').replace('\n\n\n', '</h3>'), 'subtype': 'html'})

        mbodyCc = mtemp
        rtn = self.thisMaster.sendMail(mheadCc, msubj, mbodyCc, self.this.REQUEST)
        if rtn < 0:
          standard.writeError(self.thisMaster, "[ZMSFormulator.sendData] failed to send mail as copy")
    else:
      standard.writeError(self.thisMaster, "[ZMSFormulator.sendData] no mail address specified")

  def printDataRaw(self, receivedData=None, frmt='txt'):

    data = self.getData()
    header = ['TIMESTAMP']
    output = []
    s = '' # text stream

    # Received data
    if isinstance(receivedData, dict):
      data = receivedData

    # Handle ZODB-Dictionary and REQUEST-Data
    if isinstance(data, dict):
      if frmt=='txt':
        s = '%s entries:\n\n'%len(data)

      # data values
      if len(data) > 0:
        s1 = ''
        sorted_v = {}
        for t, v in sorted(list(data.items())):
          output = []
          output.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t)))
          sorted_v = sorted(v)
          for i in sorted_v:
            i1, i2 = i
            outstr = self.this.str_item(i2)
            outstr = outstr.replace('\n',', ')
            output.append(standard.html_quote(outstr))
          s1 += '#/#'.join(output) + '\n'

        # data header
        s0 = ''
        for i in sorted(v):
          i1, i2 = i
          header.append(i1)
        s0 += '#/#'.join(header).upper() +'\n'
        s = s0 + s1

    # Handle SQL-Storage
    else:
      sel = select([self.sqldb.c.ZMS_FRM_TST]).group_by(self.sqldb.c.ZMS_FRM_TST)
      try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with self.engine.connect() as conn:
          res = conn.execute(sel)
      except Exception as e:
        raise e
      finally:
        conn.close()

      if frmt=='txt':
        s = '%s entries:\n\n'%res.rowcount

      sel = select([self.sqldb.c.ZMS_FRM_KEY, self.sqldb.c.ZMS_FRM_ORD]).distinct().order_by(self.sqldb.c.ZMS_FRM_ORD, self.sqldb.c.ZMS_FRM_KEY)
      try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with self.engine.connect() as conn:
          res1 = conn.execute(sel)
      except Exception as e:
        raise e
      finally:
        conn.close()

      sel = select([self.sqldb.c.ZMS_FRM_KEY, self.sqldb.c.ZMS_FRM_ALT, self.sqldb.c.ZMS_FRM_RES, self.sqldb.c.ZMS_FRM_TST]).order_by(self.sqldb.c.ZMS_FRM_TST, self.sqldb.c.ZMS_FRM_KEY)
      try:
        # Using a with statement ensures that the connection is always released
        # back into the pool at the end of statement (even if an error occurs)
        with self.engine.connect() as conn:
          res2 = conn.execute(sel)
      except Exception as e:
        raise e
      finally:
        conn.close()

      for head in res1:
        header.append(head[0])

      from collections import defaultdict
      records = defaultdict(dict)
      for rec in res2:
        frm_key = rec[0]
        frm_res = rec[2]
        frm_tst = rec[3]
        records[frm_tst][frm_key] = frm_res

      for tst, key in sorted(list(records.items())):
        rec = []
        for h in header:
          if h in key:
            outstr = key[h]
            outstr = outstr.replace('\n',', ')
            rec.append(standard.html_quote(outstr))
          elif (h!='TIMESTAMP'):
            rec.append('')
        output.append('\n'+str(tst))
        output.extend(rec)

      s1 = '#/#'.join(header)
      s2 = '#/#'.join(output)

      s += s1.upper() + s2.replace('#/#\n', '\n')

    # Return data for download as CSV file
    # handle special characters Latin-1 mapping in conf/zms.formulator.metaobj.xml line 1480 et seq.
    if (frmt == 'csv'):
      import csv
      from io import StringIO
      stream = StringIO()
      csvdat = csv.writer(stream, dialect='excel', delimiter=';', quoting=csv.QUOTE_ALL)

      for line in s.splitlines():
        csvdat.writerow(line.split('#/#'))

      return stream.getvalue().replace('&quot;','""')

    # Render current transmitted item (last element in output-list)
    # line-by-line tab-separated to be used in sendData by mail
    if (frmt == 'tab'):
      s = ''
      # Get sorted form names
      formnames = ['TIMESTAMP']
      formtitles = ['TIMESTAMP']
      objs = list(filter(lambda ob: ob.isActive(self.this.REQUEST), self.this.getObjChildren('formulatorItems', self.this.REQUEST, ['ZMSFormulatorItem'])))
      for obj in objs:
        formnames.append(standard.id_quote(obj.attr('titlealt')).upper())
        formtitles.append(obj.attr('title'))

      if len(output)>=len(header):
        l = zip(header, output[-len(header):])
        d = {}
        for i in l:
          d[str(i[0])] = str(i[1])
        for i, f in enumerate(formnames):
          for k in list(d.keys()):
            if f == k.split('[')[0]:
              desc = formtitles[i]
              cont = d[k].strip().replace('&quot;','"').replace('&amp;','&')
              if cont=='':
                continue
              if len(desc)<8:
                tab = '\t\t\t'
              elif len(desc)<16:
                tab = '\t\t'
              else:
                tab = '\t'
              if desc.endswith('[]'):
                line = cont.split(', ')
                cont = ('\n\t'+tab).join(line)
              s += desc + tab + cont + '\n'
              # destructive iteration: avoid doubled output
              del d[k]
      s += '\n'

    return s

  def printDataPretty(self, receivedData, ref='', mailtxt=''):

    # TODO: cleanup this fragile replace-orgy and abstract frmt-handling
    return """
      <html>
        <head>
          <style>
            %s
          </style>
        </head>
        <body>
          <h1>%s
          %s
          <br />
          <table>
            <tr><th>%s
          </table>
        </body>
      </html>
    """%(self.mailFrmtCSS, ref, mailtxt,
         self.printDataRaw(receivedData,frmt='tab').replace('\n\t\t\t\t','</td></tr>\n<tr><th></th><td>').replace('\n\t\t\t','</td></tr>\n<tr><th></th><td>').replace('\n\t\t','</td></tr>\n<tr><th></th><td>').replace('\n\t','</td></tr>\n<tr><th></th><td>').replace('\t\t\t','</th><td>').replace('\t\t','</th><td>').replace('\t','</th><td>').replace('\n','</td></tr>\n<tr><th>').replace('<tr><td><tr><td>','<tr><th>').replace('</td></tr></td></tr>','</td></tr>').replace('<tr><th></td></tr>\n<tr><td>',''))

class ZMSFormulatorItem:

  def __init__(self, this):

    self.eid          = this.getId()
    self.oid          = this.get_oid()
    self.uid          = this.get_uid()
    self.cid          = this.getHome().getId()
    self.fid          = this.getParentNode().getId()
    self.url          = this.getParentNode().getDeclUrl()
    self.meta_id      = this.meta_id
    self.bodycontent  = this.getBodyContent(this.REQUEST)

    # to keep headlines of DATA in sync for all language versions
    # use the value of titlealt in primary language always and ignore value of current language version
    lang = this.REQUEST.get('lang', this.getPrimaryLanguage())
    this.REQUEST.set('lang', this.getPrimaryLanguage())
    # titlealt_ remove square brackets, whitespaces etc. from user inputs to be used as key which does not interfere with formfield names
    self.titlealt     = standard.id_quote(this.attr('titlealt')).upper()
    this.REQUEST.set('lang', lang)

    self.title        = this.attr('title')
    self.description  = this.attr('attr_dc_description')
    self.type         = this.attr('type')
    self.default      = this.attr('valueDefault')
    self.minimum      = this.attr('valueMinimum')
    self.maximum      = this.attr('valueMaximum')
    self.select       = this.attr('valueSelect')
    self.rawJSON      = this.attr('rawJSON')
    self.mandatory    = this.attr('mandatoryField')
    self.hidden       = this.attr('hiddenField')
    self.replyToField = this.attr('replyToField')
    self.copyToField  = this.attr('copyToField')
    self.mailTextCc   = this.attr('mailTextCc').strip()
    self.mailDataIncl = this.attr('mailDataIncluded')