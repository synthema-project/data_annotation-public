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



## License

This project is licensed under the [MIT License](LICENSE).

This project extends and uses the following Open Softwares, which are compliant with MIT License:

* FastAPI: MIT License
* Pandas: BSD License
* psycopg2-binary: PostgreSQL License
* Uvicorn: BSD License
* python-multipart: MIT License
* python-jose: MIT License
* passlib: BSD License
* pytest: MIT License
* jsonschema: MIT License
* sqlalchemy: MIT License
* sqlmodel: MIT License
* requests: Apache 2.0 License
