from lunr import lunr
from bs4 import BeautifulSoup
from typing import List
from OFS.Image import manage_addFile
import json
import requests


# Taken from https://scrapfly.io/blog/search-engine-using-web-scraping/#building-index
def build_index(docs: List[dict], fields: List[dict]):

    config = {
        "lang": ["en"],
        "min_search_length": 1,
    }

    page_dicts = {"docs": docs, "config": config}

    if bool(docs[0]):
        idx = lunr(
            ref="location",
            fields=fields,
            documents=docs,
        )
        page_dicts["index"] = idx.serialize()
        return json.dumps(page_dicts, sort_keys=True, separators=(",", ":"), indent=2)
    else:
        return json.dumps({})


def manage_lunr_build_index(self):

    documents = []
    fields = []
    attr_ids = []
    root_url = self.getHome().content.absolute_url()
    adapter = self.getCatalogAdapter()
    attrs = adapter.getAttrs()

    for attr_id in adapter._getAttrIds():
        attr = attrs.get(attr_id, {})
        attr_boost = attr.get('boost')
        if attr_boost is not None:
            fields.append(dict(field_name=attr_id, boost=attr_boost))
            attr_ids.append(attr_id)

    for node in requests.get(f'{root_url}/++rest_api/content/get_tree_nodes').json():
        if node.get('meta_id') not in adapter.getIds():
            continue

        field = {"location": node["index_html"].replace("./../..", root_url),
                 "content": ""}  # TODO: remove this aggregated field as workaround for search frontend

        for attr_id in attr_ids:
            html = attr_id in node and node[attr_id] or ""
            field[attr_id] = BeautifulSoup(html).get_text()
        if "title" not in field:
            field["title"] = "titlealt" in field and field["titlealt"] or ""

        # aggregate field attributes into "content" to be processed in main.js (L43) and worker.js (L80+L123)
        # TODO: keep field attributes in python and adapt processing in javascript according to split values
        for key, val in field.items():
            if key not in ['location', 'title', 'titlealt']:
                field["content"] += val

        documents.append(field)

    index_file = 'search_index.json'
    index_data = build_index(documents, fields)
    index_path = self.lunr_page

    if index_file in index_path:
        index_path.manage_delObjects(ids=[index_file])

    manage_addFile(index_path, id=index_file, title=index_file, file=index_data.encode('utf-8'), content_type='application/javascript')

    return index_data
