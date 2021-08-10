'''
	utils.py

    Run MATCH with PeTaL data.
    Last modified on 9 August 2021.

	Authors: Eric Kong (eric.l.kong@nasa.gov, erickongl@gmail.com)
'''

def extract_labels(js):
    """Extracts list of labels from a JSON object representing a paper.

    Args:
        js (dict): JSON object representing a paper in the PeTaL golden dataset.

    Returns:
        List(str): all of its labels concatenated into a single list
    """
    
    level1labels = js['level1'] if js['level1'] else []
    level2labels = js['level2'] if js['level2'] else []
    level3labels = js['level3'] if js['level3'] else []    
    return level1labels + level2labels + level3labels