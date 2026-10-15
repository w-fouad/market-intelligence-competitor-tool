import os
import pandas as pd
import plotly.express as px
import streamlit as st


# 1. Page configuration
st.set_page_config(
    page_title="Shopping Apps Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("Shopping and Delivery Apps Analysis")
st.write("Interactive analysis of customer reviews.")


# 2. Load data
files = {
    "summary": "data/analysis_results.csv",
    "reviews": "data/analyzed_reviews.csv",
    "words": "data/frequent_words.csv"
}

if not all(os.path.exists(p) for p in files.values()):
    st.error("Analysis files are missing.")
    st.info("Run scraper.py and analysis.py first.")
    st.stop()

summary = pd.read_csv(files["summary"])
reviews = pd.read_csv(files["reviews"])
words = pd.read_csv(files["words"])


# 3. Validate data
required_columns = {
    "summary": [
        "app_name", "average_review_score",
        "google_play_rating", "positive_by_text",
        "neutral_by_text", "negative_by_text",
        "delivery_mentions"
    ],
    "reviews": [
        "app_name", "review_text", "score",
        "sentiment", "mentions_delivery"
    ],
    "words": ["word", "frequency"]
}

datasets = {
    "summary": summary,
    "reviews": reviews,
    "words": words
}

for name, columns in required_columns.items():
    if not set(columns).issubset(datasets[name].columns):
        st.error(f"Missing columns in {files[name]}.")
        st.info("Run analysis.py again.")
        st.stop()


# 4. Prepare data
reviews["review_text"] = (
    reviews["review_text"].fillna("").astype(str)
)

reviews["score"] = pd.to_numeric(
    reviews["score"], errors="coerce"
)

summary["average_review_score"] = pd.to_numeric(
    summary["average_review_score"], errors="coerce"
)

summary["google_play_rating"] = pd.to_numeric(
    summary["google_play_rating"], errors="coerce"
)

reviews["mentions_delivery"] = (
    reviews["mentions_delivery"]
    .astype(str).str.lower().isin(["true", "1"])
)


# 5. Sidebar filters
st.sidebar.header("Filters")

apps = sorted(reviews["app_name"].dropna().unique())
sentiments = sorted(
    reviews["sentiment"].dropna().unique()
)

selected_apps = st.sidebar.multiselect(
    "Applications",
    apps,
    default=list(apps)
)

selected_sentiments = st.sidebar.multiselect(
    "Sentiments",
    sentiments,
    default=list(sentiments)
)

delivery_only = st.sidebar.checkbox(
    "Delivery-related reviews only"
)


# 6. Apply filters
data = reviews[
    reviews["app_name"].isin(selected_apps)
    & reviews["sentiment"].isin(selected_sentiments)
].copy()

if delivery_only:
    data = data[data["mentions_delivery"]]

app_summary = summary[
    summary["app_name"].isin(selected_apps)
].copy()


# 7. Overview metrics
st.header("Overview")

col1, col2, col3, col4 = st.columns(4)

average_score = data["score"].mean()

col1.metric("Reviews", f"{len(data):,}")

col2.metric(
    "Average Score",
    f"{average_score:.2f}/5"
    if pd.notna(average_score)
    else "N/A"
)

col3.metric(
    "Negative Reviews",
    int((data["sentiment"] == "Negative").sum())
)

col4.metric(
    "Delivery Mentions",
    int(data["mentions_delivery"].sum())
)


# 8. Reusable chart function
def show_chart(data, x, y, title, **options):
    figure = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        **options
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )


# 9. Rating comparison
st.header("Ratings Comparison")

if not app_summary.empty:
    ratings = app_summary[
        ["app_name", "average_review_score"]
    ].dropna()

    figure = px.pie(
        ratings,
        names="app_name",
        values="average_review_score",
        title="Average Review Score by Application",
        hole=0.35
    )

    figure.update_traces(
        textinfo="label+percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Average score: %{value:.2f}/5<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    st.plotly_chart(
        figure,
        use_container_width=True
    )



