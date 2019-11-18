# This folder countains all the files that are mandatory to be conpliant with the Travis CICD worflow. 

## Here are the steps to follows when adding a new project :

1. Copy past this folder in the root of the repository and rename it with the name of your project. (Has to be the same as the name of your image on DockerHub.)
2. Edit the followings files (search for the TODOs) :
    1. docker-compose.yml
    2. Dockerfile
    3. Version (Set your first version)
3. When you will release for the first time, comment the .check-version in the Makefile in test and release sections. The script will look for a previous version that doesn't exist yet.
4. For an overview of the different commands available in the Makefile : ```console make   ```


## Guidelines once your project has been set

1. You MUST change your version file for each Pull request following the  [Semantic Versioning](https://semver.org/)
3. The VERSION file MUST follows the following format : x.x.x, e.g. 1.5.3
2. You SHOULD have some tests in the folder test. 

