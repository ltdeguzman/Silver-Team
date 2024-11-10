import streamlit as st
import openai

# Set up OpenAI API
openai.api_key = 'OPENAI_API_KEY'

def get_chatbot_response(user_input):
    messages = [
        {"role": "system", "content": "You are a knowledgeable assistant for new restaurant owners in San Jose, helping them understand space requirements, seating capacity, and equipment needs. Respond concisely with information about restaurant capacity planning, equipment needs (such as refrigeration, ovens, seating, tables), and general tips for a successful restaurant setup."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

def generate_restaurant_image():
    # Request DALL-E to create an image of a typical restaurant space
    response = openai.Image.create(
        prompt="A modern restaurant interior with tables, chairs, a counter, ambient lighting, and a cozy, welcoming atmosphere.",
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url

def main():
    st.title("Restaurant Startup Advisor - San Jose")
    st.write("Welcome! I’m here to help you with questions about your new restaurant setup in San Jose. Ask me about seating capacity, equipment needs, or any other requirements for a successful restaurant.")

    # Display AI-generated image of a restaurant space
    st.write("### Example Restaurant Space:")
    image_url = generate_restaurant_image()
    st.image(image_url, caption="AI-generated image of a sample restaurant interior.", use_column_width=True)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        st.write(f"**{message['role']}:** {message['content']}")

    # User input for new questions
    user_input = st.text_input("Ask your question here:")

    if user_input:
        st.session_state.messages.append({"role": "User", "content": user_input})
        
        response = get_chatbot_response(user_input)
        st.session_state.messages.append({"role": "Assistant", "content": response})
        
        st.write(f"**Assistant:** {response}")

if __name__ == "__main__":
    main()