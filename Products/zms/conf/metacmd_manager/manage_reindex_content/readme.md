# Selective Reindexing of the Current Content-Context

## Purpose

manage_reindex_content refreshes the external content index (for example OpenSearch)
for selected nodes in the current content context.

Use it when indexed content is outdated, missing, or inconsistent after edits.

## Role-Based Variants

### Recursive Variant (Manager, ZMSAdministrator)

- Full object-tree UI is available.
- Recursive navigation/selection is possible.
- Intended for broader maintenance and bulk reindexing.

### Current-Level Variant (ZMSEditor)

- Scope is limited to the current node and its direct ZMSFile children.
- Subdocuments, folders, and any other child types are not shown.
- Deeper descendants are not available for selection.

## Processing Model

1. The sitemap starts from the current context node.
2. You select nodes via checkboxes within the visible role-specific scope.
3. Only checked nodes are reindexed.
4. Each selected node is processed once.
5. Unchecked nodes are excluded.

The tool sends one reindex request per selected node to the active catalog
connector (reindex_page with page_size=1).

If no catalog connector is available, execution stops with a warning.

## Usage

1. Open manage_reindex_content on the context you want to reindex.
2. Select the nodes shown by your role-specific variant.
3. Click Start.
4. Monitor progress per node in the tree row.


