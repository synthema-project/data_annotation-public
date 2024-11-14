# Data annotation workflow

## Description

This project hosts the code for the data annotation module of real data management workflow in Synthema.
Data annotation component is responsible for:

* Creating a disease-specific dataset schema
* Retrieving an existing dataset schema
* Updating an existing dataset schema
* Delete an existing dataset schema

The folder common provides general utilities, datasets and models.
The folder apps includes the various applications mentioned.
The folder fl_client is dedicated to the component FL client of the architecture.
The folder fl_server is dedicated to the component FL server of the architecture.
The folder restapi is dedicated to the REST API to allow for human interaction with the system.

### Structure

The data-annotation module 

* The folder *src* provides utilities, datasets, models and fastapi
* The folder *k8s* includes kubernetes manifests
* The folder *jenkins* contains the Jenkinsfile to run unit and functional tests. 

## Data-annotation deployment

To run the data ingestion workflow, make the following steps:

1) create the conda environment from the environment.yaml file and activate it

> conda env create -f environment.yaml

> conda activate fastapi

2) run the main.py function

> python main.py

3) open your browser and go to "http://127.0.0.1:8002/docs" (or change 8002 to the port you indicate in the main.py)
