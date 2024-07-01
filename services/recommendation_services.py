from models.AIRecommendation import AIRecommendation

aiRecommendation = AIRecommendation()


def search_product(query):
    return aiRecommendation.search_product(query)