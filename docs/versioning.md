# Workflow

## Introduction

The key tools for content quality assurance are _workflow_ and _versioning_; 
both approaches go hand in hand in content production: 

* **workflow** ensures that the right person edits or reviews content at the right time, while
* **versioning**  ensures that the history of editing steps remains transparent and traceable.

The workflow concept requires at least two _versions_ of a document:  

1. the _working version_ that is being edited, and
2. the _published version_ (aka "live" version).

When a document enters the workflow, a copy of the currently published document version is created and serves as the _working version_. When the document is published, the working version becomes the current _live version_ by irrevocably overwriting the former live version.

To model a workflow ZMS allows you to define state names for the content and programm the transitions between these states. The following general principles apply:

1. a workflow is the sequence of predefined state _transitions_ in a logical order - with 
the goal of document release.
2. a workflow step requires a transition from one active workflow state (activity state) of 
the content object to another.
3. starting from the basic state, the workflow always starts automatically with the `TR_ENTER` 
transition, i.e. with the transfer of the object to the active workflow-specific initial state _Changed_.
4. the workflow always ends with the `TR_LEAVE` transition to the target state `AC_COMMITTED` _Released_ 
(corresponds to the empty basic state `None`).


## Content States

### Basic States (STATE)

When an editor makes a content change and clicks the save button, the system records this change by assigning one of three basic states to the object. Moreover there is the possibility that no state is assigned. So these basic states are: 

1. `STATE_NEW`
2. `STATE_MODIFIED`
3. `STATE_DELETED`
4. `None` (if no state is assigned)


These states are fundamental and operate independently of any activated workflow. Once the workflow is activated, _transitions_ become relevant to add more, workflow specific state values to the content: if a content object is assigned one of basic states it automatically triggers a virtual transition to enter the workflow process, specifically the transition (tr) `TR_ENTER` for the PAGE container 
of the edited content object.
As a result, the PAGE container, along with the affected content object, is assigned the initial workflow status, which is labeled as _changed_ by an activity (ac) status `AC_CHANGED`.


### Activity States (AC)

Activity states are induced by specific workflow transitions; so any _activity state_ can get changed to another activity state by a _transition_ method that will exactly perform this specific action.

![Simple Workfow Model](images/admin_wf_minimal.gif)
_ZMS-GUI: Simple workflow with two major transitions: 1. requesting a commit and 2. committing_

The workflow model above start implicitly with the basic state "changed" and is left implicitly with the activity state "committed" ; the _activity states_ are:
1. Commit requested
2. Committed

To perform this two transition are needed:
1. Request commit
2. Commit

## Transitions (TR)

`TODO`

![Extended Workfow Model](images/admin_wf_extended.gif)
_ZMS-GUI: The simple workflow has got some more transitions to cover variants in the workflow and to make it more flexible _


Based on the standard workflow shown above, which in principle represents a two-stage process (plus an optional rejection), the interaction of transitions and active workflow states can be illustrated: entry into the workflow begins with the transition of the content object 
into the processing state.  After release (commit) or withdrawal (rollback), an object moves to the active statusobject has the active status `AC_COMMITTED` or `AC_ROLLEDBACK`. These are defined as exit criteria from the workflow process via the (virtual) transaction `TR_LEAVE` and thus ultimately return to a passive state.


## Selective workflow

# Versioning

## Introduction

Each block object (in the sense of a set of attributes) can be stored in its own version.
This attribute-container has a unique id and this id is referenced by the `ZMSCustom`-container.
An object is designed to have two versions and has attributes containing the id of the corresponding attribute-container:
* `version_live_id` for the current published live-version
* `version_work_id` for the current version in progress

These block objects are very atomic. A useful aggregate is a committable container-object. 
Committing a container-object should be equivalent to tagging a changeset.

TODO: tag each atomic block object or store all versions of atomic sub-objects in the container?
e.g.:

```Folder e1 {1.0.0: AAA, 2.0.0: AAA}
    Textarea e2 {1.0.0: AAA: 2.0.0: ABA}
    Textarea e3 {1.0.0: AAA: 2.0.0: AAA}

Folder e1 {1.0.0: {e1: AAA, e2: AAA, e3: AAA},
           2.0.0: {e1: AAA, e2: ABA, e3: AAA}}
    Textarea e2
    Textarea e3
```
## Numbering
## Versioning without workflow
## Versioning with activated workflow