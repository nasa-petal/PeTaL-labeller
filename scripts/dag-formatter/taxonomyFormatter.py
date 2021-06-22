import os
import pandas as pd
import argparse
import re


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

    parser = argparse.ArgumentParser(description="Input csv file path")
    parser.add_argument("--csv_path", "-cp", help="Full path to CSV taxonomy file: C:\..\..\taxonomy.csv",
                        default="./taxonomy.csv", type=dir_path)
    return parser


def get_children(row_index: int, column_index: int, csv: pd.DataFrame):
    """Takes a Dataframe where each column is a deeper level in a DAG structure 
    and creates a list of lists representing the structure.
    Args:
        args (row_index): An integer representing the current row's index
        args (column_index): An integet representing the current column's index
        args (csv): Dataframe representing the taxonomy csv containing different levels of biomimicry functions
    Returns:
        list: A list of lists containing a parent label and its children.
    """
    parent_column = csv[csv.columns[column_index]]
    current_row = row_index
    csv_rows = csv.shape[0]
    validation_array = [parent_column[row_index], False]
    parent_list = [re.sub("\s", "_", parent_column[row_index]).lower()]
    full_list = [parent_list]

    if (len(csv.columns) <= column_index + 1 or not csv[csv.columns[column_index + 1]][row_index]):
        return []

    child_column = csv[csv.columns[column_index + 1]]

    # Recursively pull out all nested children
    while (current_row < csv_rows and parent_column[current_row] in validation_array):
        if (child_column[current_row]):
            parent_list.append(
                re.sub("\s", "_", child_column[current_row]).lower())
            sub_list = get_children(current_row, column_index + 1, csv)
            if (len(sub_list)):
                full_list += sub_list
        current_row += 1

    return full_list


def parse_csv(csv: pd.DataFrame):
    """When given a taxonomy csv read in to a dataframe, this will iterate through each row and extract all of the nested children assuming each column represents
    a deeper level to a DAG structure.
    Args:
        args (csv): Dataframe representing the taxonomy csv containing different levels of biomimicry functions
    Returns:
        list: A single list containing strings of parent/children relationships.
    """
    csv_row_length = csv.shape[0]
    csv_base_column = csv[csv.columns[0]]
    dag_list = []

    for i in range(csv_row_length):
        if (csv_base_column[i]):
            row_list = get_children(i, 0, csv)
            if (len(row_list)):
                stringified_list = [" ".join(sub_list)
                                    for sub_list in row_list if len(sub_list)]
                dag_list += stringified_list
    return dag_list


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()
    taxonomy_csv = pd.read_csv(args.csv_path).fillna(False)
    dag_list = parse_csv(taxonomy_csv)

    with open("taxonomy.txt", "w") as taxonomy_text:
        count = 1
        list_size = len(dag_list)

        for row in dag_list:
            print("Progress of JSON Write Completed = {0:.0%}".format(
                count/list_size), end='\r')
            taxonomy_text.write(row)
            if(count < list_size):
                taxonomy_text.write("\n")
            count += 1
        taxonomy_text.close()
