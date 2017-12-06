# Backend ReadMe

## Building and using the container

* Starting at the root of the repository.
* `cd backend/ && bash build_container.sh`
* `docker images` should now include something like:

```
REPOSITORY                     TAG                 IMAGE ID            CREATED             SIZE
backend_test_container         0.1                 df7a03f558df        38 minutes ago      976MB
```
* This container contains all the required stuff for the backend but none of the front end so far. This includes all the netcdf libraries aswell as some standard tools, feel free to add anything but if you do please put them into the docker file and retag with a new version number.
* To run stuff manually inside the container you can simply do `docker run -it  backend_test_container:0.1` the `-it` simply means that it is run in interactive mode.
* To run specific code in the container you first have to mount the directory inside the container using the flag `-v <path_on_host>:<path_inside_container>` you also have to specify something to run. After this has run the container will die and any output in folders not mounted will dissapear into the abyss. An example script could be 

```
#!/usr/bin/env bash
SCRIPTPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
docker run -it -v $SCRIPTPATH:/root/code backend_test_container:0.1 bash /root/code/run_on_start.sh
```

* A trick to stop the container dying when the command returns is to put `sleep infinity` at the end of the script that runs when it opens. 

* To get into a container after it is created use `docker exec -it <container or IMAGE ID> bash`

* Any other queries just ask Ben. 

## The current progress with the backend. 
* I have set up the infrastructure (the docker containers, api's and a testing framework. For something to be tested it simply needs to follow the pytest collection naming scheme. 


# VegML Usage

A standard usage cycle might look like.

```
from VegML import ClimModel
from VegML import VegML

TEST_NC = "some_file.nc"

model = VegML()
model_id = model.create_model(model_type="KNN")
train = [ClimModel(TEST_NC) for _ in range(10)]
labels = [0 for _ in range(5)] + [1 for _ in range(5)]
performance = model.partial_fit(model_id=model_id, data=train, targets=labels)
predictions = model.predict(model_id=model_id, data=train)
model.close_model(model_id=model_id)

model.delete_model(model_id=model_id)
```

The system will automatically persist models and load and save them as necessary by their id strings.
It supports concurrent access from different instances of the VegML object.












