import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.lang import Builder
import random

# Define the ScreenManager *before* loading the KV file
class WindowManager(ScreenManager):
    pass

# First Page (Welcome Screen)
class FirstWindow(Screen):
    pass

# Second Page (User Input)
class SecondWindow(Screen):
    name_input = ObjectProperty(None)
    email_input = ObjectProperty(None)
    games_played_input = ObjectProperty(None)
    mood_input = ObjectProperty(None)

    def submit_info(self):
        # Validate inputs
        if not self.name_input.text.strip() or not self.games_played_input.text.strip() or not self.mood_input.text.strip():
            print("Please fill in all required fields.")
            return

        # Pass user input to the third page
        recommendations_screen = self.manager.get_screen("third")
        recommendations_screen.user_name = self.name_input.text.strip()
        recommendations_screen.played_games = [game.strip() for game in self.games_played_input.text.split(',') if game.strip()]
        recommendations_screen.user_mood = self.mood_input.text.strip().lower()
        recommendations_screen.generate_recommendations()

        # Clear input fields
        self.name_input.text = ""
        self.email_input.text = ""
        self.games_played_input.text = ""
        self.mood_input.text = ""

# Third Page (Recommendations)
class ThirdWindow(Screen):
    recommendation_text = StringProperty("Your recommendations will appear here.")
    user_name = StringProperty("")
    played_games = ListProperty([])
    user_mood = StringProperty("")

    def on_enter(self):
        self.generate_recommendations()

    def generate_recommendations(self):
        # Simple placeholder for game recommendations
        game_data = {
            "relaxed": ["Stardew Valley", "Animal Crossing", "Terraria", "Slime Rancher"],
            "intense": ["Doom Eternal", "Cyberpunk 2077", "Sekiro: Shadows Die Twice", "Apex Legends"],
            "emotional": ["The Last of Us Part II", "Life is Strange", "To the Moon", "What Remains of Edith Finch"],
            "scary": ["Resident Evil Village", "Outlast", "Amnesia: The Dark Descent", "Phasmophobia"],
            "strategic": ["Civilization VI", "StarCraft II", "XCOM 2", "Crusader Kings III"],
            "funny": ["Portal 2", "Untitled Goose Game", "Borderlands 3", "Human: Fall Flat"]
        }
        recommendations = set()
        for played_game in self.played_games:
            if played_game.lower() in [game.lower() for sublist in game_data.values() for game in sublist]:
                print(f"User has played: {played_game}")
                # Add some related games based on mood
                if self.user_mood in game_data:
                    potential_recommendations = [game for game in game_data[self.user_mood] if game.lower() not in [pg.lower() for pg in self.played_games]]
                    recommendations.update(potential_recommendations)
                break  # Just give one recommendation based on played game for now

        if not recommendations and self.user_mood in game_data:
            recommendations.update(random.sample(game_data[self.user_mood], min(3, len(game_data[self.user_mood]))))
        elif not recommendations:
            recommendations.add("No specific recommendations found based on your input.")

        recommendation_string = f"Hello {self.user_name}, based on your mood '{self.user_mood}' and games played '{', '.join(self.played_games)}', here are your recommendations:\n\n" + "\n".join([f"- {rec}" for rec in recommendations])
        self.recommendation_text = recommendation_string

# Main App
class GameRecommendationApp(App):
    def build(self):
        # Load KV file or screens programmatically
        return Builder.load_file("gamerecommendationapp.kv")

if __name__ == "__main__":
    # Ensure the KV file is loaded
    Builder.load_file("gamerecommendationapp.kv")
    GameRecommendationApp().run()