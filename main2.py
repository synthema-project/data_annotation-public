from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, PositiveInt, PositiveFloat
from typing import List, Dict, Union
#from typeguard import check_type
import uuid
import json
import numpy as np

app = FastAPI()

class DynamicDataset(BaseModel):
    data : Dict[str, Dict[str, List[Union[str, int, float, bool]]]]
#class DynamicDataset(BaseModel):
##    metadata: Dict[str, List[Union[str, int, float, bool]]]
#    mutations: Dict[str, List[int]]
#    clinical: Dict[str, List[float]]

class ModelRequirements(BaseModel):
    model : Dict[str, Dict[str, List[Union[str, int, float, bool]]]]
    #table: str
    #columns: List[str]

#required_tables = ["metadata", "mutations", "clinical"]
key_checks = {
        "metadata": {"ID": {"type":str},
                     "Age": {"type": int, "positive": True},
                     "Weight" : {"type":float, "positive":True},
                     "Height" : {"type":float, "positive":True},
                     "Alcool" : {"type": bool, "allowed_values": [True, False]},
                     "Smoking" : {"type": bool, "allowed_values": [True, False]},
                     },
        "mutations": {"IDH1": {"type": int, "allowed_values": [0, 1]},
                      "ATRX" : {"type": int, "allowed_values": [0, 1]},
                      },
        "clinical" : {"BMB": {"type": float, "positive": True},
                      "LDH" : {"type":float, "positive": True}
                      }
    }

type_keys = {
    int: 'integer',
    float: 'floating',
    str: 'string',
    bool: 'boolean',
}

sign_keys = {
    1: 'positive',
    -1: 'negative'
}

#def check_dataset(DD: DynamicDataset):
#    errors = []
#    #faccio il check sulle tabelle
##    for tab in required_tables:
 ##       if tab not in DD['data']: #se la tabella non è presente, appendo un errore
#            errors.append(f"Error: '{tab}' table is missing")
##            yield f"Error: '{tab}' table is missing"
 #       else: #se la tabella è presente, controllo le colonne
 #           for col, check in table_keys.items(): #controllo colonne e valori
 #               if col in DD['data'][tab]: #se la colonna è presente
 #                   for sub_key, sub_checks in check.items(): #controllo tipo e valore
  #                      if sub_key in DD['data'][tab][col]:
 #                           values = DD['data'][tab][col][sub_key]
 #                           for value in values:
 #                               if not isinstance(value, sub_checks["type"]):
 #                                   errors.append(f"Error: '{sub_key}' values must be of type {sub_checks['type']}")
 #                                   yield f"Error: '{sub_key}' values must be of type {sub_checks['type']}"
 #                               elif sub_checks.get("positive") and value <= 0:
 #                                   errors.append(f"Error: '{sub_key}' values must be positive")
 #                                   yield f"Error: '{sub_key}' values must be positive"
 #                               elif sub_checks.get("allowed_values") and value not in sub_checks["allowed_values"]:
  #                                  errors.append(f"Error: '{sub_key}' values must be in {sub_checks['allowed_values']}")
  #                                  yield f"Error: '{sub_key}' values must be in {sub_checks['allowed_values']}"
  #  yield errors

def check_dataset(DD:DynamicDataset):
    key_checks = {
        "metadata": {"ID": {"type": str},
                     "Age": {"type": int, "positive": True},
                     "Weight": {"type": float, "positive": True},
                     "Height": {"type": float, "positive": True},
                     "Alcool": {"type": bool, "allowed_values": [True, False]},
                     "Smoking": {"type": bool, "allowed_values": [True, False]},
                     },
        "mutations": {"IDH1": {"type": int, "allowed_values": [0, 1]},
                      "ATRX": {"type": int, "allowed_values": [0, 1]},
                      },
        "clinical": {"BMB": {"type": float, "positive": True},
                     "LDH": {"type": float, "positive": True}
                     }
    }

    errors = []
    for tab in key_checks.keys():#required_tables:
        print(key_checks.keys())
        if tab not in DD['data']: #se la tabella non è presente, appendo un errore
            errors.append(f"Error: '{tab}' table is missing")
            yield f"Error: '{tab}' table is missing"
        else: #se la tabella è presente, controllo le colonne
            for key, value in key_checks[tab].items():
                if key in DD["data"][tab]:
                    for field, constraints in value.items():
                        field_value = DD["data"][tab][key][0]#[data.dict()["data"][tab][key].index(field) + 1]
                        if field == "type":
                            type = type_keys[constraints]
                            #print(type)
                            if not isinstance(field_value, constraints):
                                errors.append(f"Error: '{key}' must be of type {type_keys[constraints]}")
                                yield f"Error: '{key}' must be of type {constraints}"
                        elif field == "positive":
                            if field_value < 0:
                                errors.append(f"Error: '{key}' must be a positive {type}")
                                yield f"Error: '{key}' must be a positive {type}"
                        elif field == "allowed_values":
                            if field_value not in constraints:
                                errors.append(f"Error: '{key}' has invalid value. Allowed values are: {constraints}")
                                yield f"Error: '{key}' has invalid value. Allowed values are: {constraints}"
    yield json.dumps(errors)

