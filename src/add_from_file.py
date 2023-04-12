import json
import os


def set_pairs_from_file(input_file, pairs_file):
    missing_keys = []
    for key, value in pairs_file.items():
        if key in input_file.keys():
            input_file[key] = value
        else:
            missing_keys.append(key)
    if len(missing_keys) == 0:
        return {"missing_keys": "No missing keys found"}
    else:
        return {"missing_keys": missing_keys}


def run(config_file):
    for config_group in json.load(open(config_file, "r")).values():
        input_file = json.load(open(config_group["input_file"], "r"))
        pairs_file = json.load(open(config_group["pairs_file"], "r"))
        missing_file = {}
        match config_group["action"]:
            case "set_pairs_from_file":
                missing_file = set_pairs_from_file(input_file, pairs_file)
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(input_file, open(config_group["output_file"], "w"), indent="\t")
        os.makedirs(os.path.dirname(config_group["missing_file"]), exist_ok=True)
        json.dump(missing_file, open(config_group["missing_file"], "w"), indent="\t")
