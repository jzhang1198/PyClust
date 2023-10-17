#!/usr/bin/env python3

""" 
run_jobs.py
Author: Jonathan Zhang
Date: 2023-10-17

Template script for submitting cluster jobs from the command line. This script
is meant to be executed from within the remote cluster, not a local device.
"""

from PyClust import SGEJob
import argparse

def comma_separated_list(value):
    """ 
    Utility function to parse comma separated lists from the command line.
    """
    return [item.strip(' ') for item in value.split(',')]

def init_parser():
    """ 
    Utility function for setting up parser.
    """

    parser = argparse.ArgumentParser(
        description='Script for submitting cluster jobs from the command line.',
        epilog="Example usage:\n\t./run_jobs.py /path/to/output base /path/to/script -N example_job -n 420 -t 05:00:00 -B arch=x86_64, avx2=1")
    parser.add_argument('outpath', help='Path to directory to dump script outputs.')
    parser.add_argument('conda_env_name', help='Conda environment to run script in.')
    parser.add_argument('script', help='Path to job script to run (needs to be executable).')
    parser.add_argument('--script-args', '-A', help='Arguments to pass to job script', default='')
    parser.add_argument('--job-name', '-N', help='The name for the job', default='job')
    parser.add_argument('--n-tasks', '-n',help='The number of tasks.', default=1)
    parser.add_argument('--time-allocation', '-t',help='The time allocation for the job.', default='02:00:00')
    parser.add_argument('--memory-allocation', '-m', help='The memory allocation (in G) for the job.', default=3)
    parser.add_argument('--hardware-requirements', '-B', help='The hardware requirements for the job.', default=[], type=comma_separated_list, nargs='+')

    return parser.parse_args()

if __name__ == '__main__':
	
    # set up argument parser
    args = init_parser()
    
    # construct SGEJob object and submit the job
    job = SGEJob(
        args.outpath,
        args.conda_env_name,
        job_name=args.job_name,
        n_tasks=args.n_tasks,
        time_allocation=args.time_allocation,
        memory_allocation=args.memory_allocation,
        hardware_requirements=[item for sublist in args.hardware_requirements for item in sublist if item != '']
    )
    job.submit(args.script, args.script_args)