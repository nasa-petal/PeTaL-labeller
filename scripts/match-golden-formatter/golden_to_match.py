import json
import re
import argparse
import os

def get_args():
    """Allows arguments to be passed into this program through the terminal.
    Returns:
        argparse.Namespace: Object containing selected options
    """
    def is_file(string: str):
        if os.path.isfile(string):
            return string
        else:
            raise

    parser = argparse.ArgumentParser(description="Formatter to convert the Golden JSON into a MATCH friendly format.")
    parser.add_argument("input_file", type=is_file, help="The full or relative path to the golden.json file.")
    parser.add_argument("output_file_name", type=str, help="The name of the output file")

    return parser.parse_args()


def load_json(input_file: str):
    """ Loads in the golden JSON file as a list of dictionaries.
    Args:
        input_file : str
            The full or relative path of the golden JSON file.
    Returns:
        list
            List of objects containing papers from our dataset.
    """

    golden_json_strings = []
    
    with open(input_file, "r") as golden_json_file:
        for line in golden_json_file:
            golden_json_strings.append(line)
        golden_json_file.close()

    golden_jsons = [json.loads(re.sub(r"(\n)*(\t)*", "", json_elem)[:-1]) for json_elem in golden_json_strings[1:-3]]
    return golden_jsons


def convert_golden(golden_jsons: list):
    """ Reformats the golden JSON list into a MATCH friendly list.
    Args:
        golden_jsons : list
            A list of dictionaries containing paper information.
    Returns:
        list
            List of objects containing papers with MATCH friendly content and fields.
    """

    for index in range(len(golden_jsons)):
        golden_jsons[index]["text"] = list(set(golden_jsons[index].pop("title") + golden_jsons[index].pop("abstract")))
        golden_jsons[index]["text"] = [text for text in golden_jsons[index]["text"] if text != ""]
        venue_type = "venue_mag" if len(golden_jsons[index]["venue_mag"]) else "venue"
        venues = [re.sub(r"\s", "_", venue).lower() for venue in golden_jsons[index][venue_type] if len(golden_jsons[index][venue_type])]
        golden_jsons[index]["venue"] = venues
        golden_jsons[index].pop("venue_mag")

    return golden_jsons
    

def save_match(match_jsons: list, output_name: str):
    """ Saves MATCH list in a JSON newline delimited format.
    Args:
        match_jsons : list
            A list of objects containing papers which have been formatted for MATCH.
        output_name : str
            A string corresponding to the name of the file that will be saved.
    """

    with open(f"{output_name}.json", "w") as match_input:
        count = 1
        list_size = len(match_jsons)

        for row in match_jsons:
            print("Progress of JSON Write Completed = {0:.0%}".format(count/list_size), end = '\r')
            match_input.write(json.dumps(row))
            if(count < list_size):
                match_input.write("\n")
            count += 1
        match_input.close()


if __name__ == "__main__":
    args = get_args()
    golden_json = load_json(args.input_file)
    match_jsons = convert_golden(golden_json)
    save_match(match_jsons, args.output_file_name)