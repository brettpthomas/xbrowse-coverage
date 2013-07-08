import unittest
import pymongo
import os

from xcoverage import CoverageDatastore

class TestCoverageRegionOverlap(unittest.TestCase):

    def runTest(self):
        db = pymongo.Connection().test_coverage_datastore
        coverage_store = CoverageDatastore(db)

        coverage_file_path = os.path.dirname(os.path.abspath(__file__)) + '/example_coverage_file.bed'
        coverage_store.add_individual('proj1', 'indiv1', open(coverage_file_path))

        first_400 = coverage_store.get_coverage_totals_in_region('proj1', 'indiv1', 1e9+1, 1e9+30400)
        self.assertEqual(first_400['poor_mapping'], 45)

        first_600 = coverage_store.get_coverage_totals_in_region('proj1', 'indiv1', 1e9+1, 1e9+30600)
        self.assertEqual(first_600['poor_mapping'], 158)

        #print coverage_store.get_coverage_totals_in_region('proj1', 'indiv1', 1e9+800000, 1e9+880000)

if __name__ == '__main__':
    unittest.main()