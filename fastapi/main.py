from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, PositiveInt, PositiveFloat
from typing import List, Dict, Union
#from typeguard import check_type
import uuid
import json
import numpy as np
from data_annotation_utils import generate_uuid, check_dataset_model, check_model, check_dataset, ModelRequirements, DynamicDataset



app = FastAPI()

datasets_storage: Dict[str, Union[DynamicDataset, uuid.UUID]] = {}
dataset_list = []

uuid_generator_data = generate_uuid()

###########
# DATASET #
###########

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


##########
# MODELS #
##########

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
