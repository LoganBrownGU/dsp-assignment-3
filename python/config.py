import json

def read_config(): 
    with open("assets/config.json") as f:
        json_data = json.loads(f.read())
        return json_data["baud"], json_data["f1"], json_data["f2"]
    
    raise Exception("Error parsing config")
