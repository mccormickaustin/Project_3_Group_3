# 🎮 Steam Game Recommender with Mood-Based Filtering & Game Details Viewer

## 📌 Overview

This project is a machine learning-based game recommendation system that suggests Steam games based on user input.  
Users can:

- 🎯 Get 5 similar games based on a title and selected mood
- 🔍 View detailed information about any game (price, platform, tags, description)
- 🖥️ Use a desktop app with a dark-themed Kivy interface

Built using TF-IDF + KNN, this project demonstrates the full ML pipeline — from raw data to UI.

---

## 🎯 Objectives

- Recommend games based on user input and emotional "mood"
- Provide detailed insights about a selected game
- Showcase complete ML workflow with deployment-ready UI
- Enhance personalization with mood filtering and game metadata

---

## 📂 Dataset

**Source:** [Game Recommendations on Steam (Kaggle)](https://www.kaggle.com/datasets/antonkozyriev/game-recommendations-on-steam)

Files used:

- `games.csv`: Base info (app ID, platform, price, reviews)
- `games_metadata.json`: Tags and description
- ✅ Merged on `app_id` → cleaned into `cleaned_games.csv`
- ✅ Created:
  - `combined_features` (tags + description)
  - `mood` column (based on keywords)
  - Platform + price + release date fields

---

## 🛠️ Technologies Used

| Tool/Library      | Purpose                             |
|-------------------|-------------------------------------|
| `pandas`          | Data loading and merging            |
| `scikit-learn`    | TF-IDF vectorizer, KNN model        |
| `pickle`          | Save trained models to disk         |
| `Kivy`            | Desktop GUI with buttons, input     |
| `JSON`, `CSV`     | Input files for raw game data       |

---

## 💡 Mood Categories Used

- `fun`
- `horror`
- `brainy`
- `intense`
- `relaxing`
- `general`

🧠 Mood is assigned based on keywords found in tags or description.

---

## 🖥️ How to Run the App

### ✅ Step 1: Install dependencies

```bash
pip install -r requirements.txt
✅ Step 2: Run the Kivy UI
bash
Copy
Edit
cd Final_project/app
python ui_kivy.py
🎮 App Features
Enter a game title in the input field

Select a mood from the dropdown

Click:

View Details to see:

Mood, price, platform, release date, tags, description

Get Recommendations to see:

5 games with similar tags and mood category

📸 Sample Output (Text)
yaml
Copy
Edit
• Portal 2
  Windows, macOS | $9.99 | Released: 2011-04-19

• The Talos Principle
  Windows, Linux | $29.99 | Released: 2014-12-11
🚀 Future Improvements
Use NLP or sentiment analysis to tag moods more accurately

Add genre, platform, or discount filters in UI

Integrate Steam API for real-time prices and availability

Deploy the app online via Gradio or Flask

👤 Developed By
Austin McCormick

Laurie Webb

Kashi Zafar

Final Project – OSU AI Bootcamp
May 2025