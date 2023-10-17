#!/usr/bin/env python3

""" 
script_example.py
Author: Jonathan Zhang
Date: 2023-10-17

An example job script to illustrate how one can submit a job array on an SGE
cluster (i.e. Wynton).
"""

import os

if __name__ == '__main__':

    # get the directory the job is running in
    working_dir = os.getcwd()
    
    # get task id (set to 1 if there is none)
    task_id = int(os.environ.get("SGE_TASK_ID", 1)) 

    # get total number of tasks (set to 1 if there is none)
    total_jobs = int(os.environ.get("SGE_TASK_LAST", 1)) 

    with open(os.path.join(working_dir, f'output{task_id}.txt'), 'w') as file:
        file.write('Hello from worker #{} of {}!'.format(task_id, total_jobs))