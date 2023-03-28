import json


def parse_action(current_pattern, current_output):
    match current_pattern["action"]:
        case "base":
            return current_pattern["value"]
        case "begin":
            return current_pattern["value"] + current_pattern["separator"] + current_output
        case "end":
            return current_output + current_pattern["separator"] + current_pattern["value"]
        case "replace":
            return current_output.replace(current_pattern["replace_what"], current_pattern["replace_with"])
    return current_output


def parse_patterns(loaded_patterns, current_key, current_value):
    output_value = current_value
    for current_pattern in loaded_patterns:
        key_parts = current_key.split(".")[-1].split("_")
        if current_pattern["key_part"] in key_parts:
            output_value = parse_action(current_pattern, output_value)
    return output_value


def run(config_file):
    for config_group in json.load(open(config_file, "r"))["config_groups"]:
        pattern_file = json.load(open(config_group["pattern_file"], "r"))
        key_root = pattern_file["key_root"]
        loaded_patterns = pattern_file["patterns"]
        input_file = json.load(open(config_group["input_file"], "r"))
        output_object = {}
        for key, value in input_file.items():
            output_object[key] = value
            if key.startswith(key_root):
                output_object[key] = parse_patterns(loaded_patterns, key, value)
        json.dump(output_object, open(config_group["output_file"], "w"), indent="\t")
    print("Done replacing values!")
