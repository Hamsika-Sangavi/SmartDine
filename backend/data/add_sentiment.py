import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

df = pd.read_pickle("data/zomato_clean.pkl")
analyzer = SentimentIntensityAnalyzer()

def avg_sentiment(reviews):
    if not reviews:
        return 0.0
    scores = [analyzer.polarity_scores(r)["compound"] for r in reviews]
    return sum(scores) / len(scores)

df["sentiment_score"] = df["reviews_parsed"].apply(avg_sentiment)

print(df[["name", "rate", "sentiment_score"]].head(5).to_string())
print("\nSentiment score range:", df["sentiment_score"].min(), "to", df["sentiment_score"].max())

df.to_pickle("data/zomato_with_sentiment.pkl")
print("Saved to data/zomato_with_sentiment.pkl")