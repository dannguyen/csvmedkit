# TODOS


## 0.1 

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
    - [x] use cmkmixutil class
    - [x] sans replacement flag
    - [x] port old tests
    - [ ] implicit stdin pipe isn't working; fix broken test
    - [ ] make `-E` more robust, e.g. a custom formatter that looks for 2/3 nargs



- csvrgrep 
    - [?] port over
    - [x] port tests
    - [?] clean up argument/stdin handling
        - [ ] finish up isatty hangups
    - [ ] clean up filter_rows
    - [ ] does implicit stdin pipe work? write test

- write intro docs


## 0.2

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
