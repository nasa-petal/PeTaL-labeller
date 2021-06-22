# Lens Cleaner Script

## What does it do?
<p>The Lens Cleaner Script takes in the JSON output from the Lens API and reformats it into a match friendly JSON file. The Lens Cleaner Script also takes in a csv that contains a column of titles and three columns of labels representing different levels. The labels from this csv is added to the Lens JSON file based on title where applicable.</p>
<br/>

## How do I run it?
<p>The script is run by starting it with the "python" command (ex. python example_script.py). The script will by default, look for a "labeled_data.csv" and a "lens_output.json" file within the same directory.</p>
<p>The script accepts two arguments (-jp, --json_path, -cp, --csv_path) which is the path + file_name and extension of the respective files. The help parameter can also be passed to the script to get these commands and examples (-h, --help).</p>