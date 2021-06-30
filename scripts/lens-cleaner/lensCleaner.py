import os
import pandas as pd
import argparse
import re
import nltk
import ast
import string
import json

# Global Variables
stopwords = nltk.corpus.stopwords.words('english')
special_characters = string.punctuation


def get_arg_parser():
    """Allows arguments to be passed into this program through the terminal.
    Returns:
        argeparse.ArgumentParser: Object containing selected options
    """

    def dir_path(string):
        if os.path.isfile(string):
            return string
        else:
            raise NotADirectoryError(string)

    def formatting_type(string):
        if string.lower() in ["leaf", "all"]:
            return string.lower()
        else:
            raise parser.error("Bad Argument: {}\nAcceptable options: leaf, all".format(string))

    parser = argparse.ArgumentParser(
        description="This script will take our labeled_data and a lens_output file and create a MATCH friendly paper output file.")
    parser.add_argument("type", help="Argument indicating what kind of labels should be included in the final output.\nAccepts: leaf, all",
                        type=formatting_type)
    parser.add_argument("--json_path", "-jp", help="Full path to Lens JSON output file: C:\..\..\lens_output.json",
                        default="./lens_output.json", type=dir_path)
    parser.add_argument("--csv_path", "-cp", help="Full path to CSV labeled file: C:\..\..\labeled_data.csv",
                        default="./labeled_data.csv", type=dir_path)
    return parser


def get_all_labels(labeled_data: pd.DataFrame, merged_data: list):
    """Merges all of the levels of labels from our labeled data into a single list and appends it to the reference of a list.
    Args:
        args (labeled_data): Dataframe of our labeled data read from a csv.
        args (merged_data): A list which will have a single list per paper appended to it.
    Returns:
        None
    """

    for index, row in labeled_data.iterrows():

        merged_labels = [*ast.literal_eval(row["label_level_1"] if type(row["label_level_1"]) == str else '[]'),
                         *ast.literal_eval(row["label_level_2"]
                                           if type(row["label_level_2"]) == str else '[]'),
                         *ast.literal_eval(row["label_level_3"] if type(row["label_level_3"]) == str else '[]')
                         ]
        merged_data.append(merged_labels)
    return


def get_leaf_labels(labeled_data: pd.DataFrame, merged_data: list):
    """Takes only the leaf list of labels from our labeled data and appends it to the reference of a list.
    Args:
        args (labeled_data): Dataframe of our labeled data read from a csv.
        args (merged_data): A list which will have a single list per paper appended to it.
    Returns:
        None
    """

    for index, row in labeled_data.iterrows():
        if (not pd.isna(row["label_level_3"])):
            merged_data.append(ast.literal_eval(row["label_level_3"]))
        else:
            merged_data.append(ast.literal_eval(row["label_level_2"]))
    return


def load_csv(csv_path: str, format_type: str):
    """Loads in labeled csv data, pulls the title and labels out and creates a dataframe.
    Args:
        args (csv_path): Path of the csv file.
        args (format_type): A string dictating what kind of labels should the parser include in its output.
    Returns:
        pandas.Dataframe: A dataframe consisting of only titles and labels.
    """
    labeled_data = pd.read_csv(csv_path)
    merged_data = []

    if (format_type == "all"):
        get_all_labels(labeled_data, merged_data)

    elif (format_type == "leaf"):
        get_leaf_labels(labeled_data, merged_data)

    merged_dataframe = pd.DataFrame(data={"label": merged_data})
    merged_dataframe["title"] = labeled_data["title"]
    merged_dataframe["doi"] = labeled_data["doi"].str.lower()
    return merged_dataframe


def load_lens_json(lens_output_path: str):
    """Loads in JSON data pulled from the Lens API.
    Args:
        args (lens_output_path): Path of the JSON file.
    Returns:
        dict: A dictionary representing the JSON file.
    """

    with open(lens_output_path, 'r', encoding='cp866') as json_file:
        data = json.load(json_file)
        json_file.close()
    return data


