from passive.passive_tweet_generator import main as generate_tweet
from site_interactions import post_to_site

def tweet(post_type, now, name, bot_id, username, password):
    # Generate the tweet content
    try:
        print("\n post type is", post_type)
        content = generate_tweet(bot_id, post_type)
    except Exception as e:
        print(f"{now} - Error generating tweet content for {name} ({bot_id}): {e}")


    # Post the tweet
    try:
        post_to_site(username, password, content)
        print(f"{now} - Tweet posted by {name} ({username}): {content}")
    except Exception as e:
        print(f"{now} - Failed to post tweet for {name} ({username}). Error: {e}")
        
