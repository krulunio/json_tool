import json
import os


def get_exclusions(current_pattern, exclusion_tags):
    try:
        exclusion_list = []
        for exclusion in current_pattern["exclusions"]:
            if exclusion[0] == '#':
                for exclusion_from_tag in exclusion_tags[exclusion[1:]]:
                    exclusion_list.append(exclusion_from_tag)
            else:
                exclusion_list.append(exclusion)
        return exclusion_list
    except:
        return []


def check_exclusions(key_parts, exclusions):
    for key_part in key_parts:
        if key_part in exclusions:
            return True
    return False


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


def parse_patterns(loaded_patterns, exclusion_tags, current_key, current_value):
    output_value = current_value
    for current_pattern in loaded_patterns:
        key_parts = current_key.split(".")[-1].split("_")
        exclusions = get_exclusions(current_pattern, exclusion_tags)
        if (current_pattern["key_part"] in key_parts) and not check_exclusions(key_parts, exclusions):
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
                output_object[key] = parse_patterns(loaded_patterns, pattern_file["exclusion_tags"], key, value)
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(output_object, open(config_group["output_file"], "w"), indent="\t")
