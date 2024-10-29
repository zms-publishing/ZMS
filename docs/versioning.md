# Workflow
## Introduction
## Activities
## States
## Transitions
## Selective workflow

# Versioning
## Introduction
Each atomic object (in the sense of a set of attributes) can be stored in its own version.
This attribute-container has a unique id and this id is referenced by the `ZMSCustom`-container.
An object is designed to have two versions and has attributes containing the id of the corresponding attribute-container:
* `version_live_id` for the current published live-version
* `version_work_id` for the current version in progress, 
## Numbering
## Versioning without workflow
## Versioning with activated workflow