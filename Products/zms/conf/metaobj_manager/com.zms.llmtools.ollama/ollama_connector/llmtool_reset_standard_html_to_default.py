from Products.zms import llmtools


def llmtool_reset_standard_html_to_default(connector, context, args):
    return llmtools.execute_llmtool('reset_standard_html_to_default', args or {}, context)