def check_model(MR:ModelRequirements):
    key_checks = {
        "metadata": {"ID": {"type": str},
                     "Weight": {"type": float, "positive": True},
                     "Alcool": {"type": bool, "allowed_values": [True, False]},
                     },
        "mutations": {"IDH1": {"type": int, "allowed_values": [0, 1]},
                      },
        "clinical": {"BMB": {"type": float, "positive": True},
                     }
    }
    errors = []
    for tab in key_checks.keys():#required_tables:
        if tab not in MR['model']: #se la tabella non è presente, appendo un errore
            errors.append(f"Error: '{tab}' table is missing")
            yield f"Error: '{tab}' table is missing"
        else: #se la tabella è presente, controllo le colonne
            for key, value in key_checks[tab].items():
                if key in MR["model"][tab]:
                    for field, constraints in value.items():
                        field_value = MR["model"][tab][key][0]#[data.dict()["data"][tab][key].index(field) + 1]
                        if field == "type":
                            type = type_keys[constraints]
                            #print(type)
                            if not isinstance(field_value, constraints):
                                errors.append(f"Error: '{key}' must be of type {type_keys[constraints]}")
                                yield f"Error: '{key}' must be of type {constraints}"
                        elif field == "positive":
                            if field_value < 0:
                                errors.append(f"Error: '{key}' must be a positive {type}")
                                yield f"Error: '{key}' must be a positive {type}"
                        elif field == "allowed_values":
                            if field_value not in constraints:
                                errors.append(f"Error: '{key}' has invalid value. Allowed values are: {constraints}")
                                yield f"Error: '{key}' has invalid value. Allowed values are: {constraints}"
    yield json.dumps(errors)

def check_dataset_model(DD:DynamicDataset, MR:ModelRequirements):

    errors = []

    data_tabs = DD['data'].keys()
    model_tabs = MR['model'].keys()

    print(data_tabs)
    print(model_tabs)

    for tab in model_tabs:
        print(tab)
        if tab not in data_tabs:
            errors.append(f"Error: {tab} is not present in dataset!")
            yield f"Error: {tab} is not present in dataset!"
        else:
            #print(DD["data"][tab])
            for key, values in DD["data"][tab].items():
                #print(key)
                #print(values)
                if key not in MR["model"][tab]:
                    errors.append(f"Error: {key} is not present in tab {tab} in dataset!")
                    yield f"Error: {key} is not present in tab {tab} in dataset!"
                else:
                    #field_value = DD['data'][tab][key][0]
                    #constraints = values
                    #print(constraints)
                    model_value = MR['model'][tab][key][0]
                    data_value = DD['data'][tab][key][0]
                    type_name = type(MR['model'][tab][key][0])
                    #print(model_value)
                    #print(data_value)
                    #print(type_name)
                    if type(model_value) is not type(data_value):
                        errors.append(f"Error: '{key}' must be of type {type_name}")
                        yield f"Error: '{key}' must be of type {type_name}"
                    if type_name is not str and type_name is not bool:
                        sign_ref = np.sign(MR['model'][tab][key][0])
                        if np.sign(model_value) != np.sign(data_value):
                            errors.append(f"Error: '{key}' must be {sign_keys[sign_ref]}")
                            yield f"Error: '{key}' must be {sign_keys[sign_ref]}"
                    #for field, constraint in constraints:#.items():
                    #    if field == "type":
                    #        type_name = type_keys[constraint]
                    #        if not isinstance(field_value, constraint):
                    #            errors.append(f"Error: '{key}' must be of type {type_name}")
                    #            yield f"Error: '{key}' must be of type {type_name}"
                        #elif field == "positive":
                        #    if field_value <= 0:
                        #        errors.append(f"Error: '{key}' must be a positive {type_name}")
                        #        yield f"Error: '{key}' must be a positive {type_name}"
                        #elif field == "allowed_values":
                        #    if field_value not in constraint:
                        #        errors.append(f"Error: '{key}' has invalid value. Allowed values are: {constraint}")
                        #        yield f"Error: '{key}' has invalid value. Allowed values are: {constraint}"

    yield json.dumps(errors)



