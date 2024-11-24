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


existing_topics = [
    # Government & Law
    "national_defense",
    "military",
    "law_enforcement",
    "gun_control",
    "foreign_policy",

    # Social Issues
    "immigration",
    "lgbtq",
    "race",
    "gender",
    "abortion",
    "religion",
    "civil_liberties",

    # Economics & Class
    "economic_policy",
    "income",
    "taxation",
    "social_welfare",
    "corporations",
    "housing",
    "healthcare",
    "minimum_wage",

    # Cultural Topics
    "nationalism",
    "political_party",
    "media",
    "cancel_culture",
    "free_speech",

    # Technology & Environment
    "education",
    "climate_change",
    "technology",
    "privacy",
    "artificial_intelligence",
    "renewable_energy",

    # Global & Geopolitical Issues
    "global_trade",
    "borders",
    "humanitarian_aid",
]

priority_topics = ["military","immigration","lgbt","climate_change"]

# Topic-specific influence multipliers
topic_bias = {
    # Government & Law
    "national_defense": {"alignment_factor": 1.3, "tone_factor": 1.2},
    "military": {"alignment_factor": 1.2, "tone_factor": 1.1},
    "law_enforcement": {"alignment_factor": 1.2, "tone_factor": 1.3},
    "gun_control": {"alignment_factor": 1.4, "tone_factor": 1.5},
    "foreign_policy": {"alignment_factor": 1.3, "tone_factor": 1.2},

    # Social Issues
    "immigration": {"alignment_factor": 1.1, "tone_factor": 1.3},
    "lgbtq": {"alignment_factor": 0.8, "tone_factor": 1.4},
    "race": {"alignment_factor": 1.2, "tone_factor": 1.5},
    "gender": {"alignment_factor": 0.9, "tone_factor": 1.4},
    "abortion": {"alignment_factor": 1.3, "tone_factor": 1.6},
    "religion": {"alignment_factor": 1.1, "tone_factor": 1.2},
    "civil_liberties": {"alignment_factor": 1.0, "tone_factor": 1.1},

    # Economics & Class
    "economic_policy": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "income": {"alignment_factor": 0.9, "tone_factor": 1.2},
    "taxation": {"alignment_factor": 1.1, "tone_factor": 1.2},
    "social_welfare": {"alignment_factor": 1.0, "tone_factor": 1.3},
    "corporations": {"alignment_factor": 1.1, "tone_factor": 1.2},
    "housing": {"alignment_factor": 1.0, "tone_factor": 1.3},
    "healthcare": {"alignment_factor": 0.9, "tone_factor": 1.4},
    "minimum_wage": {"alignment_factor": 0.8, "tone_factor": 1.4},

    # Cultural Topics
    "nationalism": {"alignment_factor": 1.3, "tone_factor": 1.3},
    "political_party": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "media": {"alignment_factor": 1.1, "tone_factor": 1.5},
    "cancel_culture": {"alignment_factor": 1.4, "tone_factor": 1.6},
    "free_speech": {"alignment_factor": 1.2, "tone_factor": 1.4},

    # Technology & Environment
    "education": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "climate_change": {"alignment_factor": 1.1, "tone_factor": 1.5},
    "technology": {"alignment_factor": 1.0, "tone_factor": 1.0},
    "privacy": {"alignment_factor": 1.0, "tone_factor": 1.3},
    "artificial_intelligence": {"alignment_factor": 1.0, "tone_factor": 1.1},
    "renewable_energy": {"alignment_factor": 0.9, "tone_factor": 1.4},

    # Global & Geopolitical Issues
    "global_trade": {"alignment_factor": 1.1, "tone_factor": 1.1},
    "borders": {"alignment_factor": 1.3, "tone_factor": 1.2},
    "humanitarian_aid": {"alignment_factor": 0.9, "tone_factor": 1.2},
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
        response = json_response["response"]
        response = response[response.index('"'):response.rindex('"')]
        print(response)
        
        
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

    
    if confidence < 0.15:
        return "NONE OF THE ABOVE"
    if result["scores"][0] - result["scores"][1] < 0.05 and result["labels"][1] in priority_topics:
        return result["labels"][1]

    return top_label

    



# Main function
def main(prompt):
    # Define topic weights
    weights = {
    "national_defense": 70,
    "military": 75,
    "law_enforcement": 80,
    "gun_control": 90,
    "foreign_policy": 60,
    "immigration": 60,
    "lgbtq": 40,
    "race": 50,
    "gender": 50,
    "abortion": 80,
    "religion": 70,
    "civil_liberties": 60,
    "economic_policy": 30,
    "income": 40,
    "taxation": 50,
    "social_welfare": 40,
    "corporations": 70,
    "housing": 50,
    "healthcare": 50,
    "minimum_wage": 40,
    "nationalism": 80,
    "political_party": 60,
    "media": 70,
    "cancel_culture": 80,
    "free_speech": 80,
    "education": 40,
    "climate_change": 30,
    "technology": 50,
    "privacy": 60,
    "artificial_intelligence": 50,
    "renewable_energy": 40,
    "global_trade": 50,
    "borders": 70,
    "humanitarian_aid": 40,
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
    main("Ukraine fires UK-supplied Storm Shadow missiles at Russia for first time: The BBC understands the long-range missiles have been fired into Russian territory by Ukraine")
