import json
import os


def check_dict(default_value, name, key):
    try:
        return name[key]
    except KeyError:
        return default_value


def resolve_tags(values_and_tags, tags):
    values_list = []
    for value_or_tag in values_and_tags:
        if value_or_tag[0] == '#':
            for value_from_tag in tags[value_or_tag[1:]]:
                values_list.append(value_from_tag)
        else:
            values_list.append(value_or_tag)
    return values_list


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
            return current_pattern["value"] + check_dict("", current_pattern, "separator") + current_output
        case "end":
            return current_output + check_dict("", current_pattern, "separator") + current_pattern["value"]
        case "replace":
            return current_output.replace(current_pattern["replace_what"], current_pattern["replace_with"])
    raise ValueError("No action named '{}'!".format(current_pattern["action"]))


def parse_patterns(loaded_patterns, tags, current_key, current_value):
    output_value = current_value
    for current_pattern in loaded_patterns:
        key_parts = current_key.split(".")[-1].split("_")
        inclusions = resolve_tags(current_pattern["inclusions"], tags)
        exclusions = check_dict([], current_pattern, "exclusions")
        exclusions = resolve_tags(exclusions, tags)
        if check_inclusions(key_parts, inclusions) and not check_exclusions(key_parts, exclusions):
            output_value = parse_action(current_pattern, output_value)
    return output_value


def default_try_except(config_groups):
    try:
        default_group = config_groups.pop("@default")
        try:
            default_group["io_path"]
        except KeyError:
            default_group["io_path"] = "."
        try:
            default_group["pattern_path"]
        except KeyError:
            default_group["pattern_path"] = "."
    except KeyError:
        default_group = {
            "io_path": ".",
            "pattern_path": "."
        }
    return default_group


def config_try_except(config_name, config_group, default_group):
    try:
        config_group["pattern_file"] = default_group["pattern_path"] + '/' + config_group["pattern_file"]
    except TypeError:
        config_group = {"pattern_file": default_group["pattern_path"] + '/' + config_group}
    except KeyError:
        raise KeyError("Missing 'pattern_file' in '"+config_name+"' group!")

    try:
        config_group["input_file"] = default_group["io_path"] + '/' + config_group["input_file"]
    except (KeyError, TypeError):
        try:
            config_group["input_file"] = default_group["io_path"] + '/' + default_group["input_file"]
        except KeyError:
            raise KeyError("Missing 'input_file' in '" + config_name + "' group!")

    try:
        config_group["output_file"] = default_group["io_path"] + '/' + config_group["output_file"]
    except (KeyError, TypeError):
        try:
            config_group["output_file"] = default_group["io_path"] + '/' + default_group["output_file"]
        except KeyError:
            raise KeyError("Missing 'output_file' in '" + config_name + "' group!")

    return config_group


def run(config_file):
    config_groups = json.load(open(config_file, "r"))
    default_group = default_try_except(config_groups)

    for config_name, config_group in config_groups.items():
        config_group = config_try_except(config_name, config_group, default_group)

        pattern_file = json.load(open(config_group["pattern_file"], "r"))
        input_file = json.load(open(config_group["input_file"], "r"))
        output_file = config_group["output_file"]

        key_root = check_dict("", pattern_file, "key_root")
        tags = check_dict({}, pattern_file, "tags")
        output_object = {}
        for key, value in input_file.items():
            output_object[key] = value
            if key.startswith(key_root):
                output_object[key] = parse_patterns(pattern_file["patterns"], tags, key, value)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        json.dump(output_object, open(output_file, "w"), indent="\t")
