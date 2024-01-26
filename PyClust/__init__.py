import subprocess
import os


class SGEJob:
    def __init__(
            self, 
            outpath: str, 
            conda_env_name: str,
            job_name: str = 'sgejob',
            n_tasks: int = 1,
            time_allocation: str = '02:00:00',
            memory_allocation: float = 3,
            hardware_requirements: list = [],
            ):
        """ 
        Constructor for SGEJob object.

        Parameters:
        script_path (str): Path to job script to execute on Wynton.
        conda_env_name (str): The name of the conda environment to run the job script in.
        job_name (str, optional): The name of the job.
        time_allocation (float, optional): The maximum compute time of the job (in hh:mm:ss).
        memory_allocation (float, optional): Memory allocation (in GB).
        """

        self.outpath = outpath
        self.conda_env_name = conda_env_name
        self.job_name = job_name
        self.n_tasks = n_tasks
        self.time_allocation = time_allocation
        self.memory_allocation = memory_allocation
        self.hardware_requirements = hardware_requirements

        # set internal attributes
        self.job_id = None
        self.script = None

    def _generate_qsub_command(
            self,
            job_script: str,
            scrpit_args: str,
    ):
        
        # specify job requirements and allocations
        qsub_command = ' '.join([
            'qsub',
            '-cwd',
            '-N {}'.format(self.job_name),
            '-t 1-{0}'.format(self.n_tasks),
            '-l h_rt={0}'.format(self.time_allocation),
            '-l mem_free={}G'.format(self.memory_allocation),
            '-o {}'.format(self.outpath),
            '-j y'
        ])

        if len(self.hardware_requirements) > 0:
            qsub_command += ' ' + ' '.join(['-l {}'.format(req) for req in self.hardware_requirements])
        
        # in-line script to execute environment activation and job script
        qsub_command += '\n'.join([
            "<<'END'",
            '#!/bin/bash',
            '#$ -wd {}'.format(self.outpath),
            '#$ -S /bin/bash',
            'conda activate {} && {} {}'.format(self.conda_env_name, job_script, ' '.join([str(i) for i in scrpit_args])),
            'END'
        ])

        return qsub_command


    def submit(self, script: str, script_args: str, print_qsub: bool = True):
        """ 
        Method for submitting SGE jobs from within the cluster.
        """
        qsub_command = self._generate_qsub_command(script, scrpit_args=script_args)

        if print_qsub:
            print('')
            print(qsub_command)
            print('')

        try:
            subprocess.run(qsub_command, shell=True, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Error executing qsub command:\n{qsub_command}")
