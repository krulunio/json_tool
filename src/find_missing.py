import json
import os


def find_missing_keys(checked_file):
    for checked_key in checked_file.keys():
        template_file.pop(checked_key, None)
    missing_keys = list(template_file.keys())
    if len(missing_keys) == 0:
        return {"missing_keys": "No missing keys found"}
    else:
        return {"missing_keys": missing_keys}


def find_missing_values(checked_file):
    missing_values = []
    for key, value in checked_file:
        if value == "":
            missing_values.append(key)
    if len(missing_values) == 0:
        return {"missing_values": "No missing values found"}
    else:
        return {"missing_values": missing_values}


def run(config_file):
    for config_group in json.load(open(config_file, "r"))["config_groups"]:
        global template_file
        template_file = json.load(open(config_group["template_file"], "r"))
        missing = {}
        match config_group["action"]:
            case "keys":
                missing = json.load(open(config_group["input_file"], "r"), object_hook=find_missing_keys)
            case "values":
                missing = json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_missing_values)
            case "both":
                missing.update(json.load(open(config_group["input_file"], "r"), object_hook=find_missing_keys))
                missing.update(json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_missing_values))
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(missing, open(config_group["output_file"], "w"), indent="\t")
    print("Done finding missing!")
