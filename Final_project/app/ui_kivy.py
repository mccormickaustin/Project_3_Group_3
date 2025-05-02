from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
import pandas as pd
import pickle
import webbrowser
import re

Window.size = (850, 650)
Window.clearcolor = get_color_from_hex("#121212")

class RecommenderUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 12

        self.input_field = TextInput(hint_text='Enter a game title...', size_hint=(1, 0.08),
                                     foreground_color=(1, 1, 1, 1), background_color=(0.2, 0.2, 0.2, 1),
                                     cursor_color=(1, 1, 1, 1))
        self.add_widget(self.input_field)

        self.appid_input = TextInput(hint_text='Enter Steam App ID...', size_hint=(1, 0.08),
                                     foreground_color=(1, 1, 1, 1), background_color=(0.2, 0.2, 0.2, 1),
                                     cursor_color=(1, 1, 1, 1))
        self.add_widget(self.appid_input)

        self.add_widget(Label(text='🧠 Mood:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.mood_selector = Spinner(text='None', values=['None', 'general', 'fun', 'horror', 'brainy', 'intense', 'relaxing'],
                                     size_hint=(1, 0.08))
        self.add_widget(self.mood_selector)

        self.add_widget(Label(text='🎮 Genre:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.genre_selector = Spinner(text='None',
                                      values=['None', 'Action', 'Adventure', 'Puzzle', 'Horror', 'RPG', 'Simulation', 'Strategy'],
                                      size_hint=(1, 0.08))
        self.add_widget(self.genre_selector)

        button_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        self.details_button = Button(text='Game Description and Similar Games', background_color=(0.2, 0.2, 0.6, 1), color=(1, 1, 1, 1))
        self.details_button.bind(on_press=self.show_game_details)

        self.recommend_button = Button(text='Recommendations', background_color=(0.1, 0.6, 0.2, 1), color=(1, 1, 1, 1))
        self.recommend_button.bind(on_press=self.get_recommendations)

        button_row.add_widget(self.details_button)
        button_row.add_widget(self.recommend_button)
        self.add_widget(button_row)

        self.results = Label(text='Results will appear here...', size_hint=(1, 0.6), halign='left', valign='top',
                             markup=True, color=(1, 1, 1, 1))
        self.results.bind(size=self.results.setter('text_size'))
        self.results.bind(on_ref_press=self.open_hyperlink)

        scroll = ScrollView()
        scroll.add_widget(self.results)
        self.add_widget(scroll)

        self.df = pd.read_csv("../data/cleaned_games.csv")
        with open("../models/knn_model.pkl", "rb") as f:
            self.knn = pickle.load(f)
        with open("../models/tfidf_matrix.pkl", "rb") as f:
            self.tfidf_matrix = pickle.load(f)

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def show_game_details(self, instance):
        title = self.input_field.text.strip().lower()
        app_id = self.appid_input.text.strip()
        game = pd.DataFrame()

        if app_id.isdigit():
            game = self.df[self.df['app_id'] == int(app_id)]
        elif title:
            game = self.df[self.df['title'].str.lower() == title]
        else:
            self.show_popup("Missing Input", "Enter either a game title or App ID.")
            return

        if game.empty:
            self.show_popup("Not Found", "Game not found.")
            return

        row = game.iloc[0]
        price = "Free" if pd.isna(row['price']) or row['price'] == 0 else f"${row['price']:.2f}"
        date = str(row['release_date'])[:10]
        reviews = row.get('user_reviews', 'N/A')
        platforms = [p for p, v in zip(['🖥 Windows', '🍏 macOS', '🐧 Linux'], [row.get('win'), row.get('mac'), row.get('linux')]) if v]
        app_link = f"https://store.steampowered.com/app/{row['app_id']}/"

        output = (
            f"[b]{row['title']}[/b]\n"
            f"[color=#ffa726]App ID:[/color] {row['app_id']} | [ref={app_link}][color=#42a5f5][u]Open on Steam[/u][/color][/ref]\n"
            f"[color=#80cbc4]Mood:[/color] {row.get('mood', 'unknown')}\n"
            f"[color=#ce93d8]Platform:[/color] {', '.join(platforms)}\n"
            f"[color=#ffcc80]Price:[/color] {price}\n"
            f"[color=#f4ff81]Total Reviews:[/color] {reviews}\n"
            f"[color=#c5e1a5]Release Date:[/color] {date}\n"
            f"[color=#b39ddb]Tags:[/color] {row.get('tags', '')}\n\n[i]{row.get('description', '')}[/i]"
        )
        self.results.text = output

    def get_recommendations(self, instance):
        title = self.input_field.text.strip().lower()
        app_id = self.appid_input.text.strip()
        mood = self.mood_selector.text if self.mood_selector.text != "None" else None
        genre = self.genre_selector.text if self.genre_selector.text != "None" else None

        # Title or App ID based recommendation
        if title or app_id:
            matches = pd.DataFrame()
            if app_id.isdigit():
                matches = self.df[self.df['app_id'] == int(app_id)]
            elif title:
                matches = self.df[self.df['title'].str.lower() == title]

            if mood:
                matches = matches[matches['mood'].str.lower() == mood.lower()]

            if matches.empty:
                self.show_popup("No Match", "No matching game found.")
                return

            game_index = matches.index[0]
            _, indices = self.knn.kneighbors(self.tfidf_matrix[game_index])
            recommendations = self.df.iloc[indices[0][1:16]]
        else:
            # Mood/Genre-only filtering
            filtered_df = self.df.copy()
            if mood:
                filtered_df = filtered_df[filtered_df['mood'].str.lower() == mood.lower()]
            if genre:
                genre_lower = genre.lower()
                filtered_df = filtered_df[
                    filtered_df['tags'].astype(str).str.lower().str.contains(fr'\b{re.escape(genre_lower)}\b', regex=True, na=False)
                ]

            recommendations = filtered_df.sort_values(by='user_reviews', ascending=False).head(15)

        if recommendations.empty:
            self.show_popup("No Results", "No games found for selected filters.")
            return

        self.results.text = self._format_dual_column_output("Recommended Games", recommendations)

    def _format_dual_column_output(self, title, df):
        left, right = "", ""
        for i, (_, row) in enumerate(df.iterrows()):
            number = f"{i+1}."
            price = "Free" if pd.isna(row['price']) or row['price'] == 0 else f"${row['price']:.2f}"
            date = str(row['release_date'])[:10]
            reviews = f"{int(row['user_reviews'])} reviews" if pd.notna(row.get('user_reviews')) else "N/A"
            platforms = [p for p, v in zip(['🖥 Windows', '🍏 macOS', '🐧 Linux'], [row.get('win'), row.get('mac'), row.get('linux')]) if v]
            app_link = f"https://store.steampowered.com/app/{row['app_id']}/"
            info = (
                f"{number} [ref={app_link}][color=#42a5f5][u]{row['title']}[/u][/color][/ref]\n"
                f"   {', '.join(platforms)} | {price} | Released: {date} | {reviews}\n\n"
            )
            if i < 8:
                left += info
            else:
                right += info
        return f"[b]{title}[/b]\n\n[left]{left}[/left]     [right]{right}[/right]"

    def open_hyperlink(self, instance, ref):
        webbrowser.open(ref)

class GameApp(App):
    def build(self):
        return RecommenderUI()

if __name__ == '__main__':
    GameApp().run()
