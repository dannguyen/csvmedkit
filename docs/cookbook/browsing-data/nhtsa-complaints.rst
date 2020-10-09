***************************************************************************
Figuring out what's in the NHTSA's safety-related defect complaint database
***************************************************************************


- Landing page: https://www-odi.nhtsa.dot.gov/downloads/
- README: https://www-odi.nhtsa.dot.gov/downloads/folders/Complaints/CMPL.txt
- Direct download (250MB+): https://www-odi.nhtsa.dot.gov/downloads/folders/Complaints/FLAT_CMPL.zip



.. command line for sampling the data:
.. xsv sample -d '\t' 100 ~/Downloads/sample-data-csvmedkit/nhtsa/FLAT_CMPL.txt | csvformat -e latin1 -T > examples/real/nhtsa-complaints.txt



TKTKTK

Looking at the first record::

        $ head -n 1 examples/real/nhtsa-complaints.txt | csvformat -t | csvheaders --HM | csvflatten -P


        | field    | value                                                     |
        | -------- | --------------------------------------------------------- |
        | field_1  | 1                                                         |
        | field_2  | 958173                                                    |
        | field_3  | Ford Motor Company                                        |
        | field_4  | LINCOLN                                                   |
        | field_5  | TOWN CAR                                                  |
        | field_6  | 1994                                                      |
        | field_7  | Y                                                         |
        | field_8  | 19941222                                                  |
        | field_9  | N                                                         |
        | field_10 | 0                                                         |
        | field_11 | 0                                                         |
        | field_12 | SERVICE BRAKES, HYDRAULIC:PEDALS AND LINKAGES             |
        | field_13 | HIGH LAND PA                                              |
        | field_14 | MI                                                        |
        | field_15 | 1LNLM82W8RY                                               |
        | field_16 | 19950103                                                  |
        | field_17 | 19950103                                                  |
        | field_18 |                                                           |
        | field_19 | 1                                                         |
        | field_20 | BRAKE PEDAL PUSH ROD RETAINER WAS NOT PROPERLY INSTALLED, |
        |          | CAUSING BRAKES TO FAIL, RESULTING IN AN ACCIDENT AFTER    |
        |          | RECALL REPAIRS (94V-129). *AK                             |
        | field_21 | EVOQ                                                      |
        | field_22 |                                                           |
        | field_23 |                                                           |
        | field_24 |                                                           |
        | field_25 |                                                           |
        | field_26 |                                                           |
        | field_27 |                                                           |
        | field_28 |                                                           |
        | field_29 |                                                           |
        | field_30 |                                                           |
        | field_31 |                                                           |
        | field_32 |                                                           |
        | field_33 |                                                           |
        | field_34 |                                                           |
        | field_35 |                                                           |
        | field_36 |                                                           |
        | field_37 |                                                           |
        | field_38 |                                                           |
        | field_39 |                                                           |
        | field_40 |                                                           |
        | field_41 |                                                           |
        | field_42 |                                                           |
        | field_43 |                                                           |
        | field_44 |                                                           |
        | field_45 |                                                           |
        | field_46 | V                                                         |
        | field_47 |                                                           |
        | field_48 |                                                           |
        | field_49 |                                                           |
