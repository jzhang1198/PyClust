from datetime import datetime
import paramiko
import json
import os

root_dir = os.path.dirname(os.path.dirname(__file__))
config_path = os.path.join(root_dir, 'config.json')

def realpath(path: str, ssh_client):
    """ 
    Checks whether a path exists on a remote server.
    """
    sftp = ssh_client._ssh_client.open_sftp()
    isreal = True if sftp.stat(path).st_mode & 0o100000 or sftp.stat(path).st_mode & 0o040000 else False
    return isreal

class SSHClient:
    def __init__(
              self, 
              cluster_id: str
              ):
        
        hostname, username, path_to_key = SSHClient._map_cluster_id(cluster_id)
        self.hostname = hostname
        self.username = username
        self.path_to_key = path_to_key

        # set internal attributes
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    @staticmethod
    def _map_cluster_id(cluster_id: str):

        with open(config_path, "r") as f:
            config = json.load(f)

        hostname = config[cluster_id]['hostname']
        username = config[cluster_id]['username']
        key = config[cluster_id]['key']

        return hostname, username, key

    def connect(self, port: int = 22):
        try: 
            self._ssh_client.connect(self.hostname, port, self.username, key_filename=self.path_to_key)
            print('SSH connection to {} successful.'.format(self.hostname))
        except paramiko.SSHException as e:
            print('SSH connection to {} successful: {}'.format(self.hostname, e))

    def local_to_remote_scp(self, source: str, target: str):
        """ 
        Wrapper over paramiko.SSHClient methods for local to remote scp.
        """
        sftp = self._ssh_client.open_sftp()
        sftp.put(source, target)
        sftp.close()

    def remote_to_local_scp(self, source: str, target: str):
        """ 
        Wrapper over paramiko.SSHClient methods for remote to local scp.
        """
        with self._ssh_client.open_sftp() as sftp:
            sftp.get(source, target)
        sftp.close()

    def qstat(self):
        """
        Wrapper over paramiko.SSHClient methods for qstat command
        """
        _, stdout, _ = self._ssh_client.exec_command('qstat')
        print(''.join(stdout.readlines()))

    def exec_command(self, command: str):
        """"
        Wrapper over paramiko.SSHClient methods for executing bash commands.
        """
        stdin, stdout, stderr = self._ssh_client.exec_command(command)
        return stdin, stdout, stderr

class SGEJob:
    def __init__(
            self, 
            scratchspace: str, 
            conda_env_name: str,
            job_name: str = 'sgejob',
            time_allocation: str = '02:00:00',
            memory_allocation: float = 3
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

        self.scratchspace = scratchspace
        self.conda_env_name = conda_env_name
        self.job_name = job_name
        self.n_jobs = 1
        self.time_allocation = time_allocation
        self.memory_allocation = memory_allocation

        # make a subdir to hold stderr and stdout
        date = datetime.now()
        dirname = f'{date.year}-{date.month}-{date.day}_{date.hour}-{date.minute}-{date.second}'
        self.scratchspace_subdir = os.path.join(self.scratchspace, dirname)

        # set internal attributes
        self.job_id = None
        self.script = None

    def _generate_qsub_command(self, script_path: str):
        qsub_command = ' '.join([
            'qsub',
            '-wd',
            self.scratchspace_subdir,
            '-N', 
            self.job_name,
            '-t', 
            '1-{0}'.format(self.n_jobs),
            '-l', 
            'h_rt={0}'.format(self.time_allocation),
            '-o',
            self.scratchspace_subdir,
            '-e',
            self.scratchspace_subdir
                    ]) 
        
        qsub_command += "<<'END'\n#!/bin/bash\n#$ -wd {}\n#$ -S /bin/bash\nconda activate {} && {}\nEND".format(self.scratchspace_subdir, self.conda_env_name, script_path)

        return qsub_command

    def submit_from_local(self, local_script: str, ssh_client: SSHClient):
        """ 
        Method for submitting SGE jobs from a local device.

        Parameters:
        local_script (str): path to the locally-hosted script you want to run.
        ssh_client (SSHClient): an SSHClient object. Note that the .connect()
            needs to be called beforehand to establish remote connection.
        """

        if not realpath(self.scratchspace, ssh_client):
            print(f'{self.scratchspace} does not exist on {ssh_client.username}@{ssh_client.hostname}.')
            return

        if self.job_id:
            print(f'{self.job_id} is still running.')
            return
        
        # within the scratchspace, create a unique dir to store stdout and stderr
        ssh_client.exec_command(f'mkdir {self.scratchspace_subdir}')

        # transfer local script to Wynton via scp and make it executable
        target = os.path.join(self.scratchspace_subdir, local_script.split('/')[-1])
        ssh_client.local_to_remote_scp(local_script, target)
        ssh_client.exec_command('chmod +x {}'.format(target))
        
        # generate and execute qsub command
        qsub_command = self._generate_qsub_command(target)
        _, stdout, stderr = ssh_client.exec_command(qsub_command)
        stdout, stderr = ''.join(stdout.readlines()), ''.join(stderr.readlines())

        if len(stdout) > 0:
            print(stdout)
            job_id = stdout.split(' ')[2]
            self.job_id = job_id
            self.script = target
        elif len(stderr) > 0:
            print(stderr)
    
    def submit():
        """ 
        Method for submitting SGE jobs from within the cluster.
        """
        pass

    def retrieve_output(self, ssh_client: SSHClient, target_dir: str = '.', retrieve_std: bool = False):
        """ 
        Method for retrieving program output.

        Parameters:
        target (str, optional): the locally-hosted directory to dump output files.
        retrieve_std (bool, optional): determines whether or not stdout and stderr files are retrieved.
        """
        
        stderr_file, stdout_file, script_file = '{}.e{}?'.format(self.job_name, self.job_id), '{}.o{}?'.format(self.job_name, self.job_id), self.script.split('/')[-1]
        excluded_files = {stderr_file, stdout_file, script_file} if not retrieve_std else {script_file}

        _, stdout, _ = ssh_client.exec_command(f'ls {self.scratchspace_subdir}')
        output_files = [item.rstrip('\n') for item in stdout.readlines() if item.rstrip('\n') not in excluded_files]

        for output_file in output_files:
            ssh_client.remote_to_local_scp(os.path.join(self.scratchspace_subdir, output_file), os.path.join(target_dir, output_file))