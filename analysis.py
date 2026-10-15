import os
import pandas as pd

# File paths
apps_file = "data/apps.csv"
reviews_file = "data/reviews.csv"

# Positive Arabic words
positive_words = [
    "ممتاز", "ممتازة", "رائع", "رائعة", "جيد", "جيدة",
    "جميل", "جميلة", "سريع", "سريعة", "شكرا", "شكراً",
    "أحب", "مفيد", "مفيدة", "مريح", "مريحة", "سهل",
    "سهلة", "أنصح", "مميز", "مميزة", "حلو", "حلوة"
]

# Negative Arabic words
negative_words = [
    "سيء", "سيئة", "سيئ", "بطيء", "بطيئة", "تأخير",
    "متأخر", "متأخرة", "مشكلة", "مشاكل", "خطأ",
    "سيئه", "فاشل", "فاشلة", "غالي", "غالية",
    "إلغاء", "لا يعمل", "ما يعمل", "سيء جدا",
    "سيء للغاية", "سيئة للغاية"
]

# Words related to delivery
delivery_words = [
    "توصيل", "التوصيل", "الطلب", "السائق", "مندوب",
    "تأخير", "متأخر", "لم يصل", "ما وصل",
    "وصل متأخر", "تأخر الطلب", "رسوم التوصيل",
    "عنوان", "الشحن"
]

# Common words excluded from frequent-word analysis
stop_words = {
    "في", "من", "على", "عن", "إلى", "الى", "هذا",
    "هذه", "هو", "هي", "و", "أو", "لا", "ما",
    "كان", "كانت", "مع", "كل", "بعد", "تم",
    "التطبيق", "الذي", "التي", "انا", "أنا",
    "لكن", "جدا", "جداً", "للغاية"
}


def analyze_sentiment(text):
    """Classify review sentiment using keyword matching."""
    text = str(text).strip()

    if not text:
        return "Unknown"

    positive_count = sum(
        1 for word in positive_words if word in text
    )

    negative_count = sum(
        1 for word in negative_words if word in text
    )

    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"


def main():
    # Check that input files exist
    if not os.path.exists(apps_file) or not os.path.exists(reviews_file):
        print("Please run scraper.py first.")
        return

    # Read data
    apps = pd.read_csv(apps_file)
    reviews = pd.read_csv(reviews_file)

    # Clean app data
    apps = apps.drop_duplicates(subset="app_id")
    apps["score"] = pd.to_numeric(
        apps["score"], errors="coerce"
    )

    # Clean review data
    reviews["review_text"] = (
        reviews["review_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    reviews["score"] = pd.to_numeric(
        reviews["score"], errors="coerce"
    )

    reviews["review_date"] = pd.to_datetime(
        reviews["review_date"],
        errors="coerce",
        utc=True
    )

    reviews = reviews.drop_duplicates(
        subset="review_id"
    )

    reviews = reviews[
        reviews["score"].between(1, 5)
    ].copy()

    # Analyze sentiment from review text
    reviews["sentiment"] = reviews[
        "review_text"
    ].apply(analyze_sentiment)

    # Detect reviews mentioning delivery
    reviews["mentions_delivery"] = reviews[
        "review_text"
    ].apply(
        lambda text: any(
            word in text for word in delivery_words
        )
    )

    # Summarize reviews for each app
    summary = reviews.groupby("app_name").agg(
        reviews_in_sample=("score", "count"),
        average_review_score=("score", "mean"),

        # Sentiment based on star ratings
        positive_by_rating=(
            "score", lambda x: (x >= 4).sum()
        ),
        neutral_by_rating=(
            "score", lambda x: (x == 3).sum()
        ),
        negative_by_rating=(
            "score", lambda x: (x <= 2).sum()
        ),

        # Sentiment based on review text
        positive_by_text=(
            "sentiment", lambda x: (x == "Positive").sum()
        ),
        neutral_by_text=(
            "sentiment", lambda x: (x == "Neutral").sum()
        ),
        negative_by_text=(
            "sentiment", lambda x: (x == "Negative").sum()
        ),

        # Delivery-related reviews
        delivery_mentions=("mentions_delivery", "sum")
    ).round(2).reset_index()

    # Add Google Play app rating
    summary = summary.merge(
        apps[["app_name", "score"]].rename(
            columns={"score": "google_play_rating"}
        ),
        on="app_name",
        how="left"
    )

    # Save summary results
    summary.to_csv(
        "data/analysis_results.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Save analyzed reviews
    reviews.to_csv(
        "data/analyzed_reviews.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Find the most frequent words
    all_text = " ".join(
        reviews["review_text"].tolist()
    ).lower()

    words = all_text.split()

    cleaned_words = [
        word.strip(".,!?؟،؛:()[]{}\"'«»")
        for word in words
    ]

    cleaned_words = [
        word for word in cleaned_words
        if len(word) > 2 and word not in stop_words
    ]

    word_counts = (
        pd.Series(cleaned_words)
        .value_counts()
        .head(30)
        .rename_axis("word")
        .reset_index(name="frequency")
    )

    word_counts.to_csv(
        "data/frequent_words.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Display results
    print("Analysis completed successfully!")
    print("\nApp comparison:")
    print(summary.to_string(index=False))

    print("\nMost frequent words:")
    print(word_counts.head(10).to_string(index=False))

    print("\nFiles saved:")
    print("- data/analysis_results.csv")
    print("- data/analyzed_reviews.csv")
    print("- data/frequent_words.csv")


if __name__ == "__main__":
    main()









































# import pandas as pd

# # File paths
# apps_file = "data/apps.csv"
# reviews_file = "data/reviews.csv"

# # Check files
# if not os.path.exists(apps_file) or not os.path.exists(reviews_file):
#     print("Please run scraper.py first.")
# else:
#     # Read data
#     apps = pd.read_csv(apps_file)
#     reviews = pd.read_csv(reviews_file)

#     # Clean app data
#     apps = apps.drop_duplicates(subset="app_id")
#     apps["score"] = pd.to_numeric(apps["score"], errors="coerce")

#     # Clean reviews
#     reviews["review_text"] = reviews["review_text"].fillna("").astype(str).str.strip()
#     reviews["score"] = pd.to_numeric(reviews["score"], errors="coerce")
#     reviews["review_date"] = pd.to_datetime(
#         reviews["review_date"], errors="coerce", utc=True
#     )

#     reviews = reviews.drop_duplicates(subset="review_id")
#     reviews = reviews[reviews["score"].between(1, 5)]

#     # Summarize reviews for each app
#     summary = reviews.groupby("app_name").agg(
#         reviews_in_sample=("score", "count"),
#         average_review_score=("score", "mean"),
#         positive_reviews=("score", lambda x: (x >= 4).sum()),
#         neutral_reviews=("score", lambda x: (x == 3).sum()),
#         negative_reviews=("score", lambda x: (x <= 2).sum())
#     ).round(2).reset_index()

#     # Add Google Play rating
#     summary = summary.merge(
#         apps[["app_name", "score"]].rename(
#             columns={"score": "google_play_rating"}
#         ),
#         on="app_name",
#         how="left"
#     )

#     # Save results
#     summary.to_csv(
#         "data/analysis_results.csv",
#         index=False,
#         encoding="utf-8-sig"
#     )

#     print("Analysis completed successfully!")
#     print(summary.to_string(index=False))
#     print("\nResults saved to data/analysis_results.csv")