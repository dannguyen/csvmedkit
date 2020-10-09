# TODOS


## 0.1 

- csvpivot
    - [ ] implementation
        - [ ] should throw warning if user has custom name aggregation when `--pivot-column` is set
    - [ ] port tests
        - Left off with this broken: `test_agg_count_with_2_args_typecast`
    - [ ] documentation
- csvflatten
    - documentation
        - [ ] write up common use cases
    - [X] how to deal with extremely long headers?
        - if `-L` isn't specified, and max header is bigger than terminal, then throw error/warning
    - [X] add agate.print_table internally, i.e. `--prettify`
    - [X] add ``--row_ids``
    - [x] general tests
    - [x] is default prettify markdown-table compatible? 
        - seems to be yes? https://gist.github.com/dannguyen/296461fd1ccdd3719ecb36a6302a65f3

- csvheader
    - [ ] documentation
    - [x] default preview headers listing
    - [x] `--HA/--add-headers`
    - [x] `--HM/--make-generic-headers` 
    - sed headers (replace)
        - [x] renamed it to: `-X/--regex`
        - [x] basic
        - [x] write tests
    - slugify headers
        - [x] basic
        - [x] fix tests from --slug to --slugify
    - rename headers
        - [x] basic
        - [x] validate given indexes
        - [x] write tests


- csvsed
    - [ ] documentation
    - [x] use cmkmixutil class
    - [x] sans replacement flag
    - [x] port old tests
    - [x] implicit stdin pipe isn't working; fix broken test
    - moved -E functionality to experimental phase for now
        - [NA] make `-E` more robust, e.g. a custom formatter that looks for 2/3 nargs


- Overall documentation
    - [ ] Write intro
    - [ ] Write tutorial
    - [ ] Write installation and requirements

## Datasets

- [ ] Census selected characteristics, for csvheaders

## 0.2

- csvpose: transposing
    - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.transpose.html
- csvslice
    - `-i/--index`: 

- csvdrop
    - https://stackoverflow.com/questions/14661701/how-to-drop-a-list-of-rows-from-pandas-dataframe
    - syntax: '0,1,2,10-20,-1,-5:,30:'
    - `-o` log 




## 0.0

- fix setup.py, add dependencies, test utils, etc
- add csvmedkitutil, and other baseclasses
- set up pypi
- did cookiecutter stuff




## Future

- csvswitch: case/switch transform

- csvpivot extra:
    - https://agate.readthedocs.io/en/1.6.1/api/table.html#agate.Table.pivot
    - [ ] option to sort? But is that even useful when doing just a column pivot? How about ordering columns alphabetically/numerically too? `--sort-row` `--sort-col` `a,z,n,0`
    - [ ] grand total column and row?
    - Table.pivot() params to consider:
      - default_value – Value to be used for missing values in the pivot table. Defaults to Decimal(0). If performing non-mathematical aggregations you may wish to set this to None.




- csvrgrep 
    - [?] port over
    - [x] port tests
    - [?] clean up argument/stdin handling
        - [ ] finish up isatty hangups
    - [ ] clean up filter_rows
    - [ ] does implicit stdin pipe work? write test
