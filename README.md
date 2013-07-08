xBrowse Coverage
================

This is a small package that xBrowse uses to manage coverage data.
It's probably not useful to anybody else - easier to use BEDtools or whatever.
But feel free to get in touch if you have a reason to expand it.

The coverage data we work with now all comes back in a BED file; each region in the genome is annotated with one of:
    POOR_MAPPING_QUALITY
    LOW_COVERAGE
    NO_COVERAGE
    CALLABLE
    REF_N

This package read these raw BED files for a set of individuals,
loads the raw data into a MongoDB database, and provides a set of lookup methods.

As part of the wrapper, we condense these fields into the following:
    callable
    low_coverage
    poor_mapping

Where `REF_N` is considered `poor_mapping`.

We also use a default of `low_coverage`, for areas outside the target region that are not included in the input file.

This is somewhat of an experiment. As a one-off feature, it would probably have been easier to read the BED files directly.
I want to test out the usability and performance here, as we anticipate adding many more BED-style "tracks" in the future.

### API

