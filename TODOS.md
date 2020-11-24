# TODOS


## 0.0.9.14


**csvpivot**

- [ ] documentation
    - usage overview
        - [ ] simple row count
        - [ ] multiple row count
        - [ ] row-x-column crosstab count
            - [ ] come up with better definition of pivot/crosstab
            - [ ... ] Aggregations other than counting
            - [ ] Performing multiple aggregations (left off here)
            - [ ] can't do multiple aggs and column_name
            - [ ] Why count is special
    - pandas comparison
        - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html
        - [ ] apparently pandas can't do a row-x-column pivot?
        - [ ] pandas can do grand total columns
    - [ ] write nutgraf and intro examples and test those examples
    - [ ] write options/flags section
    - [ ] write comparison section
    - [ ] write scenarios/use-cases 



**csvslice**

- do docs; this should be style and template for others
    - [x] document new --head and --tail options
    - [x] write usage examples
    - [ ] write "compared to"
        - figure out how to arrange the compared commands and the output
        - [x] separate into CLI and pandas comparisons
        - [ ] complete pandas section
        - [ ] complete CLI section 
            - [ ] xsv slice 
    - scenarios
        - [ ] finish census real-world scenario    
        - [ ] scenario when comboing with csvsort (most popular baby names?)
        - [ ] --head example with env-inspections narrative data
    - [ ] mention performance issues with xsv slice


-----------------------





## 0.1.0 (public alpha)

Overall stuff
- Separate usecases into their own section, instead of embedding them into the individual tool sections?


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


- csvnorm
    - [X] implementation (0.0.9.10)
    - [X] port tests (0.0.9.10)
    - [ ] documentation
    - [ ] find real world data with multiline narratives etc.
        - cdph-env-inspections


- csvslice
    - [ ] documentation


- csvflatten
    - [ ] have error cases been tested?
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
       - [x] write nutgraf and intro examples and test those examples
        - [x] write options/flags section
        - [ ] write high level overview
        - [ ] write comparison section
        - [x] make sure help doc is up to date with `-A/-B/-C`
        - write scenarios/use-cases 
            - babynames
                - [ ] write tests to confirm babynames tests




## 0.1.5 

**csvheader**

- add a `behead` option to cut off a dataset's header: https://github.com/BurntSushi/xsv/pull/215/commits

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


### 0.0.0.1

- fix setup.py, add dependencies, test utils, etc
- add csvmedkitutil, and other baseclasses
- set up pypi
- did cookiecutter stuff



## 0.0.9.11


csvslice:
    - [X] implementation with simplified `-i/--include` option (0.0.9.11)
    - [x] tests (0.0.9.11)


## 0.0.9.12


csvheader:
    - [X] `-C/--create`: like `--add`, but provide a comma-delimited list (0.0.9.12)
        - [need test] throw error if number of custom column names does not match data
        - [X] write tests
    - [X] throw error if more than one of `-A/-B/-C` is invoked (0.0.9.12)
    - Should we switch to single-hyphen shortnames, e.g. `-AH` and `-CH` (0.0.9.12)
        - [X] in fact, it can be simplified to `-A -B -C`, since csvkit doesn't use them. Also, `--add` is enough for the name, given that the entire context of the tool is operating on a `header`
          - [x] `-B/--bash` renamed from `--ZH/--zap-header`
          - [x] `-A/--add` renamed `--AH/--add-header`
- (older stuff)
    - [x] default `--preview` headers listing
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




## 0.0.9.13 (pushed on 2020-11-11)


- csvpivot
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





**csvslice**

- [x] rename `--intervals` to `--include`; in case we rejigger csvslice to allow resequencing of returned rows?
- [x] rename `--include` to `--indexes`
- [x] create `--head` option, and make `--indexes` optional
- [x] create `--tail` option; use a queue?

**csvsed**

- [x] change `-G/--like-grep` to `-F/--filter`
    - [x] wrote lots of tests to cover combinations of --columns and --filter
    - [x] wrote lots of tests for intermixing of args and opts and stdin
    - [ ] update documentation

**csvheader**

- [x] `-A` and `--AX` options for adding/overwriting a header by passing in a comma-delimited string of column names
- [x] `-G` and `--GX` options for adding/overwriting a header with generic field names
- [x] `-B` and `-C` (bash/create) have been killed for being too confusing  

old thoughts (2020-11-09):

- `-A/--add <column_names>` to add/append headers
- `--AX/--add-x/--AS/--add-sub <column_names` to add and overwrite/substitute header
- `-G/--generic` to append generic headers
- `-GX/--generic-sub/generic-x` to overwrite with generic headers

Old thoughts:

When writing csvheader docs, realized we needed a `-C` option that also replaces the existing header (in the case of piping from csvflatten). And/or, the --rename/-R convention needs to be changed.

NAMING THINGS IS HARD!!! THINK ABOUT IT LATER THIS WEEK


- Is there any reason to have `-B/--bash`? In what situation would a user want to replace existing data headers with generic headers?
    - [ ] not really, so kill it...
- [ ] is `-R/--rename` convention particularly graceful/convenient?
- [x] Instead of `-C`, maybe we should have some kind of `--replace`.
- [ ] But `--replace` is confusing with `--rename`, so maybe use `-C/--change/clobber`, or `-O/--overwrite`?
- [ ] `-X/--regex` should just be `--regex` for now?
