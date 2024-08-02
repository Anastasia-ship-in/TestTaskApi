import google.generativeai as genai
from env import SECRET_KEY

# API_KEY = 'AIzaSyCWMOtZlE7-fra8ztcfIxDyekpAQORZXMw'
genai.configure(api_key=SECRET_KEY)


def generate_reply(post_content, comment_content):
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"Post: '{post_content}'\nComment: '{comment_content}'\nReply with a thoughtful response:"

    response = model.generate_content(prompt)

    return response.text
