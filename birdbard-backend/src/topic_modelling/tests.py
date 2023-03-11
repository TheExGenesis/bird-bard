# %%
from prep_archive import clean_tweet_text

def test_clean_tweet_text():
    TEST_TWEET = "RT @ConversationUK: Scientists are working out the maths behind 'impossible' never-repeating patterns\n\nhttps://t.co/nyv93dMWB8 https://t.co…"
    assert clean_tweet_text("RT @ConversationUK: Scientists are working out the maths behind 'impossible' never-repeating patterns\n\nhttps://t.co/nyv93dMWB8 https://t.co…") == "Scientists are working out the maths behind 'impossible' never-repeating patterns"

if __name__ == "__main__":
    test_clean_tweet_text()
    
# %%
