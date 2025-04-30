import kivy 
from kivy.app import App 
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput 

class MyGrid(GridLayout):
    def __innit__(self, **kwargs):
        super(MyGrid, self).__innnit__(**kwargs)
        self.cols = 2
        self.widget(Label(text="Name: "))
        self.name = TextInput(multiline=False)
        self.add_widget(self.name)


class MyApp(App):
    def build(self):
        return MyGrid()

if __name__ == "__main__":
    MyApp().run()
