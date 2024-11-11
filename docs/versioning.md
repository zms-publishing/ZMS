# Workflow

## Introduction

The key tools for content quality assurance are _workflow_ and _versioning_; 
both approaches go hand in hand in content production: _workflow_ ensures that 
the right person edits or reviews content at the right time, while _versioning_ 
ensures that the history of editing steps remains transparent and traceable.
The workflow concept requires at least two versions of a document:  

1. the "working version" being edited, and
2. the published "live" version.

When a documents enters the workflow, a copy of the current live version is created 
and serves as the working version.  When the document is published, the working 
version becomes the next live version by irrevocably overwriting the previous 
live version.

## Content States
When an editor makes a content change and clicks the save button, 
the system records this change by assigning one of three basic states to the object. 
These states are 

1. STATE_NEW
2. STATE_MODIFIED
3. STATE_DELETED

There is also a possibility that no state is assigned: 

4. None (no state)

These states are fundamental and operate independently of the workflow.

## Transitions

Once a content object is assigned one of these basic states and if the workflow 
feature ist activated it triggers  a virtual transition to the workflow process, 
specifically the TR_ENTER transition, for the PAGE container of the edited content. 
This transition occurs automatically when the workflow is activated. As a result, the PAGE container, along with the 
affected content object, is assigned the initial workflow status, which is labeled 
as “Changed” (AC_CHANGED).


## Activities


## Selective workflow

# Versioning

## Introduction

Each block object (in the sense of a set of attributes) can be stored in its own version.
This attribute-container has a unique id and this id is referenced by the `ZMSCustom`-container.
An object is designed to have two versions and has attributes containing the id of the corresponding attribute-container:
* `version_live_id` for the current published live-version
* `version_work_id` for the current version in progress
## Numbering
## Versioning without workflow
## Versioning with activated workflow