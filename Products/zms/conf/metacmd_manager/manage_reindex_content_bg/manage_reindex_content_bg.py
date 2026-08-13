import argparse
import logging
import requests
import threading
from dataclasses import dataclass, field
from typing import List


LOGGER = logging.getLogger("Zope")


@dataclass
class ZMINode:
    uid: str
    title: str
    meta_id: str
    is_page: bool
    is_page_element: bool
    children: List["ZMINode"] = field(default_factory=list)

    def dump(self, level=0, write_line=None):
        if write_line is None:
            write_line = print
        write_line(f"{self.title} [{self.meta_id}] (uid={self.uid})")
        for child in self.children:
            child.dump(level + 1, write_line=write_line)


class ZMIObjectTreePython:
    def __init__(self, base_url, lang="de"):
        self.base_url = base_url.rstrip("/")
        self.lang = lang
        self.params = {"preview": "preview", "lang": lang}

    def _api(self, path):
        url = f"{self.base_url}/++rest_api/{path}"
        response = requests.get(url, params=self.params)
        response.raise_for_status()
        return response.json()

    def load_tree(self):
        """
        Holt die Wurzelknoten (get_parent_nodes) und baut den kompletten Baum.
        """
        parent_nodes = self._api("get_parent_nodes")
        root_nodes = []

        for node in parent_nodes:
            root_nodes.append(self._build_node_recursive(node))

        return root_nodes

    def _build_node_recursive(self, node_data):
        """
        Baut einen ZMINode und lädt rekursiv alle Kindknoten.
        """
        # Redirect‑Nodes überspringen
        if (
            node_data.get("titlealt", "").upper().find("REDIRECT") > -1
            and node_data.get("attr_dc_identifier_url_redirect", "").strip() != ""
        ):
            return None

        node = ZMINode(
            uid=node_data["uid"],
            title=node_data.get("titlealt", ""),
            meta_id=node_data.get("meta_id", ""),
            is_page=node_data.get("is_page", False),
            is_page_element=node_data.get("is_page_element", False),
        )

        # Kindknoten laden
        child_nodes = self._api(f"{node.uid}/get_child_nodes")

        for child in child_nodes:
            child_node = self._build_node_recursive(child)
            if child_node:
                node.children.append(child_node)

        return node

    def dump_tree(self, write_line=None):
        """
        Gibt die komplette Hierarchie aus.
        """
        if write_line is None:
            write_line = print
        parent_nodes = self._api("get_parent_nodes")
        for node_data in parent_nodes:
            self._dump_node_recursive(node_data=node_data, level=0, write_line=write_line)

    def _dump_node_recursive(self, node_data, level, write_line):
        # Redirect-Nodes überspringen
        if (
            node_data.get("titlealt", "").upper().find("REDIRECT") > -1
            and node_data.get("attr_dc_identifier_url_redirect", "").strip() != ""
        ):
            return

        uid = node_data["uid"]
        title = node_data.get("titlealt", "")
        meta_id = node_data.get("meta_id", "")
        write_line(f"[{meta_id}] (uid={uid})")

        child_nodes = self._api(f"{uid}/get_child_nodes")
        for child in child_nodes:
            self._dump_node_recursive(node_data=child, level=level + 1, write_line=write_line)


def manage_reindex_content_bg( self):
    request = self.REQUEST
    base_url = self.getDocumentElement().absolute_url()
    lang = request.get("lang", "ger")

    def _worker():
        try:
            log_prefix = f"[{base_url}]"
            def _write_to_zope_log(line):
                LOGGER.info("%s %s", log_prefix, line)

            LOGGER.info("%s started", log_prefix)
            tree = ZMIObjectTreePython(base_url=base_url, lang=lang)
            tree.dump_tree(write_line=_write_to_zope_log)
            LOGGER.info("%s finished", log_prefix)
        except Exception:
            LOGGER.exception("manage_reindex_content_bg failed")

    thread = threading.Thread(target=_worker, name="manage_reindex_content_bg", daemon=True)
    thread.start()

    message = "Background Job has Started"
    target = self.url_append_params(
        "%s/manage_main" % self.absolute_url(),
        {
            "lang": lang,
            "manage_tabs_message": message,
        },
    )
    return request.response.redirect(target)

def main():
    parser = argparse.ArgumentParser(
        description="Dump ZMI object tree hierarchy via REST API"
    )
    parser.add_argument(
        "base_url",
        help="Base REST API URL, e.g. https://example.com/api/path/to/object"
    )
    parser.add_argument(
        "--lang",
        default="de",
        help="Language parameter for ZMI API (default: de)"
    )

    args = parser.parse_args()

    tree = ZMIObjectTreePython(base_url=args.base_url, lang=args.lang)
    tree.dump_tree()
	
if __name__ == "__main__":
    main()