import unittest

from xcoverage.utils import get_interval_overlap, flatten_region_list

class CoverageRegionOverlap(unittest.TestCase):
    def setUp(self):
        self.region = {
            'xstart': 1e9+100,
            'xend': 1e9+200,
            'coverage': 'callable'
        }
    def test_before_start(self):
        self.assertEqual(get_interval_overlap(1e9+1, 1e9+2, self.region), 0)

    def test_onebase_at_start(self):
        self.assertEqual(get_interval_overlap(1e9+1, 1e9+100, self.region), 1)

    def test_totally_within(self):
        self.assertEqual(get_interval_overlap(1e9+150, 1e9+160, self.region), 11)

    def test_overlap_start(self):
        self.assertEqual(get_interval_overlap(1e9+50, 1e9+160, self.region), 61)

    def test_overlap_end(self):
        self.assertEqual(get_interval_overlap(1e9+150, 1e9+250, self.region), 51)

    def test_after_end(self):
        self.assertEqual(get_interval_overlap(1e9+250, 1e9+260, self.region), 0)

    def test_subsume(self):
        self.assertEqual(get_interval_overlap(1e9+50, 1e9+260, self.region), 101)

# TODO
class CoverageTotals(unittest.TestCase):
    def setUp(self):
        pass


class FlattenRegionLists(unittest.TestCase):

    def test_no_overlap(self):
        regions = [
            (1e9, 1e9+10),
            (1e9+20, 1e9+30)
        ]
        flattened = flatten_region_list(regions)
        self.assertEqual(flattened, regions)

    def test_one_overlap(self):
        regions = [
            (1e9, 1e9+10),
            (1e9+20, 1e9+30),
            (1e9+25, 1e9+35)
        ]
        flattened = flatten_region_list(regions)
        self.assertEqual(flattened[1], (1e9+20, 1e9+35))

    def test_nested_overlaps(self):
        regions = [
            (1e9, 1e9+10),
            (1e9+3, 1e9+5),
            (1e9+5, 1e9+20)
        ]
        flattened = flatten_region_list(regions)
        self.assertEqual(flattened, [(1e9, 1e9+20)])

if __name__ == '__main__':
    unittest.main()