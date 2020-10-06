# TODOS


## 0.1 

- csvflatten
    - [X] add tabulate/csvview internal
    - [x] general tests
    - [ ] is default prettify markdown-table compatible? 
        - seems to be yes? https://gist.github.com/dannguyen/296461fd1ccdd3719ecb36a6302a65f3
- csvheader
    - [x] default preview headers listing
    - [x] `--HA/--add-generic-headers`
    - [x] `--HM/--make-generic-headers` 
    - sed headers
        - [x] basic
        - [x] write tests
    - slug headers
        - [x] basic
        - [x] write tests
    - rename headers
        - [x] basic
        - [x] validate given indexes
        - [x] write tests

- csvrgrep 
    - [?] port over
    - [x] port tests
    - [?] clean up argument/stdin handling
        - [ ] finish up isatty hangups
    - [ ] clean up filter_rows

- csvsed
    - [ ] use cmkmixutil class
    - [ ] don't implement csvrgrep for now, but move filter class over?
    - [ ] sans replacement flag

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