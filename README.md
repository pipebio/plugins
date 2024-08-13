# PipeBio Plugins

This repository contains a sample plugin, based on the [Trinity](https://github.com/trinityrnaseq/trinityrnaseq/wiki) tool, 
developed at the Broad Institute and the Hebrew University of Jerusalem.

## Plugins structure

Plugins are packaged as docker images and use the [PipeBio python SDK](https://github.com/pipebio/python-library) to interact with PipeBio, 
in the same way you would if you were running the code locally. 

The plugin architecture **automatically** authenticates as the user running the job, you do not need to do anything for this. 
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

## Building the Dockerfile and sharing with PipeBio
See [docker-build-a-beginners-guide-to-building-docker-images](https://stackify.com/docker-build-a-beginners-guide-to-building-docker-images/) for an explanation of how to build docker images if you need help.
To build the Dockerfile in this repo
1. Create a [Dockerhub account](https://hub.docker.com/signup) and repo if you haven't already. We recommend you make the repo private.
2. Install and run Docker if you haven't already
3. Then run `docker build -t <your-dockerhub-username>/<docker-project-repo>:<tagname> .` from the root directory. If you're on a mac run `docker build -t <your-dockerhub-username>/<docker-project-repo>:<tagname> --platform linux/x86_64  .`
    - `<your-dockerhub-username>` from your Dockerhub account, [see your profile page here](https://hub.docker.com/settings/general).
    - `<docker-project-repo>` the repo in your Dockerhub account you want to push to.
    - `<tagname>` a useful tag to identify this build, such as `latest`.
4. Push the tagged image from (3) to dockerhub: `docker push <docker-project-repo>/<tagname>`. For example: `docker push owenlamontecribbbodley/pipebio-tests:latest`
5. In Dockerhub add `pipebio` as a collaborator so we can pull the build and run it.

## Developing your Plugin & making changes to the Dockerfile
As you make changes to the Dockerfile you will need to build and push again to have the changes picked up in PipeBio.
For example: `docker build -t <your-dockerhub-username>/<docker-project-repo>:<tagname> .` then `docker push <your-dockerhub-username>/<docker-project-repo>:<tagname>`

## Environment variables
The following environment variables are made available to your code, when running in the PipeBio infrastructure:
* NUMBER_OF_CPUS - an integer count of the number of cpu's available
* AVAILABLE_MEMORY - an integer count of Mib of available memory

## Testing you code locally
As you write you plugin, it can be useful to run it locally, before pushing to dockerhub. 

You will need the [pipebio sdk](https://pypi.org/project/pipebio/) installed locally, see notes there on how to use with an _.env_ file, to set your _PIPE_API_KEY_.

Both techniques, creates a job record, that your plugin code can interact with (getting details of the input docs/updating status etc).

There are two ways to test your code: 

#### Debugging your code locally
The file `runner_test_debug.py` is intended for this.

Running this file calls `runner.py`. You can set breakpoints in your IDE and then step through your code as you wish.

#### Running docker images
The file `runner_test_docker_image.py` is intended for this. 

You will need the [pipebio sdk](https://pypi.org/project/pipebio/) installed locally, see notes there on how to use with an _.env_ file, to set your _PIPE_API_KEY_.

Running this file runs a `docker run ...` command of you packaged code, on your local machine, writing all output to the terminal.

## Important things to be aware of
1. You are responsible for handling failures in your code.