import openai

# Set your OpenAI GPT-3 API key
openai.api_key = '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'

# Define a conversation with an initial message
conversation_history = [
    {"role": "system", "content": "You are a helpful assistant that summarizes text."},
    {"role": "user", "content": "Please summarize the following text:"},
    {"role": "assistant", "content": "The text you want me to summarize goes here."},
]

# Function to generate a summary using GPT-3
def get_gpt3_summary(prompt):
    response = openai.ChatCompletions.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
    )
    return response["choices"][0]["message"]["content"]

# User input with the text to be summarized
user_input = "Once upon a time, in a faraway land, there was a magical kingdom..."

# Add user input to the conversation
conversation_history[-1]["content"] = user_input

# Get GPT-3 summary
gpt3_summary = get_gpt3_summary(conversation_history)

# Print the GPT-3 summary
print("GPT-3 Summary:", gpt3_summary)
