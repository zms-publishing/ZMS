"""
_zpublish_guard.py - ZPublisher Guard API (default-deny)

Zope publishes every method that carries a docstring unless it is explicitly
marked with ``@zpublish(False)`` (ZPublisher.zpublish). This module inverts
that default for the whole ``Products.zms`` package:

* Every public method of every class defined in this package is marked
  ``@zpublish(False)`` - unless it is listed in ``PUBLISHABLE`` below.
* Methods already carrying an explicit ``@zpublish`` mark in the source are
  never touched (the source mark always wins).
* New methods are therefore NOT publishable via URL by default
  ("secure by default"). To expose a method via URL, either decorate it in
  the source with ``@zpublish`` or add it to ``PUBLISHABLE``.

The ``PUBLISHABLE`` allow-list was derived from the actual URL surface of the
package: form actions and AJAX endpoints in ZPT templates and JS plugins,
``__ac_permissions__`` declarations, ``security.declare*`` names and
``RESPONSE.redirect()`` targets.

License: GNU General Public License v2 or later,
Organization: ZMS Publishing
"""

import importlib
import inspect
import os
import pkgutil

from ZPublisher import zpublish, zpublish_marked

# Import the package directory without going through ``Products.zms``
# (which imports this module and would cause a circular import).
_pkg_path = (os.path.dirname(os.path.abspath(__file__)),)

