import json

def load_json(filename: str) -> dict:
    with open(filename, "r") as file:
        data = json.load(file)
    return data

def get_api_token(filename: str) -> str:
    data = load_json(filename)
    return data["access_token"]
