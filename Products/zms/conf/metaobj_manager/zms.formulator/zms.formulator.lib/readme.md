zms.formulator
===============

This ZMS Content Object Definition is an Extension for the ZMS Publishing System <http://www.zms-publishing.com> 
(Open Source Content Management for Science, Technology and Medicine) to integrate the JSON Editor
<https://json-editor.github.io/json-editor/>.

A JSON Schema is generated based on special content objects and used to transform it into an HTML Form handling
all the front-end validations.

The data submitted by the generated HTML Form can be transmitted into a remote SQL Storage <http://www.sqlalchemy.org>
for further processing and evaluation using standard reporting tools - or data will be stored into the included
ZODB <http://www.zodb.org> and/or sent by mail.

Form submission provides support for the reCAPTCHA service by Google <https://www.google.com/recaptcha> to protect 
from spam and abuse.


How it works
----------
zms.formulator is an authoring tool for web forms and delivering an abstract content model for arbitrary sequences 
of form fields. After adding a ZMS-Formulator object to the ZMS content tree the form fields can be added as 
zms.formulator-items. The following item types are available and automatically generate its web form elements:
  1. string
  2. email
  3. mailattachment
  4. textarea
  5. date
  6. select
  8. multiselect
  9. checkbox
  10. integer
  11. float
  12. custom (customizable according to _JSON editor_)

To write the web form data into a SQL database a SQL schema is needed and its sqlalchemy-like DNS set as ZMS parameter.  
zms.formulator is generating a new SQL table for any content instance. The table's name is the coresponding ZMS id and 
any archived field content results in a data row abstractly representing the field model. 


Requirements
----------

  * ftfy
  * sqlalchemy


Installation
----------
  1. Import the zms.formulator content model from the the list of default models (menu; configuration / content objects)
  2. Import zms.formulator.lib/langdict.xml as language terms (menu: configuration / language)
  3. Add a new SQL schema for the incoming data, e.g. `zms_forms` with da default characterset `utf8mb4`
  4. Add a database DSN as ZMS configuration parameter `ZMSFormulator.dbconnection.password` according to sqlalchemy syntax, e.g. mysql://root:passwd@127.0.0.1:3306/zms_forms
  5. In case of using Google recaptcha add two more parameters: `Google.API.sitekey.password`, `Google.API.secretkey.password`


References
----------

  * https://pypi.python.org/pypi/ZMS
  * https://github.com/json-editor/json-editor
  * https://developers.google.com/recaptcha/intro
  * http://www.sqlalchemy.org
  * http://www.zodb.org