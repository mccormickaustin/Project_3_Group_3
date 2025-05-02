import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

import pandas as pd
import pickle

Window.size = (750, 600)
Window.clearcolor = get_color_from_hex("#1e1e1e")


class RecommenderUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 15
        self.spacing = 10

        self.df = pd.read_csv("../data/cleaned_games.csv")
        with open("../models/knn_model.pkl", "rb") as f:
            self.knn = pickle.load(f)
        with open("../models/tfidf_matrix.pkl", "rb") as f:
            self.tfidf_matrix = pickle.load(f)

        self.add_widget(Label(text='🎮 Steam Game Recommender', font_size=26, size_hint=(1, 0.1), color=(1, 1, 1, 1)))

        self.input_field = TextInput(hint_text='Enter a game title...', multiline=False, size_hint=(1, 0.1),
                                     foreground_color=(1, 1, 1, 1), background_color=(0.2, 0.2, 0.2, 1),
                                     cursor_color=(1, 1, 1, 1))
        self.add_widget(self.input_field)

        self.add_widget(Label(text="Mood:", font_size=16, color=(1, 1, 1, 1), size_hint=(1, 0.05)))
        self.mood_selector = Spinner(text='None', values=['None', 'fun', 'horror', 'brainy', 'intense', 'relaxing', 'general'],
                                     size_hint=(1, 0.08), background_color=(0.4, 0.4, 0.4, 1), color=(1, 1, 1, 1))
        self.add_widget(self.mood_selector)

        self.add_widget(Label(text="Genre:", font_size=16, color=(1, 1, 1, 1), size_hint=(1, 0.05)))
        all_genres = sorted({tag.strip().lower() for tags in self.df['tags'].dropna() for tag in tags.split(',')})        self.genre_selector = Spinner(text='None', values=['None'] + all_genres,
                                      size_hint=(1, 0.08), background_color=(0.4, 0.4, 0.4, 1), color=(1, 1, 1, 1))
        self.add_widget(self.genre_selector)

        button_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        self.details_button = Button(text='Game Description',
                                     background_color=(0.35, 0.35, 0.5, 1), color=(1, 1, 1, 1))
        self.details_button.bind(on_press=self.show_game_details)

        self.recommend_button = Button(text='Recommendations',
                                       background_color=(0.25, 0.5, 0.25, 1), color=(1, 1, 1, 1))
        self.recommend_button.bind(on_press=self.get_recommendations)

        button_row.add_widget(self.details_button)
        button_row.add_widget(self.recommend_button)
        self.add_widget(button_row)

        self.results = Label(text='Enter a game title or select mood/genre.',
                             font_size=14, color=(1, 1, 1, 1), halign='left', valign='top', size_hint=(1, None),
                             markup=True)
        self.results.bind(texture_size=self.resize_label_height)

        scroll = ScrollView()
        scroll.add_widget(self.results)
        self.add_widget(scroll)
    def resize_label_height(self, instance, size):
        instance.height = size[1]

    def get_recommendations(self, instance):
        title = self.input_field.text.strip().lower()
        mood = self.mood_selector.text.lower()
        genre = self.genre_selector.text.lower()

        filtered_df = self.df

        if title:
            matches = self.df[self.df['title'].str.lower() == title]
            if matches.empty:
                self.show_popup("No Match", "Game not found.")
                return

            idx = matches.index[0]
            _, indices = self.knn.kneighbors(self.tfidf_matrix[idx])
            recs = self.df.iloc[indices[0][1:]]
        else:
            if mood != 'none':
                filtered_df = filtered_df[filtered_df['mood'].str.lower() == mood]
            if genre != 'none':
                filtered_df = filtered_df[filtered_df['tags'].str.contains(genre, case=False, na=False)]

            recs = filtered_df.sort_values(by='user_reviews', ascending=False).head(15)

        if recs.empty:
            self.results.text = "No recommendations found for the selected filters."
            return

        output = "[b]Recommended Games:[/b]\n\n"
        for _, row in recs.iterrows():
            price = "Free" if pd.isna(row['price']) or row['price'] == 0 else f"${row['price']:.2f}"
            date = str(row['release_date'])[:10] if pd.notna(row['release_date']) else "N/A"
            platforms = []
            if row.get('win'): platforms.append("Windows")
            if row.get('mac'): platforms.append("macOS")
            if row.get('linux'): platforms.append("Linux")
            platform_text = ", ".join(platforms) if platforms else "Unknown Platform"
            output += f"• {row['title']}\n  {platform_text} | {price} | Released: {date}\n\n"

        self.results.text = output

    def show_game_details(self, instance):
        title = self.input_field.text.strip().lower()
        if not title:
            self.show_popup("Input Needed", "Please enter a game title.")
            return

        match = self.df[self.df['title'].str.lower() == title]
        if match.empty:
            self.show_popup("Not Found", "Game not found.")
            return

        row = match.iloc[0]
        price = "Free" if pd.isna(row['price']) or row['price'] == 0 else f"${row['price']:.2f}"
        date = str(row['release_date'])[:10] if pd.notna(row['release_date']) else "N/A"
        platforms = []
        if row.get('win'): platforms.append("Windows")
        if row.get('mac'): platforms.append("macOS")
        if row.get('linux'): platforms.append("Linux")
        platform_text = ", ".join(platforms) if platforms else "Unknown Platform"

        output = f"[b]{row['title']}[/b]\nMood: {row.get('mood', '')}\nPlatform: {platform_text}\nPrice: {price}\nRelease Date: {date}\nTags: {row.get('tags', '')}\n\n[i]{row.get('description', '')}[/i]"
        self.results.text = output

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()


class GameApp(App):
    def build(self):
        return RecommenderUI()


if __name__ == '__main__':
    GameApp().run()
