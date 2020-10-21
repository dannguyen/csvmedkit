# TODOS


## 0.1 


- csvheader
    - [ ] documentation
       - [x] write nutgraf and intro examples and test those examples
        - [x] write options/flags section
        - [ ] write high level overview
        - [ ] write comparison section
        - [ ] write scenarios/use-cases 

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


- csvpivot
    - [ ] documentation
        - [ ] write nutgraf and intro examples and test those examples
        - [ ] write options/flags section
        - [ ] write high level overview
        - [ ] write comparison section
            - [ ] look up pandas equivalent
        - [ ] write scenarios/use-cases 

    - [x] implementation
        - [X] handle multiple aggregations if user doesn't specify column
            - [YES] does that make groupby obsolete?
        - [x] refactored aggy
        - [x] add UniformReader to interface
            - [NO] use `@filtered_column_ids` instead of `cmk_parse_col_ids` -- filtered_column_ides only works with `-c/--columns`
        - [x] needs better error message:
            - csvpivot examples/real/denver-pot-sales.csv -r YEAR -a sum:GROSS `KeyError: 'GROSS'`
    - [x] port tests
    - performance
        - [x] created filtered table to remove all columns not specified in the arguments
        - [x] benchmarking
            - `time csvpivot examples/drafts/fed-judges-service.csv -r 'Appointing President,ABA Rating' > /dev/null`
                - was 10s, now 0.5s


- csvsed
    - [ ] documentation
        - [ ] write nutgraf and intro examples and test those examples
        - [ ] write options/flags section
        - [ ] write high level overview
        - [ ] write comparison section
        - [ ] write scenarios/use-cases 
    - [ ] cmk_filter_rows should be refactored into a class instance method, and have its signature minimized
    - [x] use cmkmixutil class
    - [x] sans replacement flag
    - [x] port old tests
    - [x] implicit stdin pipe isn't working; fix broken test
    - moved -E functionality to experimental phase for now
        - [NA] make `-E` more robust, e.g. a custom formatter that looks for 2/3 nargs

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


- csvnorm
    - [ ] implementation
    - [ ] port tests

- Overall documentation
    - [ ] Write intro
    - [ ] Write tutorial
    - [ ] Write installation and requirements

## Datasets

- [ ] Census selected characteristics, for csvheaders

## 0.2


- csvmelt:
    - tidyr: gather/pivot_longer https://tidyr.tidyverse.org/reference/pivot_longer.html
    - 
    - pt.normalize('gender', ['white', 'black', 'asian', 'latino'])
    | gender | property | value |
    | ------ | -------- | ----- |
    | female | white    |     1 |
    | female | black    |     2 |
    | female | asian    |     1 |
    | female | latino   |     0 |
    | male   | white    |     0 |
    | male   | black    |     0 |
    | male   | asian    |     1 |
    | male   | latino   |     1 |

- csvpose: transposing
    - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.transpose.html
- csvslice
    - `-i/--index`: 

- csvdrop
    - https://stackoverflow.com/questions/14661701/how-to-drop-a-list-of-rows-from-pandas-dataframe
    - syntax: '0,1,2,10-20,-1,-5:,30:'
    - `-o` log 




- csvpivot
- [ ] should throw warning if user has custom name aggregation when `--pivot-column` is set
- [ ] when an aggregation involves calculation, fill the targeted column with non-nulls 






## Future

- csvdate:
    - normalize any/all datefields to isoformat
    - set time zone
    - given a series of columns, create a single column

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



## Old


### 0.0

- fix setup.py, add dependencies, test utils, etc
- add csvmedkitutil, and other baseclasses
- set up pypi
- did cookiecutter stuff
