import json
import os


def remove_unique(checked_pairs):
    unique = [
        key
        for key, value in checked_pairs.items()
        if value == 1
    ]
    for key in unique:
        del checked_pairs[key]


def find_duplicate_keys(checked_file):
    duplicates = {}
    for key, value in checked_file:
        if key in duplicates:
            duplicates[key] += 1
        else:
            duplicates[key] = 1
    remove_unique(duplicates)
    if duplicates == {}:
        return {"keys": "No duplicate keys found."}
    else:
        return {"keys": duplicates}


def find_duplicate_values(checked_file):
    duplicates = {}
    for key, value in checked_file:
        if value in duplicates:
            duplicates[value] += 1
        else:
            duplicates[value] = 1
    remove_unique(duplicates)
    if duplicates == {}:
        return {"values": "No duplicate values found."}
    else:
        return {"values": duplicates}


def run(config_file):
    for config_group in json.load(open(config_file, "r"))["config_groups"]:
        duplicates = {}
        match config_group["action"]:
            case "keys":
                duplicates = json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_duplicate_keys)
            case "values":
                duplicates = json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_duplicate_values)
            case "both":
                duplicates.update(json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_duplicate_keys))
                duplicates.update(json.load(open(config_group["input_file"], "r"), object_pairs_hook=find_duplicate_values))
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(duplicates, open(config_group["output_file"], "w"), indent="\t")
    print("Done finding duplicates!")
