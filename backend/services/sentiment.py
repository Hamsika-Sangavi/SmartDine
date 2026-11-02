from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def score_text(text: str) -> float:
    if not text:
        return 0.0
    return analyzer.polarity_scores(text)["compound"]