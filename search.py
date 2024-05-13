# hello_algolia.py
from algoliasearch.search_client import SearchClient

# Connect and authenticate with your Algolia app
applicationID = "D50DM3JZ06"
api_key = "e7c937a48f59d3e0790d63dc7f75bd71"
client = SearchClient.create(applicationID, api_key)

# Search the index and print the results
index = client.init_index("Product")

results = index.search("blanket")
print(results["hits"][0]["path"].split("/")[1])
