# Data annotation workflow

## Description

### Structure

Example_data: here we can find an example of dataset structure to upload (example_dataset.json) and an example of a model structure (example_model.json)

fastapi: source code to run the FastAPI annotation workflow 

- data_annotation_utils.py: here the basic functions to upload and check compatibilities between datasets and models are defined
- main.py: here the CRUD functions for both models and datasets are defined.

To run the data ingestion workflow, make the following steps:

1) create the conda environment from the environment.yaml file and activate it

> conda env create -f environment.yaml

> conda activate fastapi

2) run the main.py function

> python main.py

3) open your browser and go to "http://127.0.0.1:8002/docs" (or change 8002 to the port you indicate in the main.py)
