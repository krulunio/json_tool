import json
import os


def check_dict(default_value, name, key):
    try:
        return name[key]
    except:
        return default_value


def find_missing_keys(template_file, input_file):
    missing_keys = []
    for key in template_file.keys():
        if not(key in input_file.keys()):
            missing_keys.append(key)
    return missing_keys


def add_missing_keys(template_file, input_file, default_value):
    for key in template_file.keys():
        if key in find_missing_keys(template_file, input_file):
            input_file[key] = default_value
    return input_file


def add_missing_values(template_file, input_file, default_value):
    for key, value in input_file.items():
        if value == default_value:
            input_file[key] = template_file[key]
    return input_file


def set_all_to_default(template_file, default_value):
    for key in template_file.keys():
        template_file[key] = default_value
    return template_file


def load_input_file(file_name, key_root):
    input_file = json.load(open(file_name, "r"))
    input_keys = [
        key
        for key in input_file.keys()
        if key.startswith(key_root)
    ]
    filtered_input_file = {
        key: input_file.items()[key]
        for key in input_keys
    }
    return filtered_input_file


def run(config_file):
    for config_group in json.load(open(config_file, "r")).values():
        template_file = json.load(open(config_group["template_file"], "r"))
        output_file = {}

        match config_group["action"]:
            case "add_missing_keys":
                input_file = json.load(open(config_group["input_file"], "r"))
                output_file = add_missing_keys(template_file, input_file, config_group["default_value"])
            case "add_missing_values":
                input_file = json.load(open(config_group["input_file"], "r"))
                output_file = add_missing_values(template_file, input_file, config_group["default_value"])
            case "set_all_to_default":
                output_file = set_all_to_default(template_file, config_group["default_value"])
        os.makedirs("./"+os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(output_file, open(config_group["output_file"], "w"), indent="\t")
