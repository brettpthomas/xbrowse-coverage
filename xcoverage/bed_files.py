import constants

from xbrowse import genomeloc

def iterate_coverage_bed_file(bed_file):
    for line in bed_file:
        fields = line.strip().split('\t')
        chr = 'chr' + fields[0]
        start = int(fields[1])
        end = int(fields[2])
        xstart = genomeloc.get_single_location(chr, start)
        xend = genomeloc.get_single_location(chr, end)
        coverage = constants.COVERAGE_TAG_MAP[fields[3]]

        yield {
            'xstart': xstart,
            'xend': xend,
            'xpos': {'xstart': xstart, 'xend': xend}, # for geospatial indexing
            'coverage': coverage,
        }