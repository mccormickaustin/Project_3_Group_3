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
from datetime import datetime
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

        heading = Label(
        text='[b][size=28]Steam Game Recommender[/size][/b]',
        markup=True,
        size_hint=(1, 0.12),
        halign='center',
        valign='middle',
        color=(1, 1, 1, 1)
    )
    
        heading.bind(size=heading.setter('text_size'))
        self.add_widget(heading)

        self.input_field = TextInput(hint_text='Enter a game title...', size_hint=(1, 0.08),
                                 foreground_color=(1, 1, 1, 1), background_color=(0.2, 0.2, 0.2, 1),
                                 cursor_color=(1, 1, 1, 1))
        self.add_widget(Label(text='Game Title:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.add_widget(self.input_field)

        self.appid_input = TextInput(hint_text='Enter Steam App ID...', size_hint=(1, 0.08),
                                 foreground_color=(1, 1, 1, 1), background_color=(0.2, 0.2, 0.2, 1),
                                 cursor_color=(1, 1, 1, 1))
        self.add_widget(Label(text='App ID:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.add_widget(self.appid_input)

        self.add_widget(Label(text='Mood:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.mood_selector = Spinner(text='None', values=['None', 'general', 'horror', 'brainy', 'intense', 'relaxing'],
                         size_hint=(1, 0.08))
        self.add_widget(self.mood_selector)

        self.add_widget(Label(text='Genre:', size_hint=(1, 0.05), color=(1, 1, 1, 1)))
        self.genre_selector = Spinner(text='None',
                                  values=['None', 'Action', 'Adventure', 'Puzzle', 'Horror', 'RPG', 'Simulation', 'Strategy'],
                                  size_hint=(1, 0.08))
        self.add_widget(self.genre_selector)

        button_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        self.details_button = Button(text='Show Game Info', background_color=(0.2, 0.2, 0.6, 1), color=(1, 1, 1, 1))
        self.details_button.bind(on_press=self.show_game_details)

        self.recommend_button = Button(text='Find Similar Games', background_color=(0.1, 0.6, 0.2, 1), color=(1, 1, 1, 1))
        self.recommend_button.bind(on_press=self.get_recommendations)

        self.favorite_button = Button(text='⭐ Save to Favorites', background_color=(0.6, 0.4, 0.1, 1), color=(1, 1, 1, 1))
        self.favorite_button.bind(on_press=self.save_to_favorites)
        self.view_favorites_button = Button(text='📜 See Favorites', background_color=(0.3, 0.3, 0.5, 1), color=(1, 1, 1, 1))
        self.view_favorites_button.bind(on_press=self.view_favorites)
        self.clear_favorites_button = Button(text='🗑 Clear Favorites', background_color=(0.4, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        self.clear_favorites_button.bind(on_press=self.clear_favorites)
        self.export_favorites_button = Button(text='💾 Save list', background_color=(0.2, 0.5, 0.2, 1), color=(1, 1, 1, 1))
        self.export_favorites_button.bind(on_press=self.export_favorites)

        self.exit_button = Button(text='Exit', background_color=(0.6, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        self.exit_button.bind(on_press=self.exit_app)

        button_row.add_widget(self.details_button)
        button_row.add_widget(self.recommend_button)
        button_row.add_widget(self.favorite_button)
        button_row.add_widget(self.view_favorites_button)
        button_row.add_widget(self.clear_favorites_button)
        button_row.add_widget(self.export_favorites_button)
        button_row.add_widget(self.exit_button)
        self.add_widget(button_row)


        self.results = Label(text='Game info and recommendations', size_hint=(1, 0.6), halign='left', valign='top',
                            markup=True, color=(1, 1, 1, 1))
        self.results.bind(size=self.results.setter('text_size'))
        self.results.bind(on_ref_press=self.open_hyperlink)

        self.favorites = []  # Store favorite games in memory

        scroll = ScrollView()
        scroll.add_widget(self.results)
        self.add_widget(scroll)

        self.df = pd.read_csv("../data/cleaned_games.csv") # Load preprocessed data
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
        price_val = row.get('price') or row.get('price_final')
        price = "Free" if pd.isna(price_val) or price_val == 0 else f"${price_val:.2f}"
        release = row.get('release_date') or row.get('date_release') or ''
        raw_date = str(release)[:10]
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
            date = parsed_date.strftime("%m-%d-%Y")
        except:
            date = raw_date

        reviews = row.get('user_reviews', 'N/A')
        platforms = [p for p, v in zip(['🖥 Windows', '🍏 macOS', '🐧 Linux'], [row.get('win'), row.get('mac'), row.get('linux')]) if v]
        app_link = f"https://store.steampowered.com/app/{row['app_id']}/"
        rating_label = str(row.get('rating', '')).strip().lower()

        rating_map = {
            "overwhelmingly positive": 5.0,
            "very positive": 4.5,
            "mostly positive": 4.0,
            "positive": 3.5,
            "mixed": 3.0,
            "mostly negative": 2.0,
            "very negative": 1.5,
            "overwhelmingly negative": 1.0
        }

        rating_value = rating_map.get(rating_label, None)
        if rating_value:
            full_stars = int(rating_value)
            half_star = "½" if rating_value - full_stars >= 0.5 else ""
            stars = "⭐" * full_stars + half_star
            rating_text = f"{rating_value}/5.0 {stars} ({row['rating']})"
        else:
            rating_text = "Not Rated"


        output = (
            f"[b]{row['title']}[/b]\n"
            f"[color=#ffa726]App ID:[/color] {row['app_id']} | [ref={app_link}][color=#42a5f5][u]Open on Steam[/u][/color][/ref]\n"
            f"[color=#80cbc4]Mood:[/color] {row.get('mood', 'unknown')}\n"
            f"[color=#ce93d8]Platform:[/color] {', '.join(platforms)}\n"
            f"[color=#ffcc80]Price:[/color] {price}\n"
            f"[color=#fbc02d]Rating:[/color] {rating_text}\n"
            f"[color=#f4ff81]Total Reviews:[/color] {reviews}\n"
            f"[color=#c5e1a5]Release Date:[/color] {date}\n"
            f"[i][color=#bdbdbd]Description:[/color] {row.get('description', '')}[/i]\n"
        )
        self.results.text = output

    def get_recommendations(self, instance):
        title = self.input_field.text.strip().lower()
        app_id = self.appid_input.text.strip()
        mood = self.mood_selector.text if self.mood_selector.text != "None" else None
        genre = self.genre_selector.text if self.genre_selector.text != "None" else None

        # Generate recommendations based on input title or App ID

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
            recommendations = self.df.iloc[indices[0][1:6]]
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

            review_col = 'user_reviews' if 'user_reviews' in filtered_df.columns else (
                'user_reviews_x' if 'user_reviews_x' in filtered_df.columns else None
            )

            if review_col:
                recommendations = filtered_df.sort_values(by=review_col, ascending=False).head(5)
            else:
                recommendations = filtered_df.head(5)


        if recommendations.empty:
            self.show_popup("No Results", "No games found for selected filters.")
            return

        self.results.text = self._format_dual_column_output("Recommended Games", recommendations)

    def _format_dual_column_output(self, title, df):
        left, right = "", ""
        # Show up to 5 recommended games, split into two columns
        for i, (_, row) in enumerate(df.head(5).iterrows()):
            number = f"{i+1}."
            price_val = row.get('price') or row.get('price_final')
            price = "Free" if pd.isna(price_val) or price_val == 0 else f"${price_val:.2f}"

            # Format the release date as MM-DD-YYYY
            release_val = row.get('release_date') or row.get('date_release') or ''
            raw_date = str(release_val)[:10]
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
                date = parsed_date.strftime("%m-%d-%Y")
            except:
                date = raw_date

            review_val = row.get('user_reviews') or row.get('user_reviews_x')
            reviews = f"{int(review_val)} reviews" if pd.notna(review_val) else "N/A"
            platforms = [p for p, v in zip(['🖥 Windows', '🍏 macOS', '🐧 Linux'],
                                    [row.get('win'), row.get('mac'), row.get('linux')]) if v]
            app_link = f"https://store.steampowered.com/app/{row['app_id']}/"

            # Rating
            rating_label = str(row.get('rating', '')).strip().lower()
            rating_map = {
                "overwhelmingly positive": 5.0, "very positive": 4.5, "mostly positive": 4.0,
                "positive": 3.5, "mixed": 3.0, "mostly negative": 2.0,
                "very negative": 1.5, "overwhelmingly negative": 1.0
            }
            rating_value = rating_map.get(rating_label, None)
            if rating_value:
                full_stars = int(rating_value)
                half_star = "½" if rating_value - full_stars >= 0.5 else ""
                stars = "⭐" * full_stars + half_star
                rating_text = f"{rating_value}/5.0 {stars}"
            else:
                rating_text = row.get('rating', 'Not Rated')


            # Info block
            info = (
                f"{number} [ref={app_link}][color=#42a5f5][u]{row['title']}[/u][/color][/ref]\n"
                f"   App ID: {row['app_id']} | {', '.join(platforms)} | {price} | Rating: {rating_text} | {reviews} | Released: {date}\n\n"
            )


            if i < 7:
                left += info
            else:
                right += info

        return f"[b]{title}[/b]\n\n{left}{right}"

    def save_to_favorites(self, instance):
        title = self.input_field.text.strip().lower()
        app_id = self.appid_input.text.strip()

        if not title and not app_id:
            self.show_popup("Missing Input", "Enter a game title or App ID to save.")
            return

        game = pd.DataFrame()
        if app_id.isdigit():
            game = self.df[self.df['app_id'] == int(app_id)]
        elif title:
            game = self.df[self.df['title'].str.lower() == title]

        if game.empty:
            self.show_popup("Not Found", "Game not found.")
            return

        game_title = game.iloc[0]['title']
        if game_title in self.favorites:
            self.show_popup("Already Saved", f"⭐ {game_title} is already in your favorites.")
        else:
            self.favorites.append(game_title)
            self.show_popup("Saved", f"⭐ {game_title} has been added to your favorites!")
    def view_favorites(self, instance):
        if not self.favorites:
            self.show_popup("Favorites", "⭐ You haven't saved any games yet.")
            return

        favorites_text = "\n".join([f"• {title}" for title in self.favorites])
        self.show_popup("⭐ Your Favorite Games", favorites_text)
    def clear_favorites(self, instance):
        if not self.favorites:
            self.show_popup("Nothing to Clear", "⭐ Your favorites list is already empty.")
            return

        self.favorites.clear()
        self.show_popup("Cleared", "🗑 Your favorites list has been cleared.")

    def export_favorites(self, instance):
        if not self.favorites:
            self.show_popup("Export Failed", "⭐ No favorites to export.")
            return

        try:
            with open("favorites.txt", "w", encoding='utf-8') as file:
                for title in self.favorites:
                    file.write(f"{title}\n")
            self.show_popup("Exported", "💾 Favorites saved to 'favorites.txt'.")
        except Exception as e:
            self.show_popup("Error", f"Failed to export: {str(e)}")

    def open_hyperlink(self, instance, ref):
            webbrowser.open(ref)

    def exit_app(self, instance):
            App.get_running_app().stop()
class GameApp(App):
        def build(self):
            return RecommenderUI()
    
if __name__ == '__main__':
    GameApp().run()
