"""
_zpublish_guard.py - ZPublisher Guard API

Return 404 on non-publishable URL calls (ZPublisher.zpublish).

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

import importlib
from ZPublisher import zpublish, zpublish_marked

NOT_PUBLISHABLE = {
    'IZMSCatalogConnector': (
        'reindex_page',
    ),
    'IZMSConfigurationProvider': (
        'setArtefacts',
    ),
    'IZMSRepositoryManager': (
        'exec_auto_commit',
        'exec_auto_update',
    ),
    'ZMSCharformatManager': (
        'importCharformatXml',
        'moveCharformat',
        'delCharformat',
        'setCharformat',
    ),
    'ZMSFilterManager': (
        'updateRepository',
        'importXml',
        'setFilter',
        'delFilter',
        'setFilterProcess',
        'delFilterProcess',
        'moveFilterProcess',
        'setProcess',
        'delProcess',
    ),
    'ZMSLLMConnector': (
        'updateRepository',
    ),
    'ZMSMetacmdProvider': (
        'updateRepository',
        'importXml',
        'delMetacmd',
        'setMetacmd',
    ),
    'ZMSMetadictManager': (
        'updateRepositoryMetas',
        'importMetadictXml',
        'delMetadictAttr',
        'setMetadictAttr',
        'moveMetadictAttr',
    ),
    'ZMSMetamodelProvider': (
        'updateRepository',
    ),
    'ZMSMetaobjManager': (
        'updateRepositoryModel',
        'importMetaobjXml',
        'importTheme',
        'setMetaobj',
        'delMetaobj',
        'setMetaobjAttr',
        'delMetaobjAttr',
        'moveMetaobjAttr',
    ),
    'ZMSRepositoryManager': (
        'commitChanges',
        'updateChanges',
    ),
    'ZMSTextformat': (
        'setId',
        'setDisplay',
        'setTag',
        'setSubTag',
        'setAttrs',
        'setRichedit',
        'setUsage',
    ),
    'ZMSTextformatManager': (
        'importTextformatXml',
        'delTextformat',
        'setTextformat',
        'setDefaultTextformat',
    ),
    'ZMSWorkflowActivitiesManager': (
        'updateRepositoryActivities',
        'setActivity',
    ),
    'ZMSWorkflowProvider': (
        'updateRepository',
        'importXml',
        'setRevision',
        'delItem',
        'moveItem',
        'doAutocommit',
    ),
    'ZMSWorkflowProviderAcquired': (
        'doAutocommit',
    ),
    'ZMSWorkflowTransitionsManager': (
        'updateRepositoryTransitions',
        'setTransition',
    ),
    'ZMSZCatalogAdapter': (
        'reindex',
        'reindex_node',
        'unindex_nodes',
        'setIds',
        'setCustomFilterFunction',
        'setAttrIds',
        'setAttrs',
        'add_connector',
    ),
    'ZMSZCatalogConnector': (
        'updateRepository',
        'reindex_page',
    ),
    '_accessmanager': (
        'doAddUser',
        'removeUser',
        'synchronizePublicAccess',
        'synchronizeRolesAccess',
        'initRoleDefs',
        'setUserAttr',
        'delUser',
        'delUserAttr',
        'purgeLocalUsers',
        'setLocalUser',
        'delLocalUser',
    ),
    '_cachemanager': (
        'clearReqBuff',
        'storeReqBuff',
    ),
    '_conf': (
        'set_properties',
        'set_property',
        'del_property',
        'updateRepository',
    ),
    '_confmanager': (
        'importConfPackage',
        'importConf',
    ),
    '_filtermanager': (
        'initExportFilter',
        'execProcessFilter',
    ),
    '_globals': (
        'setEnv',
    ),
    '_mediadb': (
        'setLocation',
        'storeFile',
    ),
    '_multilangmanager': (
        'setPrimaryLanguage',
        'setLangs',
        'setLanguage',
        'delLanguage',
        'set_lang_dict',
    ),
    '_objattrs': (
        'attr',
        'setReqProperty',
        'setObjProperty',
        'synchronizeObjAttr',
        'synchronizeObjAttrs',
    ),
    '_objchildren': (
        'initObjChild',
        'initObjChildren',
    ),
    '_versionmanager': (
        'syncObjModifiedChildren',
        'resetObjTranslation',
        'initializeWorkVersion',
        'setObjState',
        'delObjStates',
        'resetObjStates',
        'setObjStateNew',
        'setObjStateModified',
        'setObjStateDeleted',
        'commitObjChanges',
        'rollbackObjChanges',
        'restoreObjVersion',
        'resetWfStates',
        'commitObj',
        'rollbackObj',
    ),
    '_zreferableitem': (
        'synchronizeRefByObjs',
        'registerRefObj',
        'changeRefsToObj',
    ),
    'llmtools': (
        'execute_llmtool',
    ),
    'zms': (
        'initZMS',
    ),
    'zmscontainerobject': (
        'moveObjsToTrashcan',
    ),
    'zmslinkelement': (
        'setEmbedType',
        'initProxy',
    ),
    'zmslog': (
        'setProperties',
    ),
    'zmsobject': (
        'set_uid',
        'clear_request_context',
        'set_request_context',
        'changeProperties',
        'setSortId',
    ),
    'zmssqldb': (
        'setModel',
        'commit',
        'rollback',
        'execute',
        'executeQuery',
        'delete_blob',
        'set_blob',
    ),
    'zmstrashcan': (
        'run_garbage_collection',
    ),
}


def apply():
    """Mark the listed methods as not publishable, unless already marked."""
    for modname, names in NOT_PUBLISHABLE.items():
        module = importlib.import_module('Products.zms.' + modname)
        for cls in vars(module).values():
            if not isinstance(cls, type) or cls.__module__ != module.__name__:
                continue
            for name in names:
                func = vars(cls).get(name)
                if callable(func) and not zpublish_marked(func):
                    setattr(cls, name, zpublish(False)(func))


apply()
