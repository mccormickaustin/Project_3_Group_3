# 🎮 Steam Game Recommender

This is a content-based recommender system that suggests Steam games based on a user's input — either a game title, genre, mood, or App ID. It uses text analysis and machine learning to recommend similar games and includes a clean, dark-themed interface built with Kivy.

## 🔍 What This App Does

Recommends 14 similar games when a game title or Steam App ID is entered.

Lets users filter games by mood (like brainy, relaxing, intense) or genre (Action, Puzzle, Horror, etc.).

Displays key game details: App ID, title, platform support (Windows/macOS/Linux), release date, review count, rating, price, and a link to the Steam store page.

Provides a scrollable, user-friendly interface with clickable links using Kivy.
⭐ Features for Personalized Experience:

- ⭐ Add games to a favorites list  
- 📜 View your saved favorite games  
- 🗑️ Clear all favorites with one click  
- 💾 Export your favorites to a text file for later

## 📁 Dataset Used

We used data from the Kaggle dataset:

🎮 [Game Recommendations on Steam – Kaggle](https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam?resource=download)

This dataset includes:

- `games.csv` — with titles, platform info, release dates, prices, and reviews.
- `games_metadata.json` — with game descriptions and genre tags.

These were merged using app_id and then cleaned. We engineered the following extra columns:

tags: Assigned based on keywords in title/description.

mood: Custom labels like horror, intense, etc.

combined_features: A string column combining tags + description for similarity calculation.

## 🧠 How It Works

### Preprocessing

Cleaned game titles by removing special characters like ™, ®, and any non-standard symbols.

Used keyword matching to assign each game a genre.

Tagged each game with a mood based on its description (e.g., "relaxing", "horror", "fun").

Combined the tags and description into a single column for use in vectorization.

### TF-IDF + KNN Model

Applied TF-IDF (Term Frequency-Inverse Document Frequency) to the combined features.

Trained a KNN (K-Nearest Neighbors) model using cosine similarity to find similar games.

Saved both the vector matrix and model using pickle.

### Kivy UI

Users can enter a title or App ID to see game details.

Optional dropdowns for mood and genre filtering.

Scrollable section shows results with links to each game’s Steam page.

Clean layout using dark theme and visual spacing for clarity.

### 🖥️ How to Run the App

1. Clone or download this repository: [GitHub Repository](https://github.com/mccormickaustin/Project_3_Group_3.git)

2. Ensure the following files exist:

   ../data/cleaned_games.csv

   ../models/knn_model.pkl

   ../models/tfidf_matrix.pkl

3. Install dependencies:

   pip install kivy pandas scikit-learn

4. Run the app:

python ui_kivy.py

## 👨‍💻 Technologies Used

Python

Pandas

Scikit-learn (TF-IDF, NearestNeighbors)

Kivy (UI framework)

Regex (for text cleaning)

Pickle (to save/load models)

## 👨‍👩‍👧‍👦 Team Members (Group 3)

Austin Mccormick

Laurie Webb

Kashif Zafar

We collaborated by splitting up tasks related to data cleaning, model training, and UI development. Communication and version control were done using GitHub, Slack, and VS Code.

## 💡 What We Learned

How to merge and clean large datasets from multiple sources.

Writing logic to assign genres and moods when the data isn’t clean.

How to build and save a working ML recommendation model.

Building a real-time, scrollable UI using Kivy.

Improving search flexibility by allowing both title and App ID lookups.

Adding favorites features to create a more personalized experience.

## ⚠️ Challenges We Faced

Dealing with incomplete or messy metadata.

Matching titles across datasets (some didn’t have exact matches).

Getting the Kivy UI to scroll and resize properly.

Making sure recommendations actually felt relevant and useful.

Ensuring proper filtering when genre and mood were combined.

Persisting favorites within a session and enabling export.

## 🚀 Future Improvements

If we continue this project, here are a few things we’d like to add:

Steam API integration for live game data.

Add game screenshots and trailers to the UI.

Add charts/visuals to show popularity or genre distribution.

Refine mood detection using NLP sentiment analysis or transformer models.

Thanks for checking out our project — we hope you find a new favorite game through it! 🎮