# Generator for generating UUIDs
def generate_uuid():
    while True:
        yield uuid.uuid4()

datasets_storage: Dict[str, Union[DynamicDataset, uuid.UUID]] = {}
dataset_list = []

uuid_generator_data = generate_uuid()
##### DATASET CRUD #####

# Create operation - manually create a dictionary
#@app.post("/datasets/{dataset_uuid}/")
#async def create_dataset(data: DynamicDataset):
#    dataset_uuid = next(uuid_generator_data)
#    #if dataset_name in datasets_storage:
#    #    raise HTTPException(status_code=400, detail="Dataset already exists")
#    errors = list(check_dataset(data.dict()))
#    print(errors)
#    #if errors:
#    #   raise HTTPException(status_code=400, detail=errors)
#    datasets_storage[str(dataset_uuid)] = {"data": data, "uuid": dataset_uuid}
#    return {"message": f"Dataset created successfully", "uuid": str(dataset_uuid)}

# Create operation - upload an existing database (json file)

@app.post("/datasets/{dataset_uuid}/", tags=['Dataset'])
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a dataset in .json format. This function will create and assign it a UUID.
    """
    dataset_uuid = next(uuid_generator_data)
    if file.filename.endswith(".json"):
        dataframe = await file.read()
        try:
            data = json.loads(dataframe)
            errors = list(check_dataset(data))
            #print(errors)
            datasets_storage[str(dataset_uuid)] = {"data": data, "uuid": dataset_uuid}
            dataset_list.append(str(dataset_uuid))
            return {"message": f"Dataset loaded successfully", "uuid": str(dataset_uuid)}, "List of available datasets: ", dataset_list
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing json file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Only json files are accepted")

# Read operation
@app.get("/datasets/{dataset_uuid}/", tags=['Dataset'])#, response_model=Dict[str, Union[DynamicDataset, uuid.UUID]])
async def read_dataset(dataset_uuid: uuid.UUID):
    """
    This function will give you the dataset corresponding to the UUID you insert.
    """
    if str(dataset_uuid) not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    dataset = datasets_storage[str(dataset_uuid)]
    return {"data": dataset["data"], "uuid": dataset["uuid"]}

# Update operation
@app.put("/datasets/{dataset_uuid}/", tags=['Dataset'])
async def update_dataset(dataset_uuid: uuid.UUID, data: DynamicDataset):
    """
    This function will update the dataset corresponding to the UUID you insert.
    """
    if str(dataset_uuid) not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    errors = check_dataset(data)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    datasets_storage[str(dataset_uuid)]["data"] = data
    return {"message": f"Dataset updated successfully", "uuid": str(dataset_uuid)}

# Delete operation
@app.delete("/datasets/{dataset_uuid}/", tags=['Dataset'])
async def delete_dataset(dataset_uuid: uuid.UUID):
    """
    This function will remove the dataset corresponding to the UUID you insert.
    """
    if str(dataset_uuid) not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    del datasets_storage[str(dataset_uuid)]
    dataset_list.remove(str(dataset_uuid))
    return {"message": f"Dataset deleted successfully", "uuid": str(dataset_uuid)}, "List of available datasets: ", dataset_list

#print(datasets_storage)

##### MODELS CRUD #####

models_storage: Dict[str, Union[ModelRequirements, uuid.UUID]] = {}
uuid_generator_model = generate_uuid()
model_list = []

# Create operation for model requirements
#@app.post("/models/{model_uuid}/")
#async def create_model(model: ModelRequirements):
#    model_uuid = next(uuid_generator_model)
    #errors = check_model(model.dict())
    #if errors:
    #    raise HTTPException(status_code=400, detail=errors)
    #merged_table = merge_columns(model)
#    models_storage[str(model_uuid)] = {"model": model, "uuid": model_uuid}
#    model_list.append(str(model_uuid))
#    return {"message": f"Model created successfully", "uuid": str(model_uuid)}

@app.post("/models/{model_uuid}/", tags=['Model'])
async def upload_model(file: UploadFile = File(...)):
    """
    Upload a model in .json format. This function will create and assign it a UUID.
    """
    model_uuid = next(uuid_generator_model)
    if file.filename.endswith(".json"):
        modelfile = await file.read()
        try:
            model = json.loads(modelfile)
            errors = list(check_model(model))
            #print(errors)
            models_storage[str(model_uuid)] = {"model": model, "uuid": model_uuid}
            model_list.append(str(model_uuid))
            return {"message": f"Model created successfully", "uuid": str(model_uuid)}, "List of available models: ", model_list
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing json file: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Only json files are accepted")

# Read operation for model requirements
@app.get("/models/{model_uuid}/", tags=['Model'])
async def read_model(model_uuid: uuid.UUID):
    """
    This function will give you the model corresponding to the UUID you insert.
    """
    if str(model_uuid) not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    model = models_storage[str(model_uuid)]
    return {"model": model["model"], "uuid": model["uuid"]}

# Update operation for model requirements
@app.put("/models/{model_uuid}/", tags=['Model'])
async def update_model(model_uuid: uuid.UUID, model: ModelRequirements):
    """
    This function will update the model corresponding to the UUID you insert.
    """
    if str(model_uuid) not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    errors = check_model(model.dict())
    #if errors:
    #    raise HTTPException(status_code=400, detail=errors)
    models_storage[str(model_uuid)]["model"] = model
    return {"message": f"Model updated successfully", "uuid": str(model_uuid)}

# Delete operation for MR
@app.delete("/models/{model_uuid}/", tags=['Model'])
async def delete_model(model_uuid: uuid.UUID):
    """
    This function will remove the model corresponding to the UUID you insert.
    """
    if str(model_uuid) not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    del models_storage[str(model_uuid)]
    model_list.remove(str(model_uuid))
    return {"message": f"Model deleted successfully", "uuid": str(model_uuid)}, "List of available models: ", model_list

#print(models_storage)
#@app.post("/check_dataset_model/")
#async def check_dataset_model_comp(DD: UploadFile = File(...), MR:UploadFile = File(...)):
##    model_uuid = next(uuid_generator_model)
#    if file.filename.endswith(".json"):
##        modelfile = await file.read()
#        try:
#            model = json.loads(modelfile)
#            errors = list(check_model(model))
#            # print(errors)
#            models_storage[str(model_uuid)] = {"model": model, "uuid": model_uuid}
#            model_list.append(str(model_uuid))
#            return {"message": f"Model created successfully",
#                    "uuid": str(model_uuid)}, "List of available models: ", model_list
#        except Exception as e:
#            raise HTTPException(status_code=500, detail=f"Error processing json file: {str(e)}")
##    else:
#        raise HTTPException(status_code=400, detail="Only json files are accepted")

@app.post("/check_dataset_model/", tags=['Compatibility'])
async def check_DD_MR(dataset_uuid: uuid.UUID, model_uuid: uuid.UUID):
    """
    This function will check the compatibility between the dataset and the model corresponding to the UUIDs you insert.
    """
    ##dataset_uuid_str = str(dataset_uuid)
    #model_uuid_str = str(model_uuid)

    #print("Stored dataset UUIDs:", datasets_storage.keys())
    #print("Stored model UUIDs:", models_storage.keys())
    #print("Received dataset UUID:", dataset_uuid_str)
    #print("Received model UUID:", model_uuid_str)

    #print(str(dataset_uuid) not in datasets_storage.keys())
    #print(str(dataset_uuid) not in datasets_storage)

    if str(dataset_uuid) not in datasets_storage:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if str(model_uuid) not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")

    dataset = datasets_storage[str(dataset_uuid)]["data"]
    model = models_storage[str(model_uuid)]["model"]

    #print(dataset)
    #print(model)

    errors = list(check_dataset_model(dataset, model))
    #print(errors)
    #errors = list(errors)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return {"message": "Dataset and model match successfully"}

# funzioni per restituire le liste dei modelli e dei dataset

@app.get("/get_datasets_list/", tags=['Dataset'])
async def get_datasets_list():
    """
    This function returns a list of all available datasets.
    """
    return ("List of all datasets", dataset_list)

@app.get("/get_models_list/", tags=['Model'])
async def get_models_list():
    """
    This function returns a list of all available models.
    """
    return ("List of all models", model_list)