def clean_text(text: str):
    """Tokenizes and cleans text: removes special characters, stopwords and sets text to lowercase.
    Args:
        args (text): Text which needs tokenizing.
    Returns:
        list: A list of cleaned, tokenized words.
    """

    tokenized_text = nltk.tokenize.word_tokenize(text)
    cleaned_text = [text.lower(
    ) for text in tokenized_text if text not in special_characters and text not in stopwords]
    return cleaned_text


def clean_lens_json(lens_output: dict, labeled_dataframe: pd.DataFrame):
    """Takes a Lens output JSON file and reformats it to be MATCH friendly, while pulling labels from our csv.
    Args:
        args (lens_output): Dictionary representing the Lens JSON file.
        args (labeled_dataframe): Dataframe representing the labeled csv containing titles and labels
    Returns:
        list: A list containing the reformated JSON data.
    """

    def find_labels(column_name: str, comparison_tag: str):
        temp_list = labeled_dataframe["label"].loc[labeled_dataframe[column_name]
                                                   == comparison_tag].tolist()

        label_list = [re.sub("\s", "_", label).lower()
                      for label in temp_list[0]] if len(temp_list) else []

        return label_list

    cleaned_papers = []
    amount_of_rows = len(lens_output['data'])
    amount_done = 0

    for paper in lens_output["data"]:

        paper_object = {}
        # Paper = Lens_id
        paper_object["paper"] = paper.get("lens_id", "")

        # Mag = Fields of study
        paper_object["mag"] = [re.sub("\s", "_", field).lower(
        ) for field in paper.get("fields_of_study", [])]

        # Mesh = Mesh_ids
        paper_object["mesh"] = paper.get("mesh_terms", []) and \
            [mesh_term["mesh_id"]
                for mesh_term in paper["mesh_terms"] if mesh_term.get("mesh_id", None)]

        # Venue - Source Title
        paper_object["venue"] = paper.get("source", "") and \
            paper["source"].get("title", "")

        # Author - MAGIDs
        try:
            paper_object["author"] = paper.get("authors", []) and \
                [author_id[0]["value"] for author_id in [author.get(
                    "ids", []) for author in paper["authors"]] if author_id[0].get("type", "") == "magid"]
        except:
            paper_object["author"] = []

        # Reference - Lens_ids
        paper_object["reference"] = paper.get("references", []) and \
            [reference_object["lens_id"]
                for reference_object in paper["references"]]

        # Scholarly Citations - Scholarly Citations
        paper_object["scholarly_citations"] = paper.get(
            "scholarly_citations", [])

        # Text - title + abstract
        title_abstract_text = " ".join(
            [paper.get("title", ""), paper.get("abstract", "")])
        paper_object["text"] = " ".join(clean_text(title_abstract_text))

        # Extract DOI
        paper_dois = []
        for external_id in paper.get("external_ids", []):
            if (external_id["type"] == "doi"):
                paper_dois.append(external_id["value"])

        # Label - Biomimicry functions

        try:
            if (len(paper_dois)):
                for paper_doi in paper_dois:
                    label_list = find_labels("doi", paper_doi)

                    if (len(label_list) == 0):
                        label_list = find_labels(
                            "title", paper.get("title", ""))
                    else:
                        break

            else:
                label_list = find_labels("title", paper.get("title", ""))

            paper_object["label"] = label_list

        except:
            paper_object["label"] = []

        cleaned_papers.append(paper_object)
        amount_done += 1
        print("Progress Completed = {0:.0%}".format(
            amount_done/amount_of_rows), end='\r')

    return cleaned_papers


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    labeled_dataframe = load_csv(args.csv_path, args.type)
    json_dict = load_lens_json(args.json_path)
    cleaned_json_list = clean_lens_json(json_dict, labeled_dataframe)

    with open("cleaned_lens_output.json", "w") as cleaned_json:
        count = 1
        list_size = len(cleaned_json_list)

        for row in cleaned_json_list:
            print("Progress of JSON Write Completed = {0:.0%}".format(
                count/list_size), end='\r')
            cleaned_json.write(json.dumps(row))
            if(count < list_size):
                cleaned_json.write("\n")
            count += 1
        cleaned_json.close()
