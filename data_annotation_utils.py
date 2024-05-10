from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, PositiveInt, PositiveFloat
from typing import List, Dict, Union
#from typeguard import check_type
import uuid
import json
import numpy as np

class DynamicDataset(BaseModel):
    data : Dict[str, Dict[str, List[Union[str, int, float, bool]]]]

#class DynamicDataset(BaseModel):
#    metadata: Dict[str, List[Union[str, int, float, bool]]]
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
                    model_value = MR['model'][tab][key][0]
                    data_value = DD['data'][tab][key][0]
                    type_name = type(MR['model'][tab][key][0])
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
