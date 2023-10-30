# --// manage_zcatalog_lunr_build_index //--

import json
import requests
from lunr import lunr
from typing import List
from OFS.Image import manage_addFile


# Taken from https://scrapfly.io/blog/search-engine-using-web-scraping/#building-index
def build_index(docs: List[dict]):

    config = {
        "lang": ["en"],
        "min_search_length": 1,
    }

    page_dicts = {"docs": docs, "config": config}

    if bool(docs[0]):
        idx = lunr(
            ref="location",
            fields=[dict(field_name='title', boost=10), 'text'],
            documents=docs,
        )
        page_dicts["index"] = idx.serialize()
        return json.dumps(page_dicts, sort_keys=True, separators=(",", ":"), indent=2)
    else:
        return json.dumps({})


def manage_zcatalog_lunr_build_index(self):

    documents = []
    root_url = self.getHome().content.absolute_url()
    for node in requests.get('%s/++rest_api/content/get_tree_nodes'%(root_url)).json():
        documents.append({
            "location": node["index_html"].replace("./../..", root_url),
            "title": "title" in node and node["title"] or "",
            "text": "text" in node and node["text"] or (
                    "attr_dc_description" in node and node["attr_dc_description"] or ""
            )
        })

    index_file = 'search_index.json'
    index_data = build_index(documents)
    index_path = self.simplesearch

    if index_file in index_path:
        index_path.manage_delObjects(ids=[index_file])

    manage_addFile(self.simplesearch, id=index_file, title=index_file, file=index_data.encode('utf-8'), content_type='application/javascript')

    return index_data

# --// /manage_zcatalog_lunr_build_index //--