# Methods that shall remain publishable via URL.
# Structure: {module_name: {class_name: (method_names, ...)}}
PUBLISHABLE = {
    '_accessmanager': {
        'AccessManager': (
            'manage_roleProperties',
            'manage_userProperties',
        ),
        'AccessableObject': (
            'manage_user',
        ),
    },
    '_confmanager': {
        'ConfManager': (
            'getConfFiles',
            'getConfProperties',
            'getConfProperty',
            'importConf',
            'manage_customizeDesign',
            'manage_customizeSystem',
        ),
    },
    '_copysupport': {
        'CopySupport': (
            'manage_copyObject',
            'manage_cutObject',
            'manage_pasteObjs',
        ),
    },
    '_exportable': {
        'Exportable': (
            'manage_export',
        ),
    },
    '_mediadb': {
        'MediaDb': (
            'manage_changeProperties',
            'manage_index_html',
            'manage_test',
        ),
    },
    '_multilangmanager': {
        'MultiLanguageManager': (
            'get_lang_dict',
            'getLanguageLabel',
            'manage_changeLangDictProperties',
            'manage_changeLanguages',
        ),
        'MultiLanguageObject': (
            'getDescendantLanguages',
        ),
    },
    '_objattrs': {
        'ObjAttrs': (
            'ajaxGetObjOptions',
            'clearTempBlobjProperty',
            'getTempBlobjPropertyUrl',
            'manage_changeTempBlobjProperty',
        ),
    },
    '_objchildren': {
        'ObjChildren': (
            'manage_initObjChild',
        ),
    },
    '_sequence': {
        'Sequence': (
            'manage_changeProperties',
        ),
    },
    '_versionmanager': {
        'VersionItem': (
            'ajaxBodyContentObjHistory',
            'manage_UndoVersion',
        ),
        'VersionManagerContainer': (
            'manage_wfTransition',
            'manage_wfTransitionFinalize',
        ),
    },
    '_zmsattributecontainer': {
        'ZMSAttributeContainer': (
            'manage_changeProperties',
        ),
    },
    'zms': {
        'ZMS': (
            'manage_addMediaDb',
        ),
    },
    'zmscontainerobject': {
        'ZMSContainerObject': (
            'manage_addZMSCustom',
            'manage_addZMSCustomDefault',
            'manage_addZMSModule',
            'manage_addZMSObject',
            'manage_ajaxDragDrop',
            'manage_ajaxZMIActions',
            'manage_deleteObjs',
            'manage_eraseObjs',
            'manage_undoObjs',
        ),
    },
    'zmscustom': {
        'ZMSCustom': (
            'manage_changeRecordGrid',
            'manage_changeRecordSet',
            'manage_import',
            'recordSet_Export',
        ),
    },
    'zmsindex': {
        'ZMSIndex': (
            'manage_reindex',
            'manage_resync',
            'manage_test',
        ),
    },
    'zmslinkelement': {
        'ZMSLinkElement': (
            'manage_changeProperties',
        ),
    },
    'zmslog': {
        'ZMSLog': (
            'getLOG',
            'manage_index_html',
            'manage_submit',
        ),
    },
    'zmsobject': {
        'ZMSObject': (
            'ajaxGetBodyContent',
            'manage_changeProperties',
            'manage_executeMetacmd',
            'manage_moveObjDown',
            'manage_moveObjToPos',
            'manage_moveObjUp',
        ),
    },
    'zmssqldb': {
        'ZMSSqlDb': (
            'ajaxGetAutocompleteColumns',
            'ajaxGetObjOptions',
            'get_blob',
            'manage_changeConfiguration',
            'manage_changeProperties',
            'set_blob',
        ),
    },
    'zmstrashcan': {
        'ZMSTrashcan': (
            'manage_changeProperties',
        ),
    },
    'ZMSCharformatManager': {
        'ZMSCharformatManager': (
            'manage_changeCharformat',
        ),
    },
    'ZMSFilterManager': {
        'ZMSFilterManager': (
            'manage_changeFilter',
            'manage_changeProcess',
        ),
    },
    'ZMSItem': {
        'ZMSItem': (
            'display_icon',
            'readme',
            'zmi_page_request',
        ),
    },
    'ZMSLLMConnector': {
        'ZMSLLMConnector': (
            'manage_changeConfig',
            'manage_changeFeatures',
            'manage_changeProperties',
        ),
    },
    'ZMSMetacmdProvider': {
        'ZMSMetacmdProvider': (
            'getMetaCmdDescription',
            'manage_changeMetacmds',
        ),
    },
    'ZMSMetacmdProviderAcquired': {
        'ZMSMetacmdProviderAcquired': (
            'getMetaCmdDescription',
        ),
    },
    'ZMSMetadictManager': {
        'ZMSMetadictManager': (
            'manage_changeMetaProperties',
        ),
    },
    'ZMSMetamodelProvider': {
        'ZMSMetamodelProvider': (
            'metaobj_readme',
        ),
    },
    'ZMSMetaobjManager': {
        'ZMSMetaobjManager': (
            'manage_ajaxChangeProperties',
            'manage_changeProperties',
            'manage_create_default_zpt',
        ),
    },
    'ZMSRepositoryManager': {
        'ZMSRepositoryManager': (
            'manage_change',
        ),
    },
    'ZMSTextformatManager': {
        'ZMSTextformatManager': (
            'manage_changeTextformat',
        ),
    },
    'ZMSWorkflowActivitiesManager': {
        'ZMSWorkflowActivitiesManager': (
            'manage_changeActivities',
        ),
    },
    'ZMSWorkflowProvider': {
        'ZMSWorkflowProvider': (
            'manage_changeWorkflow',
        ),
    },
    'ZMSWorkflowProviderAcquired': {
        'ZMSWorkflowProviderAcquired': (
            'manage_changeWorkflow',
        ),
    },
    'ZMSWorkflowTransitionsManager': {
        'ZMSWorkflowTransitionsManager': (
            'manage_changeTransitions',
        ),
    },
    'ZMSZCatalogAdapter': {
        'ZMSZCatalogAdapter': (
            'manage_changeProperties',
        ),
    },
    'ZMSZCatalogConnector': {
        'ZMSZCatalogConnector': (
            'manage_changeProperties',
            'manage_destroy',
            'manage_init',
            'manage_objects_add',
            'manage_objects_clear',
            'manage_objects_remove',
            'reindex_page',
            'search_json',
            'search_xml',
            'suggest_json',
            'suggest_xml',
        ),
    },
}


def apply():
    """Default-deny: mark every public method of every class in the package
    as not publishable, unless it is allow-listed in ``PUBLISHABLE`` or
    already carries an explicit ``@zpublish`` mark in the source.
    """
    for modinfo in pkgutil.iter_modules(_pkg_path):
        module = importlib.import_module('Products.zms.' + modinfo.name)
        allowed = PUBLISHABLE.get(modinfo.name, {})
        for cls in vars(module).values():
            if not isinstance(cls, type) or cls.__module__ != module.__name__:
                continue
            cls_allowed = allowed.get(cls.__name__, ())
            for name, func in list(vars(cls).items()):
                # Only plain functions defined by this class; skip dunder
                # and private names (``__call__`` publishing is checked by
                # ZPublisher with default=True and stays unaffected).
                if name.startswith('_') or not inspect.isfunction(func):
                    continue
                if zpublish_marked(func):
                    # explicit source mark wins
                    continue
                zpublish(name in cls_allowed)(func)


apply()
