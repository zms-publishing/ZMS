"""
ZMSWorkflowActivitiesManager.py

ZMS support for zmsworkflow activities manager.

License: GNU General Public License v2 or later
Organization: ZMS Publishing
"""
import ZPublisher.HTTPRequest
import copy

from Products.zms import _blobfields
from Products.zms import standard


class ZMSWorkflowActivitiesManager(object):
  """Manage workflow activities used by transitions and repository export."""

  def provideRepositoryActivities(self, r, ids=None):
    """Write local workflow activities into the repository export payload."""
    standard.writeBlock(self, "[provideRepositoryActivities]: ids=%s" % str(ids))
    r['workflow']['Activities'] = []
    for id in self.getActivityIds():
      d = self.getActivity(id)
      d['id'] = id
      r['workflow']['Activities'].append(d)


  def updateRepositoryActivities(self, r):
    """
    Replace local activities from a repository import payload.

    @param r: Imported workflow activity payload.
    @type r: C{dict}
    @return: Imported workflow id.
    @rtype: C{str}
    """
    id = r['id']
    standard.writeBlock(self, "[updateRepositoryActivities]: id=%s" % id)
    self.activities = []
    for attr in r.get('Activities', []):
      self.setActivity(attr['id'], attr['id'], attr['name'], attr.get('icon_clazz'), attr.get('icon'))
    return id


  def setActivity(self, id, newId, newName, newIconClazz=None, newIcon=None):
    """Create or update one workflow activity and optional icon blob."""
    obs = self.activities
    if id in obs:
      i = obs.index(id)
      del obs[i]
      del obs[i]
    else:
      i = len(obs)
    newValues = {}
    newValues['name'] = newName
    newValues['icon_clazz'] = newIconClazz
    newValues['icon'] = newIcon
    for obj_id in ['%s.icon' % str(id), '%s.icon' % str(newId)]:
      if obj_id in self.objectIds():
        self.manage_delObjects([obj_id])
    if isinstance(newIcon, _blobfields.MyBlob):
      self.manage_addFile(id='%s.icon' % newId, title=newIcon.getFilename(), file=newIcon.getData())
    obs.insert(i, newValues)
    obs.insert(i, newId)
    self.activities = copy.copy(obs)
    return newId


  def getActivities(self):
    """Return all configured activities as a list of dictionaries."""
    obs = self.activities
    activities = []
    for i in range(len(obs) // 2):
      id = obs[i * 2]
      activity = obs[i * 2 + 1].copy()
      activity['id'] = id
      activities.append(activity)
    return activities


  def getActivityIds(self):
    """Return all workflow activity ids in configured order."""
    obs = self.getActivities()
    return [x['id'] for x in obs]


  def getActivity(self, id, for_export=False):
    """
    Return one activity by id.

    When C{for_export} is false and an icon exists, the icon value is converted
    to an absolute icon URL.
    """
    activity = None
    activities = [x for x in self.getActivities() if x['id'] == id]
    if activities:
      activity = activities[0]
      if not for_export:
        d = {}
        for key in activity:
          if key == 'icon' and activity.get('icon'):
            d[key] = self.absolute_url() + '/' + id + '.icon'
          else:
            d[key] = activity[key]
        activity = d
    return activity


  def getActivityDetails(self, id):
    """Return transition relation indexes for an activity graph view."""
    ids = self.getActivityIds()
    froms = []
    tos = []
    for transition in self.getTransitions():
      if transition['to'] is not None and len(transition['to']) > 0 and id in transition['to']:
        for ac_id in transition['from']:
          if ac_id in ids:
            idx = ids.index(ac_id)
            if idx not in froms:
              froms.append(idx)
      if transition['from'] is not None and len(transition['from']) > 0 and id in transition['from']:
        for ac_id in transition['to']:
          if ac_id in ids:
            idx = ids.index(ac_id)
            if idx not in tos:
              tos.append(idx)
    froms.sort()
    tos.sort()
    idxs = standard.concat_list(froms, tos)
    idx = ids.index(id)
    return {'froms': froms, 'tos': tos, 'idxs': idxs, 'idx': idx}


  def manage_changeActivities(self, lang, btn='', REQUEST=None, RESPONSE=None):
    """Handle add/edit/delete/reorder actions for workflow activities in the ZMI."""
    message = ''
    id = REQUEST.get('id', '')

    if btn in ['BTN_CANCEL', 'BTN_BACK']:
      id = ''

    if btn == 'BTN_SAVE':
      item = self.getActivity(id, for_export=True)
      newId = REQUEST.get('inpId').strip()
      newName = REQUEST.get('inpName').strip()
      newIconClazz = REQUEST.get('inpIconClazz', '').strip()
      newIcon = None
      if len(newIconClazz) == 0:
        newIcon = REQUEST.get('inpIcon', '')
        if isinstance(newIcon, ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(newIcon, 'filename', '')) == 0:
            newIcon = item.get('icon', None)
          else:
            newIcon = _blobfields.createBlobField(self, _blobfields.MyImage, newIcon)
      id = self.setActivity(item.get('id', None), newId, newName, newIconClazz, newIcon)
      message = self.getZMILangStr('MSG_CHANGED')

    elif btn == 'BTN_DELETE':
      id = self.delItem(id, 'activities')
      message = self.getZMILangStr('MSG_CHANGED')

    elif btn == 'BTN_INSERT':
      item = {}
      newId = REQUEST.get('newId').strip()
      newName = REQUEST.get('newName').strip()
      newIconClazz = REQUEST.get('newIconClazz', '').strip()
      newIcon = None
      if len(newIconClazz) == 0:
        newIcon = REQUEST.get('newIcon', '')
        if isinstance(newIcon, ZPublisher.HTTPRequest.FileUpload):
          if len(getattr(newIcon, 'filename', '')) == 0:
            newIcon = item.get('icon', None)
          else:
            newIcon = _blobfields.createBlobField(self, _blobfields.MyImage, newIcon)
      id = self.setActivity(item.get('id', None), newId, newName, newIconClazz, newIcon)
      message = self.getZMILangStr('MSG_INSERTED') % id

    elif btn == 'move_to':
      pos = REQUEST['pos']
      self.moveItem(id, pos, 'activities')
      message = self.getZMILangStr('MSG_MOVEDOBJTOPOS') % (("<i>%s</i>" % id), (pos + 1))
      id = ''

    message = standard.url_quote(message)
    return RESPONSE.redirect('manage_main?lang=%s&manage_tabs_message=%s' % (lang, message))
