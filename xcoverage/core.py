import constants
import bed_files

from xbrowse import genomeloc

import utils
import pymongo
from operator import add
from collections import Counter


class CoverageDatastore(object):
    """
    This is the main class
    """

    def __init__(self, db, reference):
        """
        Takes a pymongo Database to start
        Should be empty - unsure what collections will be used
        """
        self._db = db
        self._reference = reference
        self._exons = reference.get_ordered_exons()


    def add_individual(self, sample_id, coverage_file):
        """
        Adds an individual with data from coverage_file
        Will overwrite any data already in there for (project_id, indiv_id)

        coverage_file is file-like object
        Note that raw coverage files usually gzipped
        """
        print "Adding coverage for %s" % sample_id
        self._db.exons.remove({'sample_id': sample_id})

        for coverage in utils.iterate_exon_totals(coverage_file, iter(self._exons)):
            doc = coverage
            doc['sample_id'] = sample_id
            self._db.exons.insert(doc)

        # self._db.regions.remove({ 'project_id': project_id, 'indiv_id': indiv_id })
        #
        # # where put this?
        # self._db.regions.ensure_index([('xpos', pymongo.GEO2D),], min=0, max=1e11)
        # self._db.regions.ensure_index([('project_id', 1), ('indiv_id', 1), ('xstart', 1), ('xstop', 1)])
        #
        # self._db.exons.ensure_index([('project_id', 1), ('indiv_id', 1), ('transcript_id', 1), ('xstop', 1)])
        #
        # # db.regions.find({'xpos': {"$within" : {"$box" : [[0,1e9], [1e9+1e7,1e11]] }}})
        #
        # for line in coverage_file:
        #     fields = line.strip().split('\t')
        #     chr = 'chr' + fields[0]
        #     start = int(fields[1])
        #     end = int(fields[2])
        #     xstart = genomeloc.get_single_location(chr, start)
        #     xend = genomeloc.get_single_location(chr, end)
        #     coverage = constants.COVERAGE_TAG_MAP[fields[3]]
        #
        #     self._db.regions.insert({
        #         'project_id': project_id,
        #         'indiv_id': indiv_id,
        #         'xstart': xstart,
        #         'xend': xend,
        #         'xpos': {'xstart': xstart, 'xend': xend}, # for geospatial indexing
        #         'coverage': coverage,
        #     })


    def get_coverage_at_position(self, sample_id, xpos):
        raise NotImplementedError
        # regions = list(self._db.regions.find({
        #     'project_id': project_id,
        #     'indiv_id': indiv_id,
        #     'xstart': {'$lte': xpos},
        #     'xend': {'$gte': xpos},
        # }))
        # if len(regions) == 0:
        #     return 'low_coverage'
        # else:
        #     # TODO: will we ever have overlapping coverages?
        #     return constants.COVERAGE_OPTIONS[regions[0]['coverage']]

    def get_coverage_totals_in_region(self, sample_id, xstart, xend):
        """
        Map of { coverage_type -> total_bases } for this indiv
        """
        raise NotImplementedError
        # intervals = list(self._db.regions.find({
        #     'project_id': project_id,
        #     'indiv_id': indiv_id,
        #     'xpos': {'$within': {'$box': [ [0, xstart], [xend, 1e11]] } },
        # }))
        # return utils.get_coverage_totals_in_region_for_interval_set(xstart, xend, intervals)

    def get_coverage_totals_in_region_set(self, sample_id, region_list):
        """
        Coverage summed across a set of regions (ie. a gene)
        region_list is a list of (xstart, xend) tuples
        Regions must be sorted, but they can overlap
        """
        raise NotImplementedError
        # # TODO: check that regions are actually sorted
        #
        # flattened_regions = utils.flatten_region_list(region_list)
        #
        # list_of_totals = [self.get_coverage_totals_in_region(project_id, indiv_id, region[0], region[1]) for region in flattened_regions]
        # counter = reduce(add, (Counter(dict(x)) for x in list_of_totals))
        # return dict(counter)

    def get_coverage_for_exon(self, sample_id, exon_id):
        """
        Cumulative coverages for this exon
        """
        doc = self._db.exons.find_one({'sample_id': sample_id, 'exon_id': exon_id})
        if doc is None:
            raise Exception("No data for sample %s at %s" % (sample_id, exon_id))
        return {
            'callable': doc['callable'],
            'low_coverage': doc['low_coverage'],
            'poor_mapping': doc['poor_mapping']
        }

    def get_coverages_for_exons(self, sample_id, exon_id_list):
        """
        Map of exon_id -> coverages for each exon
        """
        docs = self._db.exons.find({'sample_id': sample_id, 'exon_id': {'$in': exon_id_list}})
        docs_by_exon = {doc['exon_id']: doc for doc in docs}
        coverages = {}
        for exon_id in coverages:
            if exon_id not in docs_by_exon:
                raise Exception("No data for sample %s at %s" % (sample_id, exon_id))
            doc = docs_by_exon[exon_id]
            coverages[exon_id] = {
                'callable': doc['callable'],
                'low_coverage': doc['low_coverage'],
                'poor_mapping': doc['poor_mapping']
            }
        return coverages