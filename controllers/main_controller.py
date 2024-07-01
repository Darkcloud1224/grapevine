from flask import jsonify, request

from services import chat_services
from services import recommendation_services


def manage_response(message, email, needsRecommendation=False):
    
    DescriptionQuery = {}
    ExtractKeywords = {}
    chat_response = {}
    recommended_product = None
    
    
    NeedsRecommendation = chat_services.generate_response("NeedsRecommendation", message, email)
    NeedsRecommendation = NeedsRecommendation.get("response", None)
    
    if NeedsRecommendation:
        ExtractKeywords = chat_services.generate_response("ExtractKeywords", message, email)
        ExtractKeywords = ExtractKeywords.get("response", None)
        
        if len(ExtractKeywords) == 0:
            prompt = f"""
            user is asking you to recommend a product for them but there isn't enough info, ask leading questions instead (don't mention that there isn't enough info).
            
            user prompt here: 
            {message}
            """
            chat_response = chat_services.generate_response("chat", prompt,  email).get("response", None)
            
        else:
            # Search or product
            recommended_product = recommendation_services.search_product(ExtractKeywords)
            
            if recommended_product:
                # prompt to recommend a product
                prompt = f"""
                    I would like you to describe this product to the user
                    
                    brand: {recommended_product.get("BrandName", None)}
                    product name: {recommended_product.get("ProductName", None)}
                    product description: {recommended_product.get("ProductDescription", None)}
                    product price: {recommended_product.get("ProductPrice", None)}
                """
                chat_response = chat_services.generate_response("chat", prompt,  email).get("response", None)
            else:
                prompt = f"""
                    user is asking you to recommend a product but the product couldn't be found, mention you couldn't find it and ask leading questions to get more info.
                    
                    user prompt here: 
                    {message}
                """
                chat_response = chat_services.generate_response("chat", prompt,  email).get("response", None)
  
            
    else:
        chat_response  = chat_services.generate_response("chat", message,  email).get("response", None)
  
    

    response = {
        "choices": [
            {
                "message": {
                    "content": {
                        "NeedsRecommendation": NeedsRecommendation,
                        "Extracted Keywords": ExtractKeywords,
                        "chat response": chat_response,
                        'product_exists': recommended_product != None,
                        "product_path": recommended_product["ProductPath"] if recommended_product else None
                    }
                }
            }
        ]
    }
    return response
def chat():
    json_data = request.json

    message = json_data["messages"][-1]["content"]
    email =  json_data["messages"][-1]["email"]


    response = manage_response(message, email)
    
    # Convert the dictionary to JSON and return
    return jsonify(response)
