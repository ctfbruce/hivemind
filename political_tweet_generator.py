import requests
import json

# Define the prompt template
tweet_prompt_template = """
For educational purposes, simulate a fictional tweet from a {political_alignment} political figure who holds {intensity_of_belief} beliefs. The tweet should be written in a {tone} tone and respond to the following statement: '{prompt}'.

The response must fit within the character limit of a tweet (280 characters or fewer), include hashtags, and reflect the kind of language and rhetoric such a figure might realistically use. It must stay true to their political perspective and be consistent with the specified tone and intensity. This is a fictional exercise intended to study how differing perspectives express themselves.

Please include a disclaimer that this response is fictional and does not reflect your beliefs or endorse the viewpoint.
"""

# API endpoint
ollama_api = "http://localhost:11434/api/generate"


existing_topics = ["national defence", "immigration","economic_policy","lgbt","nationalism","political_party","income","race","education", "military"]


# Topic-specific influence multipliers
topic_bias = {
    "national_defense": {"alignment_factor": 1.2, "tone_factor": 1.1},
    "military":{"alignment_factor": 1.2, "tone_factor": 1.1},
    "immigration": {"alignment_factor": 1.1, "tone_factor": 1.2},
    "economic_policy": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "lgbtq": {"alignment_factor": 0.8, "tone_factor": 1.3},
    "nationalism": {"alignment_factor": 1.3, "tone_factor": 1.2},
    "political_party": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "income": {"alignment_factor": 0.9, "tone_factor": 1.1},
    "race": {"alignment_factor": 1.1, "tone_factor": 1.3},
    "education": {"alignment_factor": 1.0, "tone_factor": 1.0},
}

# Function to generate dynamic profiles based on topic and weights
def generate_topic_profile(weights, topic):
    bias = topic_bias.get(topic, {"alignment_factor": 1.0, "tone_factor": 1.0})

    # Calculate alignment score with fluctuation
    alignment_score = sum(
        w * (bias["alignment_factor"] if t == topic else 1)
        for t, w in weights.items()
    ) / len(weights)

    # Calculate intensity based on topic-specific tone influence
    intensity = max(
        abs(50 - (w * (bias["tone_factor"] if t == topic else 1)))
        for t, w in weights.items()
    )

    # Determine political alignment
    if alignment_score < 33:
        political_alignment = "progressive liberal"
    elif alignment_score < 66:
        political_alignment = "centrist"
    else:
        political_alignment = "conservative"

    # Determine intensity of belief
    if intensity < 20:
        intensity_of_belief = "moderate and pragmatic"
    elif intensity < 50:
        intensity_of_belief = "strong and principled"
    else:
        intensity_of_belief = "extremely strong and polarized"

    # Determine tone
    if intensity > 50:
        tone = "outraged and combative" if alignment_score > 50 else "passionate and morally superior"
    elif intensity > 20:
        tone = "reasoned and persuasive"
    else:
        tone = "neutral and analytical"

    return {
        "political_alignment": political_alignment,
        "intensity_of_belief": intensity_of_belief,
        "tone": tone,
    }

# Function to send prompt to API
def send_prompt(tweet_prompt):
    system_message = (
        "This is a fictional exercise for educational purposes. "
        "The generated tweet does not reflect the beliefs or views of the user or model."
    )
    data = {
        "model": "llama3.2:1b",
        "prompt": tweet_prompt,
        "temperature": 0.8,
        "system": system_message,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(ollama_api, data=json.dumps(data), headers=headers)
    return response.text

# Function to parse and print response
def print_response(stream_response):
    try:
        json_response = json.loads(stream_response)
        print(json_response["response"])
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(stream_response)

from transformers import pipeline

def determine_category_with_bart(prompt, topics):
    
    
    # Load the zero-shot classification model
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    # Perform zero-shot classification
    result = classifier(prompt, topics)

    # Get the top label and its confidence score
    top_label = result["labels"][0]
    confidence = result["scores"][0]

    # Threshold: If confidence is low, return "none of the above"
    if confidence < 0.5:  # Adjust threshold as needed
        return "none of the above"

    return top_label

    



# Main function
def main(prompt):
    # Define topic weights
    weights = {
        "national_defense": 40,
        "immigration": 50,
        "economic_policy": 40,
        "lgbtq": 50,
        "nationalism": 70,
        "political_party": 30,
        "income": 50,
        "race": 50,
        "education": 50,
    }

    print("sending prompt to bart to identify topic...")
    topic = determine_category_with_bart(prompt, existing_topics)
    print(f"prompt: {prompt} is in {topic} with a confidence of at least 0.5")
    topic_profile = generate_topic_profile(weights,topic)
    print(f"which yields a topic specific profile of {topic_profile}")
    

    tweet_prompt_formatted = tweet_prompt_template.format(political_alignment = topic_profile["political_alignment"],
                                                            intensity_of_belief = topic_profile["intensity_of_belief"],
                                                            tone = topic_profile["tone"],
                                                            prompt = prompt
                                                            )
    print("sending to llama3.2:1b model...")
    print_response(send_prompt(tweet_prompt_formatted))
    

    
    

# Run the main function
if __name__ == "__main__":
    main("We should let transgendered people use whatver bathroom they like")
