from Products.zms import llmtools


def llmtool_export_content_type_xml(connector, context, args):
    return llmtools.execute_llmtool('export_content_type_xml', args or {}, context)
