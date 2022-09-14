#!/bin/bash
# ##############
# pydoctor: https://github.com/twisted/pydoctor
# customize: https://pydoctor.readthedocs.io/en/latest/customize.html?highlight=css#tweak-html-templates
# docstring markup (epytext): http://epydoc.sourceforge.net/epytext.html
# ##############
~/vpy38/bin/pydoctor ./Products/zms/ \
	--project-name ZMS \
	--project-url https://github.com/zms-publishing/ZMS/ \
	--html-output=./Products/zms/apidocs \
	--make-html \
	--html-viewsource-base https://github.com/zms-publishing/ZMS/tree/main \
	--template-dir=./Products/zms/apidocs/theme