# 10. Sentiment analysis
st.header("Sentiment Analysis")

if not app_summary.empty:
    sentiment_data = app_summary.melt(
        id_vars="app_name",
        value_vars=[
            "positive_by_text",
            "neutral_by_text",
            "negative_by_text"
        ],
        var_name="sentiment",
        value_name="count"
    )

    sentiment_data["sentiment"] = (
        sentiment_data["sentiment"].map({
            "positive_by_text": "Positive",
            "neutral_by_text": "Neutral",
            "negative_by_text": "Negative"
        })
    )

    show_chart(
        sentiment_data,
        "app_name",
        "count",
        "Sentiment by Application",
        color="sentiment",
        barmode="stack"
    )


# 11. Delivery analysis
st.header("Delivery Feedback")

if not app_summary.empty:
    show_chart(
        app_summary,
        "app_name",
        "delivery_mentions",
        "Reviews Mentioning Delivery"
    )

st.caption(
    "Delivery mentions are keyword-based and "
    "do not necessarily indicate complaints."
)


# 12. Frequent words
st.header("Most Frequent Words")

if not words.empty:
    words["frequency"] = pd.to_numeric(
        words["frequency"], errors="coerce"
    )

    top_words = (
        words.dropna(subset=["frequency"])
        .head(20)
        .sort_values("frequency")
    )

    if not top_words.empty:
        show_chart(
            top_words,
            "frequency",
            "word",
            "20 Most Frequent Words",
            orientation="h"
        )
    else:
        st.info("No frequent words available.")
else:
    st.info("No frequent words available.")


# 13. Review search and table
st.header("Customer Reviews")

search_text = st.text_input("Search review text")

filtered = data.copy()

if search_text:
    filtered = filtered[
        filtered["review_text"].str.contains(
            search_text,
            case=False,
            na=False,
            regex=False
        )
    ]

display_columns = [
    "app_name",
    "score",
    "sentiment",
    "mentions_delivery",
    "review_date",
    "review_text"
]

display_columns = [
    col for col in display_columns
    if col in filtered.columns
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True
)


# 14. Download filtered reviews
csv_data = filtered[display_columns].to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="Download Filtered Reviews CSV",
    data=csv_data,
    file_name="filtered_reviews.csv",
    mime="text/csv"
)


# 15. Application summary
st.header("Application Summary")

st.dataframe(
    app_summary,
    use_container_width=True,
    hide_index=True
)


# 16. Data source note
st.caption(
    "Source: collected Google Play data. "
    "Results represent the collected sample."
)


















# import plotly.express as px
# import streamlit as st
# import pandas as pd
# st.set_page_config(page_title="Shopping Apps Analysis", page_icon="📊", layout="wide")
# st.title("Shopping and Delivery Apps Analysis")

# files = {"summary": "data/analysis_results.csv", "reviews": "data/analyzed_reviews.csv", "words": "data/frequent_words.csv"}
# if not all(os.path.exists(p) for p in files.values()):
#     st.error("Analysis files missing. Run scraper.py and analysis.py first.")
#     st.stop()

# summary, reviews, words = [pd.read_csv(p) for p in files.values()]

# required = {
#     "summary": {"app_name", "average_review_score", "google_play_rating", "positive_by_text", "neutral_by_text", "negative_by_text", "delivery_mentions"},
#     "reviews": {"app_name", "review_text", "score", "sentiment", "mentions_delivery"},
#     "words": {"word", "frequency"}
# }
# for name, cols in required.items():
#     df = {"summary": summary, "reviews": reviews, "words": words}[name]
#     if not cols.issubset(df.columns):
#         st.error(f"Required columns missing from {files[name]}. Run analysis.py again.")
#         st.stop()

# reviews["review_text"] = reviews["review_text"].fillna("").astype(str)
# reviews["score"] = pd.to_numeric(reviews["score"], errors="coerce")
# reviews["mentions_delivery"] = reviews["mentions_delivery"].astype(str).str.lower().isin(["true", "1"])
# summary["average_review_score"] = pd.to_numeric(summary["average_review_score"], errors="coerce")
# summary["google_play_rating"] = pd.to_numeric(summary["google_play_rating"], errors="coerce")

