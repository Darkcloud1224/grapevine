from models.ChatResponse import ChatResponse

chatResponse = ChatResponse()


def generate_response(ability, message, session_id):
    return chatResponse.generate_response(ability, message, session_id)
