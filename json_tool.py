import json
import src.tool_functions.replace_values
import src.tool_functions.add_missing
import src.tool_functions.find_missing
import src.tool_functions.find_duplicates
import src.tool_functions.add_from_file

main_config_paths = [
    "main_config.json",
    "../main_config.json"
]

json_tool_functions = {
    "replace_values": src.tool_functions.replace_values.run,
    "add_missing": src.tool_functions.add_missing.run,
    "find_missing": src.tool_functions.find_missing.run,
    "find_duplicates": src.tool_functions.find_duplicates.run,
    "add_from_file": src.tool_functions.add_from_file.run
}


def try_to_load_main_config(main_config_path):
    try:
        return json.load(open(main_config_path)).items()
    except FileNotFoundError:
        return None


def load_main_config():
    for main_config_path in main_config_paths:
        main_config = try_to_load_main_config(main_config_path)
        if main_config is not None:
            return main_config
    raise FileNotFoundError("Missing 'main_config.json' file!")


def run():
    main_config = load_main_config()
    for config_group_key, config_group in main_config:
        for config_key in config_group.keys():
            for config_filename in config_group[config_key]:
                json_tool_functions[config_key](config_filename)
            print("Finished '"+config_key+"' functions.")
        print("Finished '"+config_group_key+"' group.")
    print("Finished all groups.")


run()
