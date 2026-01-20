#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

def manage_zmsdemo_process(self, request=None):
	"""
	Container-Function for making the py-module 
	importable as a ZMS-library.
	"""
	return "This object contains two functions:\n" \
		"1. manage_zmsdemo_export: Exports the current zmsdemo site as a reimportable zexp-file.\n" \
		"2. manage_zmsdemo_refresh: Replaces the current zmsdemo site with the latest exported zexp-file.\n" \
		"Please apply functions as External Methods via Zope Management Interface.\n" \


def manage_zmsdemo_export(self, request=None):
	"""
	Export the current zmsdemo site as an reimportable zexp-file.
	"""
	context = self
	if request is None:
		request = self.REQUEST
	RESPONSE = request.RESPONSE

	if not hasattr(context, 'sites'):
		raise Exception('No sites found in context')
	if not hasattr(context.sites, 'zmsdemo'):
		raise Exception('No zmsdemo site found in context.sites')

	# Get zmsdemo site
	context.sites.manage_exportObject(id='zmsdemo', download=0, RESPONSE=RESPONSE)

	# Move to the import directory
	import_fldr = '%s/import'%(os.environ.get('INSTANCE_HOME'))
	if not os.path.exists(import_fldr):
		os.makedirs(import_fldr)
	# Move the exported file to the import directory
	exported_file = '%s/var/zmsdemo.zexp'%(os.environ.get('INSTANCE_HOME'))
	if os.path.exists(exported_file):
		os.rename(exported_file, '%s/zmsdemo.zexp'%(import_fldr))
	else:
		raise Exception('Exported file not found: %s' % exported_file)
	# Return the path to the imported file
	RESPONSE.setHeader('Content-Type', 'text/plain')
	RESPONSE.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
	RESPONSE.setHeader('Pragma', 'no-cache')
	RESPONSE.setHeader('Expires', '0')
	return 'Node zmsdemo exported to %s/zmsdemo.zexp' % import_fldr


def manage_zmsdemo_refresh(self, request=None):
	"""
	Replace the current zmsdemo site with the latest exported zexp-file.
	"""
	context = self
	if request is None:
		request = self.REQUEST
	RESPONSE = request.RESPONSE

	# Get zmsdemo site
	if not hasattr(context, 'sites'):
		context.sites = context.manage_addFolder(id='sites', title='Sites')
	if hasattr(context.sites, 'zmsdemo'):
		context.sites.manage_delObjects(ids=['zmsdemo'])

	# Import the zmsdemo site from the zexp file
	import_fldr = '%s/import'%(os.environ.get('INSTANCE_HOME'))
	if not os.path.exists(import_fldr):
		raise Exception('Import folder does not exist: %s' % import_fldr)
	zexp_file = '%s/zmsdemo.zexp'%(import_fldr)
	if not os.path.exists(zexp_file):
		raise Exception('Zexp file not found: %s' % zexp_file)

	# Import the zexp file
	context.sites.manage_importObject(
		file='zmsdemo.zexp',
		set_owner=False,
		suppress_events=True
	)
	# Check if the import was successful
	if not hasattr(context.sites, 'zmsdemo'):
		raise Exception('Import of zmsdemo site failed.')

	# Refresh the zmsindex
	zmsindex = context.sites.zmsdemo.content.getZMSIndex()
	zmsindex.manage_reindex(regenerate_all=True)

	# Return success message
	RESPONSE.setHeader('Content-Type', 'text/plain')
	RESPONSE.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate')
	RESPONSE.setHeader('Pragma', 'no-cache')
	RESPONSE.setHeader('Expires', '0')
	return 'Node zmsdemo refreshed successfully.'