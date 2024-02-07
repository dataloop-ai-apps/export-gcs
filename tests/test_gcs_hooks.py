import os
import unittest
import dtlpy as dl

from modules.gcs_hooks import HookIntegrationGCS


class Node:
    def __init__(self, metadata):
        self.metadata = metadata


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.runner = HookIntegrationGCS(integration_name='')
        self.original_item = dl.items.get(item_id='658ae4cd160fb30cdebf1156')
        self.original_annotations = self.original_item.annotations.list()
        remote_filepath = "/clones/1.jpg"
        try:
            item = self.original_item.dataset.items.get(filepath=remote_filepath)
            item.delete()
        except dl.exceptions.NotFound:
            pass

        self.item = self.original_item.clone(remote_filepath=remote_filepath)
        self.context = dl.Context()
        self.context._node = Node(metadata={'customNodeConfig': {'bucket_name': 'micha-storage'}})

    def test_export_annotations(self):
        self.runner.export_annotation(item=self.item, context=self.context)

    def test_import_annotations(self):
        self.item.annotations.delete(filters=dl.Filters(resource=dl.FiltersResource.ANNOTATION))
        self.runner.import_annotation(item=self.item, context=self.context)
        assert len(self.item.annotations.list()) == len(self.original_annotations)


if __name__ == "__main__":
    unittest.main()
