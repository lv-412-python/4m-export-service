# Export service [![Build Status](https://travis-ci.org/lv-412-python/export-service-repo.svg?branch=develop)](https://travis-ci.org/lv-412-python/export-service-repo) 
## Description
This is the source code of the export service, part of 4m project. This service gets parameters, forms the task for worker-service, and sends it to the Rabbit.

## Technologies
* Python (3.6.8)
* Flask (1.0.3)

## Install
For the next steps of service installation, you will need setup of Ubuntu 18.04


### In the project root create venv and install requirements with Make

```
sudo docker pull rabbitmq
sudo docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3

cd export-service

sudo docker build -t export_service .
sudo docker run -d -p 5055:5055 export_service
```

### Run project

#### run in development mode
```
make dev-env
```

#### run in production mode
```
make prod-env
```


## Project team:
* **Lv-412.WebUI/Python team**:
    - @sikyrynskiy
    - @olya_petryshyn
    - @taraskonchak
    - @OlyaKh00
    - @ement06
    - @iPavliv
    - @Anastasia_Siromska
    - @romichh
