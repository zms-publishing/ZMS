FS30 ��d0b�      np               ��d0b�                        ��cpersistent.mapping
PersistentMapping
q .�}qX   dataq}qX   ApplicationqC       qcOFS.Application
Application
q�qQss.        ��d0b�                        ��cOFS.userfolder
UserFolder
q .�}q(X   dataqC       qcPersistence.mapping
PersistentMapping
q�qQX   _ofs_migratedq�u.      n ��d`if      �p     Added browser_id_manager        ��d`if              z        ��cProducts.Sessions.BrowserIdManager
BrowserIdManager
q .�}q(X   idqX   browser_id_managerqX   titleqX   Browser Id ManagerqX   browserid_nameqX   _ZopeIdqX   browserid_namespacesqX   cookiesq	X   formq
�qX   cookie_pathqX   /qX   cookie_domainqX    qX   cookie_life_daysqK X   cookie_secureq�X   cookie_http_onlyq�X   auto_url_encodingq�X   cookie_same_siteqX   Laxqu.      � ��de8�      Bp     Added session_data_manager        ��de8�              s         ��cProducts.Sessions.SessionDataManager
SessionDataManagerTraverser
q .�}q(X   _requestSessionNameqX   SESSIONqX   _sessionDataManagerqX   session_data_managerqu.        ��de8�              s        �cProducts.Sessions.SessionDataManager
SessionDataManager
q .�}q(X   idqX   session_data_managerqX   obpathq]q(X    qX   temp_folderqX   session_dataqeX   titleq	X   Session Data Managerq
X   _requestSessionNameqX   SESSIONqX   _hasTraversalHookqKu.      B ��djB�       �p   "  Added site error_log at /error_log        ��djB�              �         <�cProducts.SiteErrorLog.SiteErrorLog
SiteErrorLog
q .�}q.       � ��dz�       �p     Added virtual_hosting       	 ��dz�              d         f�cProducts.SiteAccess.VirtualHostMonster
VirtualHostMonster
q .�}qX   idqX   virtual_hostingqs.       � ��e��      p   "  Added default view for root object       
 ��e��              (        ��cProducts.PageTemplates.ZopePageTemplate
ZopePageTemplate
q .�}q(X   idqX
   index_htmlqX   expandqK X   _bind_namesqcShared.DC.Scripts.Bindings
NameAssignments
q)�q}qX   _asgnsq	}q
X   name_subpathqX   traverse_subpathqssbX   output_encodingqX   utf-8qX   content_typeqX	   text/htmlqX   _textqX5  <!DOCTYPE html>
<html>
  <head>
    <title tal:content="template/title">The title</title>
    <meta charset="utf-8" />
    <meta name="viewport"
          content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <link rel="shortcut icon" type="image/x-icon"
          href="/++resource++logo/favicon/favicon.svg" />
    <link rel="stylesheet" type="text/css"
          href="/++resource++logo/default.css" />
  </head>
  <body>
    <a href="https://www.zope.dev" target="_blank">
      <img src="/++resource++logo/Zope.svg" id="logo" alt="Zope logo" />
    </a>
    <h1>
      <span tal:condition="template/title" tal:replace="context/title_or_id">
        content title or id
      </span>:
      <span tal:condition="template/title" tal:replace="template/title">
        optional template title
      </span>
    </h1>
    <p>
      This is Page Template <em tal:content="template/id">template id</em>.
    </p>
    <p>
      For documentation, please visit
      <a href="https://zope.readthedocs.io">https://zope.readthedocs.io</a>.
    </p>
  </body>
