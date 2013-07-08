from xbrowse import genomeloc

import utils
import pymongo
from operator import add
from collections import Counter


COVERAGE_FILE_TAGS = [

]

COVERAGE_OPTIONS = [
    'callable',
    'low_coverage',
    'poor_mapping',
]

COVERAGE_TAG_MAP = {
    'CALLABLE': 'callable',
    'LOW_COVERAGE': 'low_coverage',
    'NO_COVERAGE': 'low_coverage',
    'POOR_MAPPING_QUALITY': 'poor_mapping',
    'REF_N': 'poor_mapping',
}

class CoverageDatastore(object):
    """
    This is the main class
    """

    def __init__(self, db):
        """
        Takes a pymongo Database to start
        Should be empty - unsure what collections will be used
        """
        self._db = db

    def add_individual(self, project_id, indiv_id, coverage_file):
        """
        Adds an individual with data from coverage_file
        Will overwrite any data already in there for (project_id, indiv_id)

        coverage_file is file-like object
        Note that raw coverage files usually gzipped
        """
        self._db.regions.remove({ 'project_id': project_id, 'indiv_id': indiv_id })

        # where put this?
        self._db.regions.ensure_index([('xpos', pymongo.GEO2D),], min=0, max=1e11)
        self._db.regions.ensure_index([('project_id', 1), ('indiv_id', 1), ('xstart', 1), ('xstop', 1)])
        # db.regions.find({'xpos': {"$within" : {"$box" : [[0,1e9], [1e9+1e7,1e11]] }}})

        for line in coverage_file:
            fields = line.strip().split('\t')
            chr = 'chr' + fields[0]
            start = int(fields[1])
            end = int(fields[2])
            xstart = genomeloc.get_single_location(chr, start)
            xend = genomeloc.get_single_location(chr, end)
            coverage = COVERAGE_TAG_MAP[fields[3]]

            self._db.regions.insert({
                'project_id': project_id,
                'indiv_id': indiv_id,
                'xstart': xstart,
                'xend': xend,
                'xpos': {'xstart': xstart, 'xend': xend}, # for geospatial indexing
                'coverage': coverage,
            })

    def get_coverage_at_position(self, project_id, indiv_id, xpos):
        regions = list(self._db.regions.find({
            'project_id': project_id,
            'indiv_id': indiv_id,
            'xstart': {'$lte': xpos},
            'xend': {'$gte': xpos},
        }))
        if len(regions) == 0:
            return 'low_coverage'
        else:
            # TODO: will we ever have overlapping coverages?
            return COVERAGE_OPTIONS[regions[0]['coverage']]

    def get_coverage_totals_in_region(self, project_id, indiv_id, xstart, xend):
        """
        Map of { coverage_type -> total_bases } for this indiv
        """
        intervals = list(self._db.regions.find({
            'project_id': project_id,
            'indiv_id': indiv_id,
            'xpos': {'$within': {'$box': [ [0, xstart], [xend, 1e11]] } },
        }))
        return utils.get_coverage_totals_in_region_for_interval_set(xstart, xend, intervals)

    def get_coverage_totals_in_region_set(self, project_id, indiv_id, region_list):
        """
        Coverage summed across a set of regions (ie. a gene)
        region_list is a list of (xstart, xend) tuples
        Regions must be sorted, but they can overlap
        """

        # TODO: check that regions are actually sorted

        flattened_regions = utils.flatten_region_list(region_list)

        list_of_totals = [self.get_coverage_totals_in_region(project_id, indiv_id, region[0], region[1]) for region in flattened_regions]
        return reduce(add, (Counter(dict(x)) for x in list_of_totals))
