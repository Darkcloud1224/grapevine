
from algoliasearch.search_client import SearchClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AIRecommendation():
    
    def __init__(self):
        self.applicationID =model_type = os.getenv('AlgoliaApplicationID') 
        self.api_key = os.getenv('AlgoliaApiKey')
        self.client = SearchClient.create(self.applicationID, self.api_key)

    def search_product(self, query):
        # Search the index and print the results
        index = self.client.init_index("Product")

        results = index.search(query)
        try:
            result = results["hits"][0]
            output = {
                "ProductName": result["ProductName"],
                "ProductPath": result["objectID"],
                "ProductDescription": result["ProductDescription"],
                "ProductPrice": result["ProductPrice"],
                "BrandName": result["BrandNameText"]
                
            }
            print(output)
            return output
        except:
            return {}