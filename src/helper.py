import json

def load_json(filename: str) -> dict:
    with open(filename, "r") as file:
        data = json.load(file)
    return data