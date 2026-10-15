from google_play_scraper import app, reviews, Sort
import pandas as pd
import os



# ==========================================
# 1. Project settings
# ==========================================

DATA_FOLDER = "data"
REVIEWS_PER_APP = 500

os.makedirs(DATA_FOLDER, exist_ok=True)


# Five apps to analyze
APPS = {
    "Careem": "com.careem.acma",
    "Yummy": "app.yummy.ps",
    "Sanad": "com.ps.sanad",
    "BDE": "ps.tempo.bde",
    "DEL": "ps.telescope.delivin.user"
}


# ==========================================
# 2. Collect app information
# ==========================================

def scrape_app_info(app_name, app_id):
    print(f"\nCollecting information for {app_name}...")

    try:
        info = app(
            app_id,
            lang="ar",
            country="ps"
        )

        record = {
            "app_name": app_name,
            "app_id": app_id,
            "title": info.get("title"),
            "score": info.get("score"),
            "ratings_count": info.get("ratings"),
            "reviews_count": info.get("reviews"),
            "installs": info.get("installs"),
            "price": info.get("price"),
            "collected_at": pd.Timestamp.now()
        }

        print(f"Successfully collected information for {app_name}.")
        return record

    except Exception as error:
        print(f"Failed to collect information for {app_name}: {error}")
        return {
            "app_name": app_name,
            "app_id": app_id,
            "title": None,
            "score": None,
            "ratings_count": None,
            "reviews_count": None,
            "installs": None,
            "price": None,
            "collected_at": pd.Timestamp.now()
        }


# ==========================================
# 3. Collect app reviews
# ==========================================

def scrape_app_reviews(app_name, app_id, review_count=500):
    print(f"Collecting reviews for {app_name}...")

    collected_reviews = []

    try:
        result, _ = reviews(
            app_id,
            lang="ar",
            country="ps",
            sort=Sort.NEWEST,
            count=review_count
        )

        for review in result:
            collected_reviews.append({
                "app_name": app_name,
                "app_id": app_id,
                "review_id": review.get("reviewId"),
                "review_text": review.get("content"),
                "score": review.get("score"),
                "review_date": review.get("at"),
                "thumbs_up": review.get("thumbsUpCount"),
                "collected_at": pd.Timestamp.now()
            })

        print(
            f"Collected {len(collected_reviews)} reviews "
            f"for {app_name}."
        )

    except Exception as error:
        print(f"Failed to collect reviews for {app_name}: {error}")

    return collected_reviews


# ==========================================
# 4. Run data collection
# ==========================================

def run_scraper():
    apps_data = []
    all_reviews = []

    for app_name, app_id in APPS.items():

        app_record = scrape_app_info(app_name, app_id)
        apps_data.append(app_record)

        app_reviews = scrape_app_reviews(
            app_name,
            app_id,
            review_count=REVIEWS_PER_APP
        )

        all_reviews.extend(app_reviews)

    # Save app information
    apps_df = pd.DataFrame(apps_data)

    apps_df.to_csv(
        os.path.join(DATA_FOLDER, "apps.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    # Save collected reviews
    reviews_df = pd.DataFrame(all_reviews)

    reviews_df.to_csv(
        os.path.join(DATA_FOLDER, "reviews.csv"),
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 45)
    print("DATA COLLECTION SUMMARY")
    print("=" * 45)
    print(f"Applications processed: {len(apps_df)}")
    print(f"Total reviews collected: {len(reviews_df)}")
    print(f"Apps file: {DATA_FOLDER}/apps.csv")
    print(f"Reviews file: {DATA_FOLDER}/reviews.csv")
    print("=" * 45)


if __name__ == "__main__":
    run_scraper()
