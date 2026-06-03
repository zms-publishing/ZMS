from AccessControl.SecurityInfo import ModuleSecurityInfo

security = ModuleSecurityInfo('Products.zms.coauthor')

security.declarePublic('get_ai_feature_settings')
def get_ai_feature_settings(zmscontext):
    """Return availability flags for AI-assisted translation helpers."""
    settings = {
        'ai_enabled': False,
        'metadata_enabled': True,
    }
    try:
        connector = zmscontext.getLLMConnector()
        if connector is not None:
            settings['ai_enabled'] = True
            settings['metadata_enabled'] = bool(connector.isFeatureEnabled('metadata_gen'))
    except Exception:
        pass
    return settings


class _field_request_proxy(dict):
    """Plain request mapping used when rendering isolated field widgets."""

    def __init__(self, request, **overrides):
        dict.__init__(self)
        try:
            self.update(dict(request))
        except Exception:
            for key in request.keys():
                self[key] = request[key]
        self.update(overrides)

    def set(self, key, value):
        self[key] = value


security.declarePublic('make_field_request')
def make_field_request(request, same_language=False, side='right', lang=None):
    """Create a per-field request snapshot with optional unique widget suffixes."""
    return request # Debug
    field_request = _field_request_proxy(request)
    if lang:
        field_request['lang'] = lang
    if same_language and side == 'left':
        fm_name = field_request.get('fmName', 'form0')
        el_name = field_request.get('elName', '')
        field_request['fmName'] = '%s_src' % fm_name
        if el_name:
            field_request['elName'] = '%s_src' % el_name
    return field_request


security.declarePublic('set_language_options')
def set_language_options(zmscontext, request, session):
    """Set language options in session and request."""
    request.set('lang', 'ger')
    request.set('preview', 'preview')

    coverage_delimiter = zmscontext.getDCCoverage(request).split('.')[0]
    lang1_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len(coverage_delimiter) + 1:])

    if session.get('lang1', '') == '':
        session.set('lang1', request.get('lang1', lang1_options[0][0]))
        request.set('lang1', session.get('lang1'))
    elif request.get('lang1', '') == '':
        request.set('lang1', session.get('lang1'))
    else:
        session.set('lang1', request.get('lang1'))

    request.set('lang1_options', lang1_options)
    request.set('lang1_bk', request.get('lang1'))

    lang2_options = zmscontext.getLangTree(zmscontext.getDCCoverage(request)[len(coverage_delimiter) + 1:])
    default_lang2 = request.get('lang1')
    for opt in lang2_options:
        if opt[0] != request.get('lang1'):
            default_lang2 = opt[0]
            break

    if session.get('lang2', '') == '':
        session.set('lang2', request.get('lang2', default_lang2))
        request.set('lang2', session.get('lang2'))
    elif request.get('lang2', '') == '':
        request.set('lang2', session.get('lang2'))
    else:
        session.set('lang2', request.get('lang2'))

    request.set('lang2_options', lang2_options)
    request.set('lang2_bk', request.get('lang2'))


security.declarePublic('get_coauthor_mode')
def get_coauthor_mode(request, session):
    """
    Get and persist the active coauthor mode (UI controls).
    
    Precedence order:
    1. If request parameter is set to a valid mode, use it, update session, and return it.
    2. If request parameter is not set, use session value if valid.
    3. Otherwise, default to 'edit' mode.
    4. If request parameter is set multiple times, the last one takes precedence (handled by request object).
    """
    valid_modes = ['edit', 'view']
    
    # Request parameter takes precedence: use it, sync to session, and return
    request_mode = request.get('coauthor_mode')
    # Handle case where request_mode is a list (e.g., ['edit', 'edit'])
    if isinstance(request_mode, list):
        request_mode = request_mode[0] if request_mode else None
    if request_mode and request_mode in valid_modes:
        session.set('coauthor_mode', request_mode)
        return request_mode
    
    # Fall back to session if no valid request parameter
    session_mode = session.get('coauthor_mode')
    if session_mode and session_mode in valid_modes:
        return session_mode
    
    # Default mode
    return 'edit'


security.declarePublic('get_debug_info')
def get_debug_info(request, session):
    """Return tooltip debug information for language/session state."""
    return 'REQUEST.lang1: %s | REQUEST.lang2: %s | SESSION.lang1: %s | SESSION.lang2: %s | SESSION.coauthor_mode: %s' % (
        request.get('lang1', ''),
        request.get('lang2', ''),
        session.get('lang1', ''),
        session.get('lang2', ''),
        session.get('coauthor_mode', ''),
    )


security.declarePublic('get_multilang_objattrs')
def get_multilang_objattrs(zmscontext):
    """Return multilingual attributes excluding technical/system ones."""
    technical_prefixes = ('change_', 'work_', 'attr_active_', 'created_', 'modified_')
    technical_attrs = ('uid', 'version', 'preview')
    objattrs = []
    for objattr_id in zmscontext.getObjAttrs():
        if objattr_id.startswith(technical_prefixes) or objattr_id in technical_attrs:
            continue
        metaobj_attr = zmscontext.getObjAttr(objattr_id)
        if metaobj_attr.get('multilang') in [1, True]:
            objattrs.append(metaobj_attr)
    return objattrs

