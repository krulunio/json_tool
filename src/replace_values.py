import json
import os

actions_dictionary = {
    "base": lambda new_value, current_value: new_value,
    "begin": lambda new_value, current_value: new_value + current_value,
    "end": lambda new_value, current_value: current_value + new_value
}

complex_actions_dictionary = {
    "replace": lambda new_value, current_value, old_value: current_value.replace(old_value, new_value)
}


def resolve_config_file_string(general_config, file_path, file_type):
    try:
        general_config[file_type] = general_config[file_path] + '/' + general_config[file_type]
    except (KeyError, TypeError):
        try:
            general_config[file_type] = general_config[file_path] + '/' + general_config[file_type]
        except KeyError:
            raise KeyError("Missing '" + file_type + "' in '" + general_config["config_name"] + "' file!")


def check_general_config(general_config):
    general_config["io_path"] = check_dictionary(".", general_config, "io_path")
    general_config["pattern_path"] = check_dictionary(".", general_config, "pattern_path")

    resolve_config_file_string(general_config, "io_path", "input_file")
    resolve_config_file_string(general_config, "io_path", "output_file")

    try:
        if type(general_config["pattern_files"]) != list:
            raise TypeError("Missing 'pattern_files' in '" + general_config["config_name"] + "' file!")
    except KeyError:
        raise KeyError("Missing 'pattern_files' in '" + general_config["config_name"] + "' file!")


def check_dictionary(default_value, name, key):
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


def check_exclusions(key, exclusions):
    for exclusion in exclusions:
        if exclusion in key:
            return False
    return True


def check_inclusions(key, inclusions):
    for inclusion in inclusions:
        if inclusion not in key:
            return False
    return True


def check_key_requirements(key, key_requirements):
    return (
        check_exclusions(key, key_requirements["exclusions"]) and
        check_inclusions(key, key_requirements["inclusions"]) and
        key.startswith(key_requirements["key_root"]) and
        key.endswith(key_requirements["key_leaf"])
    )


def get_key_requirements_from_pattern(current_pattern, pattern_file_data):
    return {
        "inclusions": resolve_tags(check_dictionary([], current_pattern, "inclusions"), pattern_file_data["tags"]),
        "exclusions": resolve_tags(check_dictionary([], current_pattern, "exclusions"), pattern_file_data["tags"]),
        "key_root": "",
        "key_leaf": ""
    }


def parse_reduced_action(action, current_key, current_value, reduced_patterns_dictionary):
    if check_dictionary(False, actions_dictionary, action):
        for checked_value, new_value in reduced_patterns_dictionary.items():
            if checked_value in current_key:
                current_value = actions_dictionary[action](new_value, current_value)
    elif check_dictionary(False, complex_actions_dictionary, action):
        for old_value, new_value in reduced_patterns_dictionary.items():
            current_value = complex_actions_dictionary[action](new_value, current_value, old_value)
    else:
        raise ValueError("No action named '{}'!".format(action))
    return current_value


def parse_action(current_pattern, current_value):
    try:
        match current_pattern["action"]:
            case "base": return actions_dictionary["base"](current_pattern["value"], None)
            case "begin": return actions_dictionary["begin"](current_pattern["value"], (check_dictionary("", current_pattern, "separator") + current_value))
            case "end": return actions_dictionary["end"](current_pattern["value"], (current_value + check_dictionary("", current_pattern, "separator")))
            case "replace": return complex_actions_dictionary["replace"](current_value, current_pattern["replace_what"], current_pattern["replace_with"])
    except KeyError:
        raise ValueError("No action named '{}'!".format(current_pattern["action"]))


def parse_reduced_patterns(pattern_file_data, io_data, current_key):
    for action, reduced_patterns_dictionary in pattern_file_data["reduced_patterns"].items():
        io_data["output_data"][current_key] = parse_reduced_action(action, current_key, io_data["output_data"][current_key], reduced_patterns_dictionary)


def parse_patterns(pattern_file_data, io_data, current_key):
    for current_pattern in pattern_file_data["patterns"]:
        if check_key_requirements(current_key, get_key_requirements_from_pattern(current_pattern, pattern_file_data)):
            io_data["output_data"][current_key] = parse_action(current_pattern, io_data["output_data"][current_key])


def load_pattern_file_data(pattern_path, pattern_file):
    tmp_pattern_file_data = json.load(open(pattern_path + '/' + pattern_file, "r"))
    tmp_tags = check_dictionary({}, tmp_pattern_file_data, "tags")
    return {
        "pattern_file": pattern_file,
        "key_root": check_dictionary("", tmp_pattern_file_data, "key_root"),
        "key_leaf": check_dictionary("", tmp_pattern_file_data, "key_leaf"),
        "inclusions": resolve_tags(check_dictionary("", tmp_pattern_file_data, "inclusions"), tmp_tags),
        "exclusions": resolve_tags(check_dictionary("", tmp_pattern_file_data, "exclusions"), tmp_tags),
        "tags": tmp_tags,
        "reduced_patterns": check_dictionary({}, tmp_pattern_file_data, "reduced_patterns"),
        "patterns": check_dictionary({}, tmp_pattern_file_data, "patterns")
    }


def load_io_data(input_file):
    return {
        "input_data": json.load(open(input_file, "r")),
        "output_data": {}
    }


def replace_values(pattern_file_data, io_data):
    for key, value in io_data["input_data"].items():
        io_data["output_data"][key] = value
        if check_key_requirements(key, pattern_file_data):
            parse_reduced_patterns(pattern_file_data, io_data, key)
            parse_patterns(pattern_file_data, io_data, key)


def run(config_file):
    general_config = json.load(open(config_file, "r"))
    general_config["config_name"] = config_file
    check_general_config(general_config)

    for pattern_file in general_config["pattern_files"]:
        pattern_file_data = load_pattern_file_data(general_config["pattern_path"], pattern_file)
        io_data = load_io_data(general_config["input_file"])
        replace_values(pattern_file_data, io_data)
        os.makedirs(os.path.dirname(general_config["output_file"]), exist_ok=True)
        json.dump(io_data["output_data"], open(general_config["output_file"], "w"), indent="\t")
