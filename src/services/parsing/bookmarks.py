import json
import traceback

def extract_bookmarks(browser, files, user_profile, logger=None):
    bookmarks = []

    def parse_node(node):
        if node.get("type") == "url":
            bookmarks.append([
                node.get("name"),
                node.get("url"),
                browser,
                user_profile
            ])
        elif node.get("type") == "folder":
            for child in node.get("children", []):
                parse_node(child)

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)

            roots = data.get("roots", {})
            for root in roots.values():
                parse_node(root)

        except Exception as e:
            if logger:
                logger.error(f"Bookmark extraction failed from {file}: {e}")

    return bookmarks