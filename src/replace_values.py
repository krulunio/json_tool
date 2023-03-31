import json
import os


def resolve_tags(values_and_tags, tags):
    try:
        values_list = []
        for value_or_tag in values_and_tags:
            if value_or_tag[0] == '#':
                for value_from_tag in tags[value_or_tag[1:]]:
                    values_list.append(value_from_tag)
            else:
                values_list.append(value_or_tag)
        return values_list
    except:
        return []


def check_exclusions(key_parts, exclusions):
    for key_part in key_parts:
        if key_part in exclusions:
            return True
    return False


def check_inclusions(key_parts, inclusions):
    for inclusion in inclusions:
        if inclusion not in key_parts:
            return False
    return True


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


def parse_patterns(loaded_patterns, tags, current_key, current_value):
    output_value = current_value
    for current_pattern in loaded_patterns:
        key_parts = current_key.split(".")[-1].split("_")
        inclusions = resolve_tags(current_pattern["inclusions"], tags)
        try:
            exclusions = resolve_tags(current_pattern["exclusions"], tags)
        except:
            exclusions = []
        if check_inclusions(key_parts, inclusions) and not check_exclusions(key_parts, exclusions):
            output_value = parse_action(current_pattern, output_value)
    return output_value


def run(config_file):
    for config_group in json.load(open(config_file, "r")).values():
        pattern_file = json.load(open(config_group["pattern_file"], "r"))
        key_root = pattern_file["key_root"]
        loaded_patterns = pattern_file["patterns"]
        input_file = json.load(open(config_group["input_file"], "r"))
        output_object = {}
        for key, value in input_file.items():
            output_object[key] = value
            if key.startswith(key_root):
                output_object[key] = parse_patterns(loaded_patterns, pattern_file["tags"], key, value)
        os.makedirs(os.path.dirname(config_group["output_file"]), exist_ok=True)
        json.dump(output_object, open(config_group["output_file"], "w"), indent="\t")
