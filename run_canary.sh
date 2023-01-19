#!/bin/bash -l

module load python
python canary.py -o test.csv -p $CFS/nstaff/tylern $SCRATCH
