
def get_interval_overlap(xstart, xend, coverage_interval):
    """
    How much does coverage_interval overlap the region defined by xstart, xend
    Both region and interval are *inclusive*
    """
    if xstart > coverage_interval['xend']: return 0
    if xend < coverage_interval['xstart']: return 0

    return 1 + xend - xstart - max(0, coverage_interval['xstart']-xstart) + min(0, coverage_interval['xend']-xend)

def get_coverage_totals_in_region_for_interval_set(xstart, xend, interval_set):
    """
    Coverage total in a region for the intervals in interval_set
    """
    totals = {k: 0 for k in ['callable', 'low_coverage', 'poor_mapping']}
    for interval in interval_set:
        overlap = get_interval_overlap(xstart, xend, interval)
        totals[interval['coverage']] += overlap
    total_so_far = sum(totals.values())
    totals['low_coverage'] += (xend - xstart - total_so_far)
    return totals

def flatten_region_list(region_list):
    """
    Flatten a region list if they overlap
    region_list is a list of (start, end) tuples
    Returns a new list of region tuples
    """
    if len(region_list) == 0: return []

    flattened_list = []

    current_region = region_list[0]
    for start, end in region_list[1:]:
        if start <= current_region[1]:
            current_region = (current_region[0], end)
        else:
            flattened_list.append(current_region)
            current_region = (start, end)
    flattened_list.append(current_region)
    return flattened_list
