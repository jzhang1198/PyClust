# PyClust

Python package for managing job submission to remote clusters.

## Submitting Jobs Directly from Your Local Device

One of the neat features of this package is that it enables submission of jobs directly from a Python runtime hosted on your local device. In order to do this, you will need to create a file named `config.json` within the root of your cloned repo. Here is an example of what it should look like:

```
{
    "wynton": {
        "hostname": "log1.wynton.ucsf.edu",
        "username": "jzhang1198",
        "key": "/path/to/key"
    }
}
```

Note that you will need to set up passwordless SSH in order to obtain an SSH key. The [Wynton documentation](https://wynton.ucsf.edu/hpc/howto/log-in-without-pwd.html) has some helpful resources on this. Now, you should be able to connect to the remote server within a local Python runtime running:

```python
ssh_client = SSHClient(cluster_id = 'wynton')
ssh_client.connect()
```