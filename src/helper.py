import json
from typing import List
from haystack import Pipeline

def load_json(filename: str) -> dict:
    with open(filename, "r") as file:
        data = json.load(file)
    return data

def get_api_token(filename: str) -> str:
    data = load_json(filename)
    return data["access_token"]

def print_pretty_results(question:List, responses:List, show_meta_data:bool = False) -> None:
    # check if question and reponses is a list 
    if not isinstance(question, list): question = [question]
    if not isinstance(responses, list): responses = [responses]

    assert len(question) == len(responses), "Length of question and responses must be the same"

    # zip question and responses together
    for q, response in zip(question, responses):
        print("Question:", q)
        print("Answer:", response["generator"]["replies"][0])
        if show_meta_data:
            print("Context:", response["generator"]["meta"][0])
        print("\n", "\n")

def output_pipeline_as_yaml(pipeline:Pipeline, filename:str) -> None:
    with open(filename, "w") as f:
        f.write(pipeline.dumps())

