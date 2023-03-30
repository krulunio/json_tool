import json
import os


def find_missing_keys(template_file, input_file):
    missing_keys = []
    for key in template_file.keys():
        if not(key in input_file.keys()):
            missing_keys.append(key)
    return missing_keys


def add_missing_keys(template_file, input_file, missing_keys, default_value):
    output_object = {}
    for key in template_file.keys():
        if key in missing_keys:
            output_object[key] = default_value
        else:
            output_object[key] = input_file[key]
    return output_object


def set_all_to_default(template_file, default_value):
    for key in template_file.keys():
        template_file[key] = default_value
    return template_file


def run(config_file):
    for config_group in json.load(open(config_file, "r"))["config_groups"]:
        template_file = json.load(open(config_group["template_file"], "r"))
        input_file = json.load(open(config_group["input_file"], "r"))
        output_file = {}
        missing_keys = find_missing_keys(template_file, input_file)
        match config_group["action"]:
            case "add_missing_keys":
                output_file = add_missing_keys(template_file, input_file, missing_keys, config_group["default_value"])
            case "set_all_to_default":
                output_file = set_all_to_default(template_file, config_group["default_value"])
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(output_file, open(config_group["output_file"], "w"), indent="\t")
    print("Done adding missing!")
