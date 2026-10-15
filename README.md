
- Yummy
- Sanad
- BDE
- DEL

Application availability and package identifiers should be
verified during data collection.

## Technologies Used

- Python
- Pandas
- Google Play Scraper
- Plotly
- Streamlit

## Project Structure

final_project/
- data/
- scraper.py
- analysis.py
- app.py
- requirements.txt
- .gitignore
- README.md

## Data Collection

Reviews are collected from Google Play using the
google-play-scraper library.

The scraper is configured to request Arabic-language reviews
using the country parameter `ps`.

The country parameter is a collection setting. It does not
prove that a reviewer lives in Palestine, Gaza, or the
West Bank.

The number of collected reviews depends on application
availability and the scraper's response.

## Data Processing and Analysis

The project includes:

- Data cleaning and preparation.
- Review rating summaries.
- Keyword-based sentiment classification.
- Delivery-related review identification.
- Frequently used word analysis.
- Application comparison.

Sentiment classification uses predefined keywords and should
be treated as an approximate indicator, not a definitive
understanding of customer opinions.

## Dashboard Features

The Streamlit dashboard provides:

- Application filters.
- Sentiment filters.
- Delivery-related review filtering.
- Rating comparison charts.
- Sentiment analysis charts.
- Delivery feedback comparisons.
- Frequently used words.
- Review search and inspection.
- Filtered data export.

Pie charts showing rating distributions represent each
application's share of the sum of the displayed ratings.
They do not represent percentages of satisfied customers.

## Installation

Make sure Python is installed.

Install the required libraries:

    pip install -r requirements.txt

## Running the Project

### Step 1: Collect Data

    python scraper.py

### Step 2: Analyze Data

    python analysis.py

### Step 3: Launch the Dashboard

    python -m streamlit run app.py

Open the local URL displayed in the terminal.

## Limitations

- Google Play data availability may vary.
- Review samples may differ between applications.
- Keyword-based sentiment analysis may miss sarcasm,
  context, and negation.
- Frequent words do not necessarily indicate the most
  important customer concerns.
- Comparisons should consider the number of reviews,
  collection date, and data coverage.

## Future Improvements

- Improve Arabic sentiment analysis.
- Add topic modeling and customer complaint categorization.
- Track competitor performance over time.
- Add more robust validation and reporting.

## Author

Python Data Analysis Project