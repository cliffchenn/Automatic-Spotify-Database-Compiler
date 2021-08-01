from kivy.app import App 
from kivy.animation import Animation
from kivy.lang import Builder

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.stacklayout import StackLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

class MainWindow(Screen):
    pass 

# class Widgets(Widget): 
#     def popUp_btn(self):
#         show_popup()

# class PopUp(Screen):
#     pass


class SecondWindow(Screen):
    pass

class ThirdWindow(Screen):
    pass 

class FourthWindow(Screen):
    pass 

class WindowManager(ScreenManager):
    pass 


kv = Builder.load_file('mainApp.kv')

class MyMainApp(App):
    def build(self):
        return kv

    def save_code(self, code):
        txt_file = open(r'C:\Users\cliff\Documents\Python Projects\Test App\auth_code.txt', 'w')
        txt_file.write(code)
        txt_file.close() 

    def buffering(self, widget, *args):
        anim = Animation(background_color=(0,0,0,0), duration=1)
        anim += Animation(background_color=(1,1,1,1), duration=1)
        anim.start(widget)

# def show_popup(): 
#     show = PopUp()
#     PopUpWindow = Popup(title='Popup Window', content=show, size_hint=(None, None), size=(400,400))
#     PopUpWindow.open()


if __name__ == '__main__':
    MyMainApp().run()
