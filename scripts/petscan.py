import requests
import csv
import pandas as pd
import wikipedia

#Wikipedia Categories
categories = ['Animals', 'Environment', 'Humans', 'Life', 'Plants']


#Petscan Parameters
depth = 1
output_format = 'csv'

with requests.Session() as s:
    all_data = []
    for category in categories:
        url = 'https://petscan.wmflabs.org/?langs_labels_no=&project=wikipedia&edits%5Bbots%5D=both \
                &search_max_results=500&cb_labels_yes_l=1&categories={0}&cb_labels_no_l=1&interface_language=en \
                &language=en&edits%5Bflagged%5D=both&ns%5B0%5D=1&edits%5Banons%5D=both&cb_labels_any_l=1 \
                &depth={1}&&doit=&format={2}'.format(category, depth, output_format)
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        category_list = list(cr)
        all_data += category_list
    
    print(len(all_data))

with open("petscan_articles.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(all_data)
    
df = pd.read_csv('petscan_articles.csv')
def scrape_wiki(row):
    content = ''
    try:
        content = wikipedia.page(pageid=row['pageid']).content
    except:
        pass
    return content


df['Content'] = df.apply(scrape_wiki, axis=1)

df.to_csv('wikipedia_articles.csv')