import openai
from sk import my_sk  # Import the API key from sk.py

# Set your OpenAI API key
openai.api_key = my_sk

def generate_prompt_based_output(prompt):
    response = openai.chat.completions.create(
        model="gpt-4",  # Specify the model as GPT-4
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    
    # return response['choices']['message']['content']
    return response
# Example of using prompt engineering
prompt = """
You are a storyteller who creates thrilling adventure stories.\
Please generate an adventure story within 100 words.\
Retrieve three key time frames from the story, and describe them with [Object] [Relation] [Object] type of scene descriptions.\
The relations was limited to "above", "below", "at the right of", "at the left of", and "on top of". \
Please tell the story in a captivating and imaginative way, engaging the reader from beginning to end.

"""

# prompt = """
# You are a storyteller who creates thrilling adventure stories. 
# Please generate an adventure story that includes the following elements:
# - A brave hero named Aria who embarks on a quest to find a hidden treasure.
# - A mysterious map that leads through enchanted forests and ancient ruins.
# - Dangerous creatures that Aria must outsmart or defeat.
# - A twist where the treasure is not what it seems.
# - A resolution where Aria learns an important lesson by the end of the journey.

# Please tell the story in a captivating and imaginative way, engaging the reader from beginning to end.
# """

# Generate the story using the prompt
story = generate_prompt_based_output(prompt)

# Print the generated story
print(story)
