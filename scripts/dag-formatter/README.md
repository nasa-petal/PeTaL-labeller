# MATCH DAG Formatter Script

## What does it do?
<p>The DAG Formatter Script takes in a csv file consisting of a taxonomy structure where each column represents an increasing level of depth and outputs a MATCH friendly text file where each line is a parent/child relationship.</p>
<br/>

## How do I run it?
<p>The script is run by starting it with the "python" command (ex. python example_script.py). The script will by default, look for a "taxonomy.csv" within its directory.</p>
<p>The script accepts one argument (-cp, --csv_path) which is the path + file_name and extension of the csv file. The help parameter can also be passed to the script to get these commands and examples (-h, --help).</p>