# TODOS


## 0.0.9.14

**thoughts 2020-12-11**

while working on data project, wondered that:

- csvflatten 
    - [x] --prettify should be default
    - [x] option to replace record separator with empty row
- csvnorm
    - [ ] should have the --max-length option, similar to csvflatten


**thoughts 2020-11-24**
- terms across frameworks
    - csvpivot: 
        - long data to wide data
        - pivot_wider == tidyr.spread == reshape.cast/dcast 
    - csvmelt: pivot_longer == tidyr.gather == reshape.melt
        - wide data to long data
- a csvmelt (i.e. unpivot) would be super useful, especially for real-world examples
- for now, link to other resources that explain pivot tables and wide data. don't write my own guide
- pandas.pivot and reshape.cast/tidyr/pivot_wider refer to an `index` argument rather than rows
    - do i want to follow that, or stick with spreadsheet conventions?
- very good reshape2 guide: https://seananderson.ca/2013/10/19/reshape/

    ```R
    melt(airquality, id.vars = c("month", "day"))

    # from:
        ##   ozone solar.r wind temp month day
        ## 1    41     190  7.4   67     5   1
        ## 2    36     118  8.0   72     5   2
        ## 3    12     149 12.6   74     5   3

    # to:

        ##   month day variable value
        ## 1     5   1    ozone    41
        ## 2     5   2    ozone    36
        ## 3     5   3    ozone    12
        ## 4     5   4    ozone    18
        ## 5     5   5    ozone    NA
        ## 6     5   6    ozone    28
    ```

**general documentation**
- given how lengthy usage overview is for csvpivot, maybe every tool should have a Quickstart?
    - [ ] wrote a basic one for csvpivot
    - [ ] do it for csvslice
- write a top level tutorial like csvkit?
    - https://csvkit.readthedocs.io/en/latest/tutorial.html#
    - Getting started congress.csv
        - combine with csvlook and csvjoin
        - csvflatten to view data
        - csvsed to replace values
    - data exploration: narrative data like env inspects
        - csvslice + csvflatten
    - data ranlgling: census
        - csvheader to replace header with custom names
        - csvslice to cut out metadata
    - to and from with csvsqlite and in2csv
        - LESO data stack

- **get inspiration from tidyverse**
    - method reference page: https://tidyr.tidyverse.org/reference/pivot_wider.html#details
        - simple, elegant, with just 4 content headers: Arguments, Details, See Also, and Examples
        - Details is just a short graf, giving background and relation to other methods
        - See Also is a single line and link: pivot_wider_spec() to pivot "by hand" with a data frame that defines a pivotting specification.
            - pivot_wider spec: https://tidyr.tidyverse.org/reference/pivot_wider_spec.html
        - Intro graf includes "Learn more in vignette("pivot")", which links to a different page with more text and elaboration: 
         - https://tidyr.tidyverse.org/articles/pivot.html
    - ggplot2 is good too: https://ggplot2.tidyverse.org/reference/geom_bar.html

**csvflatten**

- --prettify as the default, in the way that csvstat as a --csv option: https://csvkit.readthedocs.io/en/latest/scripts/csvstat.html

**csvpivot**


**pivot readings**

Read pandas docs on pandas.pivot and DataFrame.pivot_table
- pandas.pivot: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot.html
- DataFrame.pivot_table: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.pivot_table.html#pandas.DataFrame.pivot_table
    - Described as `Create a spreadsheet-style pivot table as a DataFrame.`

Reshape2 (Hadley Wickham's general reshaping library)
- tidyr vs reshape2: https://jtr13.github.io/spring19/hx2259_qz2351.html
    - reshape2 does aggregation (like csvpivot), whereas tidyr does not
- journal article: Reshaping Data with the reshape Package
    - https://www.jstatsoft.org/article/view/v021i12
    - study the theory/context sections, e.g. Conceptual Framework
    - 4. Casting molten data
    - study how example data is shown, then referred to in each example

Read tidyverse's article on pivoting: 
- Main https://tidyr.tidyverse.org/articles/pivot.html
- Wider section: https://tidyr.tidyverse.org/articles/pivot.html#wider
- Nutgraf

    > pivot_wider() is the opposite of pivot_longer(): it makes a dataset wider by increasing the number of columns and decreasing the number of rows. It’s relatively rare to need pivot_wider() to make tidy data, but it’s often useful for creating summary tables for presentation, or data in a format needed by other tools.


**R guides**

- An introduction to reshape https://seananderson.ca/2013/10/19/reshape/
    - 'What makes data wide or long?'
    - very well formatted and written guide

- https://ademos.people.uic.edu/Chapter8.html
    - reshape.cast is the equivalent to a Pivot: 
    > Casting will transform long format back into wide format. This will, essentially, make your data look as it did in the beginning (or in any other way you’d prefer).



- cli
    - simplify command-line opts to '--column' and '--rows' from '--pivot-column' and '--pivot-rows'

- [ ] documentation
    - terminology
        - look at tidyverse writeup for pivot_wider
            - https://tidyr.tidyverse.org/reference/pivot_wider.html
            - *`pivot_wider() "widens" data, increasing the number of columns and decreasing the number of rows. The inverse transformation is pivot_longer().*
        - look at tidyverse writeup for spread() (spread is now deprecated): 
            - https://rstudio-pubs-static.s3.amazonaws.com/282405_e280f5f0073544d7be417cde893d78d0.html
            - "key: The column you want to split apart (Field)"
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
    - other references about Pivot Tables
        - Pivot Tables in Google Sheets: A Beginner’s Guide: https://www.benlcollins.com/spreadsheets/pivot-tables-google-sheets/#one
        - https://business.tutsplus.com/tutorials/how-to-use-pivot-tables-in-google-sheets--cms-28887
        - https://support.microsoft.com/en-us/office/create-a-pivottable-to-analyze-worksheet-data-a9a84538-bfe9-40a9-a8e9-f99134456576

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


- csvmelt/csvgather:
    - pandas uses "melt()" to refer to an "unpivot" https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.melt.html
        - >This function is useful to massage a DataFrame into a format where one or more columns are identifier variables (id_vars), while all other columns, considered measured variables (value_vars), are “unpivoted” to the row axis, leaving just two non-identifier columns, ‘variable’ and ‘value’.

    - r lang: https://www.rdocumentation.org/packages/reshape2/versions/1.4.4/topics/melt
    - tidyr: gather/pivot_longer https://tidyr.tidyverse.org/reference/pivot_longer.html
    - tidyverse https://uc-r.github.io/tidyr#gather
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
