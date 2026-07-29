from Products.zms import llmtools


def llmtool_regenerate_standard_html(connector, context, args):
    return llmtools.execute_llmtool('regenerate_standard_html', args or {}, context)
