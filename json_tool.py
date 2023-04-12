import json
import src.replace_values
import src.add_missing
import src.find_missing
import src.find_duplicates
import src.add_from_file

functions = {
    "replace_values": src.replace_values.run,
    "add_missing": src.add_missing.run,
    "find_missing": src.find_missing.run,
    "find_duplicates": src.find_duplicates.run,
    "add_from_file": src.add_from_file.run
}


def run_functions():
    for config_filename in config_group[config_key]:
        functions[config_key](config_filename)


for config_group_key, config_group in json.load(open("main_config.json")).items():
    for config_key in config_group.keys():
        run_functions()
        print("Finished '{}' functions.".format(config_key))
    print("Finished '{}' group.".format(config_group_key))
print("Finished all groups.")
