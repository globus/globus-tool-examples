# Globus Tool Examples
Simple code scripts for various use cases using Globus.

(Currently, the repo contains only one script).

## Getting Started
Create a Python 3 virtual environment and install Globus SDK and Globus CLI
```
$ git clone git@github.com:globus/globus-tool-examples.git
$ python3 -mvevn venv
$ . vevn/bin/activate
(venv) $ cd globus-tool-examples/
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
```
## Running the scripts

### migrate_permissions.py

When managing data on Globus endpoints, there is sometimes a need to move all data from one endpoint to another. It is a case, especially, when a machine is set to retire. Migrating all data from one Globus endpoint to another does not mean moving files only. With a variety of features Globus provides like groups, sharing, access permissions, roles, etc. to keep all users's access to the same files on a new endpoint, Globus permissions must be migrated as well. It means that the full migration process requires two steps.

#### File migration
To copy all files from one endpoint to another, users can use the [Globus Web App](https://www.globus.org/), or the [Globus CLI](https://docs.globus.org/cli/):
```
(venv) $ globus transfer -r -s checksum <source_endpoint_UUID>:/ <destination_endpoint_UUID>:/[<prefix>/]
```
where the options indicates:
- `-r` transfer the directory recursively
- `-s` sync - only transfer new or changed files (where a checksum is different). The option is useful if you needed to stop a transfer for some reason, and want to start the same transfer again but avoid transferring files that already have been copied.

The optional `prefix` path is useful if a user wants to transfer files from the source endpoint to a subdirectory on the destination endpoint.

A UUID of a Globus endpoint can be found using [Globus Web App](https://app.globus.org/endpoints) in the 'Overview' tab of an endpoint, or using the [Globus CLI](https://docs.globus.org/cli/quickstart/#try_an_endpoint_search), e.g.:
```
(venv) $ globus endpoint search 'petrel#testbed'
ID                                   | Owner               | Display Name
------------------------------------ | ------------------- | -------------------------------
e56c36e4-1063-11e6-a747-22000bf2d559 | petrel@globusid.org | petrel#testbed
a742210c-17ad-11eb-893e-0a5521ff3f4b | petrel@globusid.org | ticket349455 petrel dtn testbed
```

#### Permission migration
When all files are copied to the new endpoint, you must copy all Globus permissions to the new endpoint. The `migrate_permissions.py` scripts copies all Globus permissions from one endpoint to another:
```
(venv) $ python migrate_permissions.py -s <source_endpoint_UUID> -d <destination_endpoint_UUID> [-p <prefix>]
```
If files were transferred from the source endpoint to a subdirectory on the destination endpoint, then all paths associated with Globus permissions must be prefixed by the same subdirectory path (`-p prefix` option).

The script can be run multiple times. If a Globus permission has already been copied to the destination endpoint, it will not be copied again.