# st.sidebar.header("Filters")
# apps = sorted(reviews["app_name"].dropna().unique())
# sentiments = sorted(reviews["sentiment"].dropna().unique())
# selected_apps = st.sidebar.multiselect("Applications", apps, default=list(apps))
# selected_sentiments = st.sidebar.multiselect("Sentiments", sentiments, default=list(sentiments))
# delivery_only = st.sidebar.checkbox("Delivery-related reviews only")

# data = reviews[reviews["app_name"].isin(selected_apps) & reviews["sentiment"].isin(selected_sentiments)].copy()
# if delivery_only:
#     data = data[data["mentions_delivery"]]
# app_summary = summary[summary["app_name"].isin(selected_apps)].copy()

# st.header("Overview")
# c1, c2, c3, c4 = st.columns(4)
# c1.metric("Reviews", f"{len(data):,}")
# c2.metric("Average Score", f"{data['score'].mean():.2f}/5" if data["score"].notna().any() else "N/A")
# c3.metric("Negative Reviews", int((data["sentiment"] == "Negative").sum()))
# c4.metric("Delivery Mentions", int(data["mentions_delivery"].sum()))

# def show_chart(df, x, y, title, **kwargs):
#     st.plotly_chart(px.bar(df, x=x, y=y, title=title, **kwargs), use_container_width=True)

# st.header("Ratings Comparison")
# if not app_summary.empty:
#     ratings = app_summary.melt(id_vars="app_name", value_vars=["average_review_score", "google_play_rating"], var_name="type", value_name="rating")
#     ratings["type"] = ratings["type"].map({"average_review_score": "Average Review Score", "google_play_rating": "Google Play Rating"})
#     show_chart(ratings, "app_name", "rating", "Ratings by Application", color="type", barmode="group", range_y=[0, 5])

# st.header("Sentiment Analysis")
# if not app_summary.empty:
#     sentiment = app_summary.melt(id_vars="app_name", value_vars=["positive_by_text", "neutral_by_text", "negative_by_text"], var_name="sentiment", value_name="count")
#     sentiment["sentiment"] = sentiment["sentiment"].map({"positive_by_text": "Positive", "neutral_by_text": "Neutral", "negative_by_text": "Negative"})
#     show_chart(sentiment, "app_name", "count", "Text-Based Sentiment", color="sentiment", barmode="stack")

# st.header("Delivery Feedback")
# if not app_summary.empty:
#     show_chart(app_summary, "app_name", "delivery_mentions", "Reviews Mentioning Delivery")
# st.caption("Delivery mentions are keyword-based and do not necessarily indicate complaints.")

# st.header("Most Frequent Words")
# if not words.empty:
#     words["frequency"] = pd.to_numeric(words["frequency"], errors="coerce")
#     top_words = words.dropna(subset=["frequency"]).head(20).sort_values("frequency")
#     if not top_words.empty:
#         show_chart(top_words, "frequency", "word", "20 Most Frequent Words", orientation="h")
#     else:
#         st.info("No frequent words available.")
# else:
#     st.info("No frequent words available.")

# st.header("Customer Reviews")
# search = st.text_input("Search review text")
# filtered = data[data["review_text"].str.contains(search, case=False, na=False, regex=False)] if search else data.copy()
# columns = [c for c in ["app_name", "score", "sentiment", "mentions_delivery", "review_date", "review_text"] if c in filtered.columns]
# st.dataframe(filtered[columns], use_container_width=True, hide_index=True)
# st.download_button("Download Filtered Reviews CSV", filtered[columns].to_csv(index=False).encode("utf-8-sig"), "filtered_reviews.csv", "text/csv")

# st.header("Application Summary")
# st.dataframe(app_summary, use_container_width=True, hide_index=True)
# st.caption("Source: collected Google Play data. Results describe the collected sample, not all users or reviews.")
