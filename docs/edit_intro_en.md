
# <a id="editorsguide"></a>Editor's Guide: Content Production

The ZMS GUI for editors is primarily focussed on the content. To archive a design-neutral content stream the editor produces a document (aka page) as a sequence of small content-blocks. A content-block may be a text block, a link, a picture, a video or any other content class which is availabe in the right pop-up menu ("context menu").
A new content object is added by clicking on one of the listed content classes and filling the following form.


![ZMS GUI](images/edit_gui_start_en.gif)
*The ZMS editing GUI shows the reduced page preview by listing all its containing content blocks. New content blocks are added by clicking the pop-up menu on the right of the content-blocks*

## <a id="zmi"></a>The ZMS Management Interface (ZMI)

The ZMI mainly has two functional purposes: navigating and editing. For navigation there are the following elements:
1. Top Bar (meta functions)
2. Main Menu (node modalities)
3. Path Navigation (breadcrumbs)
4. Site Map (content tree)

and for editing:
1. context menu (adds content items, executes commands)
2. content class specific data entry form (content production)

## <a id="topbar"></a>Top Bar
The top bar contains some important functions that may be needed in any working context:
1. showing the authenticated user name linking to its profile data
2. the sitemap icon toggles the left handed document tree navigation
3. the configuration menu lists role specific meta functions (like switching to the conent model configuration)
4. the flag icon lists the content languages in case it's a multlingual site
5. the globe icon lists the available gui languages
6. the preview link sitches to the rendered website view (third view) of the current node
7. the live link switches to the production server (if different from preview server)


## <a id="mainmenu"></a>Main Menu
The tabbed main menu is located below the top bar and shows different modalities of the current content node:
1. Editing: the fist tab shows the sequence of the content blocks a page consists of.
2. Properties: meta attribute
3. Import/Export: exporting the current node in to different data formats or XML-based content importing into the current node
4. Link Sources: list of links targetting the current node
5. History: if versioning is activated the menu shows the changes of the current node
5. Search: full-text search through the document tree
6. Tasks: lists document nodes of a certain status (of the workflow)


## <a id="breadcrumbs"></a>Path Navigation 
The path or breadcrumb nagivation is located below the main menu and shows the depth of the position in the document tree: it os a list of parent nodes from the current node to the root node. 


## <a id="sitemap"></a>Site Map
Clicking onto the sitemap icon in the top menu generated a left handed navigation frame of the content. The sitemap can be used to browse through the document tree quickly.

![ZMS GUI](images/edit_gui_sitemap_en.gif)
*Site map navigation browsing the document tree*

## Pages: Building a Content Tree with Folders and Documents
In general ZMS differs two types of content classes: 
1. **page**-like object classes like *Folder* or *Document* working as an aggregator of the 
2. **block** elements (or *page-elements*) for containing the content itself.

The page-like objects (also known as *nodes*) can be considered as a blank sheet of paper that can be filled with the content *blocks*. The special role of the *Folder* is to structure the pages into a tree hierarchy, because a *Folder* can contain (besides content blocks) other folders or documents. In contrast a *Document* is just the end of a hierarchy (like a leaf of the document tree).

![ZMSDocument](images/edit_gui_document_de.png)
*Document: adding a new page starts with entering some bibliographic meta-data like title, navigation title (short title), description and others*

A good way to start a new websites is to build its folder structure and thus to get a first idea about the expected amount of content. This  empty tree is also helpful as a mockup  generating  the website navigation automatically.


## Blocks: Filling Pages with Content 
Page-objects like *Folder* and *Document* are sequentally filled with content blocks. Typical block elements are:
1. Textblock
2. File
3. Link
4. Image
5. Table
6. Video

![ZMSGraphic](images/edit_gui_zmsgraphic_de.png)
*Example of a content block: Image is a typical part of a document; it is placed in a sequence with other content blocks like text-blocks and tables. The Image is constructed by a set of attributes. On uploading the image data file (gif, jpg, png, svg) the editor has to provide some additional descriptive informations like a legend text, maybe an URL the image links or a second variant in an higher resolution (and bigger data size).*




