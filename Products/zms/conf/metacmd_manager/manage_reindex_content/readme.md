# Selective Reindexing of the Current Content-Context

## Purpose

`manage_reindex_content` helps editors/admins refresh the external content index
(for example OpenSearch) for selected content nodes in the current context tree.

Use it when search results are outdated, missing, or inconsistent after content
changes.


## How It Works

1. The sitemap starts at the current context node.
2. You select the nodes to process via checkboxes.
3. Only checked nodes are reindexed.
4. Each checked node is processed exactly once.
5. Unchecked nodes are excluded.

The tool sends one reindex request per selected node to the active catalog
connector (`reindex_page` with `page_size=1`).

Hint: If no catalog connector is available, the command will stop with a warning.

## Usage

1. Open `manage_reindex_content` on the context you want to work on.
2. Expand the tree and check the nodes you want to reindex.
3. Click Start.
4. Monitor progress per node in the tree row.


