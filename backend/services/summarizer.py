import re
from collections import Counter

STOPWORDS = set("""
the a an is are was were be been being have has had do does did will would
could should may might must can this that these those i you he she it we
they my your his her its our their and or but if because as until while
of at by for with about against between into through during before after
above below to from up down in out on off over under again further then
once here there when where why how all any both each few more most other
some such no nor not only own same so than too very just don should now
food place good great service really nice really rated
""".split())

def summarize_reviews(reviews, top_n=5):
    if not reviews:
        return "No reviews available."

    text = " ".join(reviews).lower()
    words = re.findall(r"[a-z]{4,}", text)
    filtered = [w for w in words if w not in STOPWORDS]

    if not filtered:
        return "No standout themes found."

    common = Counter(filtered).most_common(top_n)
    themes = ", ".join(word for word, _ in common)
    return f"Frequently mentioned: {themes}"