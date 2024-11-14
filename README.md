# Data annotation module

## Description

This project hosts the code for the data annotation module of real data management workflow in Synthema.
Data annotation component is responsible for:

* Creating a disease-specific dataset schema
* Retrieving an existing dataset schema
* Updating an existing dataset schema
* Deleting an existing dataset schema

### Structure

The data-annotation module is structured in the following folders:

* The folder *src* provides utilities, datasets, models, fastapi, requirements and Dockerfile
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
