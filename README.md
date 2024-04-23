# PipeBio Plugins

This repository contains a sample plugin, based on the [Trinity](https://github.com/trinityrnaseq/trinityrnaseq/wiki) tool, 
developed at the Broad Institute and the Hebrew University of Jerusalem.

## Plugins structure

Plugins are packaged as docker images and use the [PipeBio python SDK](https://github.com/pipebio/python-library) to interact with PipeBio, 
in the same way you would if you were running the code locally. 
The plugin architecture automatically authenticates as the user running the job, you do not need to do anything for this. 
When running the plugin will have the **same project permissions** as the user running the job.

The Dockerfile is used to create the docker image, it:
* installs all dependencies required for the plugin
* sets the CMD entrypoint for the running container `/bin/entrypoint.sh`

The `/bin/entrypoint.sh` script simply activates the [conda](https://conda.io/docs/test-drive.html) environment and runs `python ../runner.py`

`runner.py` - this file is a wrapper around your custom code, that simply adds some logging around your job, 
some basic validation and launches your custom code.

`/custom_code` - this is the directory where you custom code should be implemented. 
It can interact with PipeBio via the SDK and any additional code you wish to add. 
If you need to add any new dependencies, ensure you have added them to the `Dockerfile`

## Building plugins
See [docker-build-a-beginners-guide-to-building-docker-images](https://stackify.com/docker-build-a-beginners-guide-to-building-docker-images/) for an explanation of how to build docker images if you need help.

## Running plugins
When you have finished development of your plugin, you will need to push the image to a container image repository, for instance [Dockerhub](https://hub.docker.com/). 
If your repository is private, you will need to add `pipebio` as a collaborator for us to be able to pull the image.

Once the plugin is pushed to a repo, that PipeBio is a collaborator on, you are ready to begin configuring you plugin in the PipeBio app. 
This will allow you to configure and parameters needed at runtime for your plugin and to set the image to use for your plugin.

