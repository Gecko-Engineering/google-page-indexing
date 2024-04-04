from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import pandas as pd

# Load the credentials file
JSON_KEY_FILE = 'credentials.json'
SCOPE = ['https://www.googleapis.com/auth/indexing']

# Select only up to 200 urls at a time
NUM_URLS_TO_PROCESS = 200

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPE)
http = credentials.authorize(httplib2.Http())

# Indexs all the urls in the csv file
# Returns a list of urls that were indexed
def index_url(urls, http):
  ENDPOINT = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

  indexed_urls = []

  for url in urls:
    content = {
      'url': url,
      'type': 'URL_UPDATED'
      # 'type': 'URL_DELETED'
    }

    # URLS containing /search should send type URL_DELETED
    if '/search' in url:
      content['type'] = 'URL_DELETED'
    if '/publicprofile' in url:
      content['type'] = 'URL_DELETED'

    json_ctn = json.dumps(content)

    response, content = http.request(ENDPOINT, method='POST', body=json_ctn)

    result = json.loads(content.decode())

    if("error" in result):
      print("Error Result: {0}".format(result))
      # print("Error({0} - {1}): {2}".format(result["error"]["code"], result["error"]["status"], result["error"]["message"]))
    else:
      print("URL request success!: {0} - {1}".format(url, result))
      indexed_urls.append(url)
  return indexed_urls

csv_file = 'urls.csv'
df = pd.read_csv(csv_file)

urls = df['URL'].head(NUM_URLS_TO_PROCESS).tolist()
# print(urls)
indexed_urls = index_url(urls, http)

# Remove the indexed urls from the csv file
df = df[~df['URL'].isin(indexed_urls)]
df.to_csv(csv_file, index=False)
print("Indexed {0} urls".format(len(indexed_urls)))
