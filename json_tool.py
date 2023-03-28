import json
import src.find_missing as find_missing
import src.find_duplicates as find_duplicates
import src.replace_values as replace_values

for config_group in json.load(open("config/config_groups.json"))["config_groups"]:
    find_missing.run(config_group["find_missing"])
    find_duplicates.run(config_group["find_duplicates"])
    replace_values.run(config_group["replace_values"])
