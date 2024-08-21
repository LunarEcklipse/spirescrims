import json

api_kv_dict = None

# Get the directory this script is in
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
json_path = os.path.join(dir_path, "api_kv_conversion.json")
new_json_path = os.path.join(dir_path, "api_kv_conversion_new.json")

with open(json_path, "r", encoding="utf-8") as f:
    api_kv_dict = json.loads(f.read())

new_dict = {"weapons": {}, "passives": {}, "actives": {}}
for key in api_kv_dict["weapons"]:
    new_dict["weapons"][key] = api_kv_dict["weapons"][key]["n"]
for key in api_kv_dict["passives"]:
    new_dict["passives"][key] = api_kv_dict["passives"][key]["n"]
for key in api_kv_dict["actives"]:
    new_dict["actives"][key] = api_kv_dict["actives"][key]["n"]

with open(json_path, "w") as f:
    json.dump(new_dict, f, indent=4)
