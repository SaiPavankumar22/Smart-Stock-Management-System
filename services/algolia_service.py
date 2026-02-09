from algoliasearch.search_client import SearchClient
from config import ALGOLIA_APP_ID, ALGOLIA_ADMIN_KEY, ALGOLIA_INDEX_NAME

class AlgoliaService:
    def __init__(self):
        self.client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_ADMIN_KEY)
        self.index = self.client.init_index(ALGOLIA_INDEX_NAME)

    def get_all_items(self, limit=5000):
        results = self.index.search("", {"hitsPerPage": limit})
        return results["hits"]

    def get_item(self, object_id):
        try:
            return self.index.get_object(object_id)
        except:
            return None

    def add_item(self, data):
        return self.index.save_object(data)

    def update_item(self, object_id, fields):
        fields["objectID"] = object_id
        return self.index.partial_update_object(fields)

    def delete_item(self, object_id):
        return self.index.delete_object(object_id)

    def bulk_update(self, items):
        return self.index.save_objects(items)