</html>qX   titleqX   Auto-generated default pagequ.       �(b_�      �p     Created initial user        �(b_�              B         z�cPersistence.mapping
PersistentMapping
q .�}qX   dataq}qX   adminqC       qcAccessControl.users
User
q�qQss.        �(b_�              B         ��cAccessControl.users
User
q .�}q(X   nameqX   adminqX   __qCH{SHA256}8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918qX   rolesqX   Managerq�qX   domainsq	]q
u.      � �(c]��      �p   &  Removed unused application attributes.        �(c]��                       �cOFS.Folder
Folder
q .�}q(X   idqX   temp_folderqX   _objectsq}q(hX   session_dataqX	   meta_typeqX   Transient Object Containerqu�q	hC       q
cProducts.Transience.Transience
TransientObjectContainer
q�qQu.        �(c]��                      B�cProducts.Transience.Transience
TransientObjectContainer
q .�}q(X   idqX   session_dataqX   titleqX   Session Data ContainerqX   _timeout_secsqM�X   _periodqKX   _timeout_slicesqK<X   _limitq	K X   _delCallbackq
NX   _addCallbackqNX   _dataqC       qcBTrees.IOBTree
IOBTree
q�qQX   _max_timesliceqC       qcProducts.Transience.Transience
Increaser
q�qQX   _last_finalized_timesliceqC       qh�qQX   _last_gc_timesliceqC       qh�qQX   _lengthqC       qcProducts.Transience.Transience
Length2
q�qQX   getLenqhh�qQu.        �(c]��                       7�cProducts.Transience.Transience
Increaser
q .�J����.        �(c]��                       7�cProducts.Transience.Transience
Increaser
q .�J8="h.       5 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       4 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       3 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       2 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       1 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       0 �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       / �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       . �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       - �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       , �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       + �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       * �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       ) �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       ( �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       ' �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       & �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       % �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       $ �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       # �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       " �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.       ! �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.         �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.        �(c]��                       !�cBTrees.OOBTree
OOBTree
q .�N.      � �(��3      �p     admin/manage_addZMS        �(��3              �         7�cProducts.Transience.Transience
Increaser
q .�JD6"h.        �(��3              �         a�cProducts.Transience.Transience
Length2
q .�}q(X   valueqKX   floorqK X   ceilingqKu.       �(��3              �        ��cProducts.Transience.TransientObject
TransientObject
q .�}q(X   tokenqX   81755200BAC2KPVBepkqX   idqX   17470738176625247322304329675qX
   _containerq}q(X   filterattr0_e85qX    q	X   filterop0_e85q
h	X   filtervalue0_e85qh	X   filterattr1_e85qh	X   filterop1_e85qh	X   filtervalue1_e85qh	X   filterattr2_e85qh	X   filterop2_e85qh	X   filtervalue2_e85qh	X   filterattr3_e85qh	X   filterop3_e85qh	X   filtervalue3_e85qh	X   filterattr4_e85qh	X   filterop4_e85qh	X   filtervalue4_e85qh	X   filterattr5_e85qh	X   filterop5_e85qh	X   filtervalue5_e85qh	X   filterattr6_e85qh	X   filterop6_e85qh	X   filtervalue6_e85qh	X   filterattr7_e85qh	X   filterop7_e85qh	X   filtervalue7_e85q h	X   filterattr8_e85q!h	X   filterop8_e85q"h	X   filtervalue8_e85q#h	X   filterattr9_e85q$h	X   filterop9_e85q%h	X   filtervalue9_e85q&h	X   filterattr10_e85q'h	X   filterop10_e85q(h	X   filtervalue10_e85q)h	X   filterattr11_e85q*h	X   filterop11_e85q+h	X   filtervalue11_e85q,h	X   filterattr12_e85q-h	X   filterop12_e85q.h	X   filtervalue12_e85q/h	X   filterattr13_e85q0h	X   filterop13_e85q1h	X   filtervalue13_e85q2h	X   filterattr14_e85q3h	X   filterop14_e85q4h	X   filtervalue14_e85q5h	X   filterattr15_e85q6h	X   filterop15_e85q7h	X   filtervalue15_e85q8h	X   filterattr16_e85q9h	X   filterop16_e85q:h	X   filtervalue16_e85q;h	X   filterattr17_e85q<h	X   filterop17_e85q=h	X   filtervalue17_e85q>h	X   filterattr18_e85q?h	X   filterop18_e85q@h	X   filtervalue18_e85qAh	X   filterattr19_e85qBh	X   filterop19_e85qCh	X   filtervalue19_e85qDh	X   filterattr20_e85qEh	X   filterop20_e85qFh	X   filtervalue20_e85qGh	X   filterattr21_e85qHh	X   filterop21_e85qIh	X   filtervalue21_e85qJh	X   filterattr22_e85qKh	X   filterop22_e85qLh	X   filtervalue22_e85qMh	X   filterattr23_e85qNh	X   filterop23_e85qOh	X   filtervalue23_e85qPh	X   filterattr24_e85qQh	X   filterop24_e85qRh	X   filtervalue24_e85qSh	X   filterattr25_e85qTh	X   filterop25_e85qUh	X   filtervalue25_e85qVh	X   filterattr26_e85qWh	X   filterop26_e85qXh	X   filtervalue26_e85qYh	X   filterattr27_e85qZh	X   filterop27_e85q[h	X   filtervalue27_e85q\h	X   filterattr28_e85q]h	X   filterop28_e85q^h	X   filtervalue28_e85q_h	X   filterattr29_e85q`h	X   filterop29_e85qah	X   filtervalue29_e85qbh	X   filterattr30_e85qch	X   filterop30_e85qdh	X   filtervalue30_e85qeh	X   filterattr31_e85qfh	X   filterop31_e85qgh	X   filtervalue31_e85qhh	X   filterattr32_e85qih	X   filterop32_e85qjh	X   filtervalue32_e85qkh	X   filterattr33_e85qlh	X   filterop33_e85qmh	X   filtervalue33_e85qnh	X   filterattr34_e85qoh	X   filterop34_e85qph	X   filtervalue34_e85qqh	X   filterattr35_e85qrh	X   filterop35_e85qsh	X   filtervalue35_e85qth	X   filterattr36_e85quh	X   filterop36_e85qvh	X   filtervalue36_e85qwh	X   filterattr37_e85qxh	X   filterop37_e85qyh	X   filtervalue37_e85qzh	X   filterattr38_e85q{h	X   filterop38_e85q|h	X   filtervalue38_e85q}h	X   filterattr39_e85q~h	X   filterop39_e85qh	X   filtervalue39_e85q�h	X   filterattr40_e85q�h	X   filterop40_e85q�h	X   filtervalue40_e85q�h	X   filterattr41_e85q�h	X   filterop41_e85q�h	X   filtervalue41_e85q�h	X   filterattr42_e85q�h	X   filterop42_e85q�h	X   filtervalue42_e85q�h	X   filterattr43_e85q�h	X   filterop43_e85q�h	X   filtervalue43_e85q�h	X   filterattr44_e85q�h	X   filterop44_e85q�h	X   filtervalue44_e85q�h	X   filterattr45_e85q�h	X   filterop45_e85q�h	X   filtervalue45_e85q�h	X   filterattr46_e85q�h	X   filterop46_e85q�h	X   filtervalue46_e85q�h	X   filterattr47_e85q�h	X   filterop47_e85q�h	X   filtervalue47_e85q�h	X   filterattr48_e85q�h	X   filterop48_e85q�h	X   filtervalue48_e85q�h	X   filterattr49_e85q�h	X   filterop49_e85q�h	X   filtervalue49_e85q�h	X   filterattr50_e85q�h	X   filterop50_e85q�h	X   filtervalue50_e85q�h	X   filterattr51_e85q�h	X   filterop51_e85q�h	X   filtervalue51_e85q�h	X   filterattr52_e85q�h	X   filterop52_e85q�h	X   filtervalue52_e85q�h	X   filterattr53_e85q�h	X   filterop53_e85q�h	X   filtervalue53_e85q�h	X   filterattr54_e85q�h	X   filterop54_e85q�h	X   filtervalue54_e85q�h	X   filterattr55_e85q�h	X   filterop55_e85q�h	X   filtervalue55_e85q�h	X   filterattr56_e85q�h	X   filterop56_e85q�h	X   filtervalue56_e85q�h	X   filterattr57_e85q�h	X   filterop57_e85q�h	X   filtervalue57_e85q�h	X   filterattr58_e85q�h	X   filterop58_e85q�h	X   filtervalue58_e85q�h	X   filterattr59_e85q�h	X   filterop59_e85q�h	X   filtervalue59_e85q�h	X   filterattr60_e85q�h	X   filterop60_e85q�h	X   filtervalue60_e85q�h	X   filterattr61_e85q�h	X   filterop61_e85q�h	X   filtervalue61_e85q�h	X   filterattr62_e85q�h	X   filterop62_e85q�h	X   filtervalue62_e85q�h	X   filterattr63_e85q�h	X   filterop63_e85q�h	X   filtervalue63_e85q�h	X   filterattr64_e85q�h	X   filterop64_e85q�h	X   filtervalue64_e85q�h	X   filterattr65_e85q�h	X   filterop65_e85q�h	X   filtervalue65_e85q�h	X   filterattr66_e85q�h	X   filterop66_e85q�h	X   filtervalue66_e85q�h	X   filterattr67_e85q�h	X   filterop67_e85q�h	X   filtervalue67_e85q�h	X   filterattr68_e85q�h	X   filterop68_e85q�h	X   filtervalue68_e85q�h	X   filterattr69_e85q�h	X   filterop69_e85q�h	X   filtervalue69_e85q�h	X   filterattr70_e85q�h	X   filterop70_e85q�h	X   filtervalue70_e85q�h	X   filterattr71_e85q�h	X   filterop71_e85q�h	X   filtervalue71_e85q�h	X   filterattr72_e85q�h	X   filterop72_e85q�h	X   filtervalue72_e85q�h	X   filterattr73_e85q�h	X   filterop73_e85q�h	X   filtervalue73_e85q�h	X   filterattr74_e85q�h	X   filterop74_e85q�h	X   filtervalue74_e85q�h	X   filterattr75_e85q�h	X   filterop75_e85q�h	X   filtervalue75_e85q�h	X   filterattr76_e85q�h	X   filterop76_e85q�h	X   filtervalue76_e85q�h	X   filterattr77_e85q�h	X   filterop77_e85q�h	X   filtervalue77_e85q�h	X   filterattr78_e85q�h	X   filterop78_e85q�h	X   filtervalue78_e85q�h	X   filterattr79_e85q�h	X   filterop79_e85q�h	X   filtervalue79_e85q�h	X   filterattr80_e85q�h	X   filterop80_e85q�h	X   filtervalue80_e85q�h	X   filterattr81_e85q�h	X   filterop81_e85q�h	X   filtervalue81_e85q�h	X   filterattr82_e85q�h	X   filterop82_e85r   h	X   filtervalue82_e85r  h	X   filterattr83_e85r  h	X   filterop83_e85r  h	X   filtervalue83_e85r  h	X   filterattr84_e85r  h	X   filterop84_e85r  h	X   filtervalue84_e85r  h	X   filterattr85_e85r  h	X   filterop85_e85r	  h	X   filtervalue85_e85r
  h	X   filterattr86_e85r  h	X   filterop86_e85r  h	X   filtervalue86_e85r  h	X   filterattr87_e85r  h	X   filterop87_e85r  h	X   filtervalue87_e85r  h	X   filterattr88_e85r  h	X   filterop88_e85r  h	X   filtervalue88_e85r  h	X   filterattr89_e85r  h	X   filterop89_e85r  h	X   filtervalue89_e85r  h	X   filterattr90_e85r  h	X   filterop90_e85r  h	X   filtervalue90_e85r  h	X   filterattr91_e85r  h	X   filterop91_e85r  h	X   filtervalue91_e85r  h	X   filterattr92_e85r  h	X   filterop92_e85r  h	X   filtervalue92_e85r  h	X   filterattr93_e85r   h	X   filterop93_e85r!  h	X   filtervalue93_e85r"  h	X   filterattr94_e85r#  h	X   filterop94_e85r$  h	X   filtervalue94_e85r%  h	X   filterattr95_e85r&  h	X   filterop95_e85r'  h	X   filtervalue95_e85r(  h	X   filterattr96_e85r)  h	X   filterop96_e85r*  h	X   filtervalue96_e85r+  h	X   filterattr97_e85r,  h	X   filterop97_e85r-  h	X   filtervalue97_e85r.  h	X   filterattr98_e85r/  h	X   filterop98_e85r0  h	X   filtervalue98_e85r1  h	X   filterattr99_e85r2  h	X   filterop99_e85r3  h	X   filtervalue99_e85r4  h	X   qfilters_e85r5  KX   manage_langr6  X   gerr7  uX   _createdr8  GA���^��X   _last_accessedr9  GA���^��X   _last_modifiedr:  GA��Ǝ��u.      � �)C�"      ep  %   admin/myzmsx/content/manage_ajaxZMIActions        �)C�"              ;�         ��cBTrees.OOBTree
OOBTree
q .�X   81755200BAC2KPVBepkqC      qcProducts.Transience.TransientObject
TransientObject
q�qQ�q�q�q�q.        �)C�"              ;�        ��cBTrees.IOBTree
IOBTree
q .�(J�:"hC       qcBTrees.OOBTree
OOBTree
q�qQJ;"hC       qh�qQJ;"hC       qh�qQJ0;"hC       qh�q	QJD;"hC       q
h�qQJX;"hC       qh�qQJl;"hC       qh�qQJ�;"hC       qh�qQJ�;"hC        qh�qQJ�;"hC       !qh�qQJ�;"hC       "qh�qQJ�;"hC       #qh�qQJ�;"hC       $qh�qQJ�;"hC       %qh�qQJ<"hC       &qh�qQJ <"hC       'q h�q!QJ4<"hC       (q"h�q#QJH<"hC       )q$h�q%QJ\<"hC       *q&h�q'QJp<"hC       +q(h�q)QJ�<"hC       ,q*h�q+QJ�<"hC       -q,h�q-QJ�<"hC       .q.h�q/QJ�<"hC       /q0h�q1QJ�<"hC       0q2h�q3QJ�<"hC       1q4h�q5QJ�<"hC       2q6h�q7QJ="hC       3q8h�q9QJ$="hC       4q:h�q;QJ8="hC       5q<h�q=Qtq>�q?�q@�qA.        �)C�"              ;�         !�cBTrees.OOBTree
OOBTree
q .�N.      e �)2g��      >p     admin/manage_delObjects        �)2g��              @         �cOFS.Application
Application
q .�}q(X   __allow_groups__qC       qcOFS.userfolder
UserFolder
q�qQX   _objectsq(}q(X   idqX	   acl_usersq	X	   meta_typeq
X   User Folderqu}q(hX   browser_id_managerqh
X   Browser Id Managerqu}q(hX   session_data_managerqh
X   Session Data Managerqu}q(hX	   error_logqh
X   Site Error Logqu}q(hX   virtual_hostingqh
X   Virtual Host Monsterqu}q(hX
   index_htmlqh
X   Page Templatequ}q(X   idqX   temp_folderqX	   meta_typeqX   Folderqutq X	   acl_usersq!hh�q"QX   browser_id_managerq#C       q$cProducts.Sessions.BrowserIdManager
BrowserIdManager
q%�q&QX   session_data_managerq'C       q(cProducts.Sessions.SessionDataManager
SessionDataManager
q)�q*QX   __before_traverse__q+}q,(K2X   SessionDataManagerq-�q.C       q/cProducts.Sessions.SessionDataManager
SessionDataManagerTraverser
q0�q1QKh�q2cZPublisher.BeforeTraverse
NameCaller
q3)�q4}q5X   nameq6hsbuX   __before_publishing_traverse__q7cZPublisher.BeforeTraverse
MultiHook
q8)�q9}q:(X	   _hooknameq;X   __before_publishing_traverse__q<X   _priorq=NX   _defined_in_classq>�X   _listq?]q@(h4h/h0�qAQeubX	   error_logqBC       qCcProducts.SiteErrorLog.SiteErrorLog
SiteErrorLog
qD�qEQX   __error_log__qFhChD�qGQX   virtual_hostingqHC       	qIcProducts.SiteAccess.VirtualHostMonster
VirtualHostMonster
qJ�qKQX
   index_htmlqLC       
qMcProducts.PageTemplates.ZopePageTemplate
ZopePageTemplate
qN�qOQhC       qPcOFS.Folder
Folder
qQ�qRQu.      > �2���      �      Created initial user        �2���      m      Ff         z�cPersistence.mapping
PersistentMapping
q .�}qX   dataq}qX   adminqC      qcAccessControl.users
User
q�qQss.       �2���              Ff         ��cAccessControl.users
User
q .�}q(X   nameqX   adminqX   __qCH{SHA256}8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918qX   rolesqX   Managerq�qX   domainsq	]q
u.      