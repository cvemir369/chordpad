# temp rezolucija
from kivy.config import Config
Config.set('graphics', 'width', '423')
Config.set('graphics', 'height', '918')

import sqlite3
import os
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.clock import mainthread

# create database file
con = sqlite3.connect("chordpad.db")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS chordpad (title, text)''')
con.commit()
con.close()

# # create db item
# con = sqlite3.connect("chordpad.db")
# cur = con.cursor()
# cur.execute(''' INSERT INTO chordpad VALUES ('chordpad#2', 'C# D E') ''')
# con.commit()
# con.close()


class SaveAsDialog(Popup):  # save dialog popup
    def save_as(self):
        global cptxt, file_name, active_file
        try:
            file_name = self.ids.filename.text
            with open(os.path.join(gl(), f"{file_name}.txt"), "w") as f:
                f.write(cptxt)
            active_file = cptxt
            self.dismiss()

        except:
            self.ids.filename.hint_text = 'illegal filename'
            self.ids.filename.text = ''


class SaveChangesDialog(Popup):
    pass


class MenuScreen(Screen):  # main menu screen
    @mainthread
    def on_enter(self):
        global lista
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute(''' SELECT title FROM chordpad ''')
        # lista = []
        lista = cur.fetchall()
        print(lista)
        cur.execute(''' SELECT title FROM chordpad ''')
        for item in cur.fetchall():
            pad_title = item[0]
            button = Button(text=pad_title)
            self.ids.pads.add_widget(button)
            self.ids[pad_title] = button
            button.bind(on_press=self.return_button_id_on_press)
            button.bind(on_release=self.open_clicked)
        con.close()

    def open_clicked(self, *args):  # opens file in ReadingModeScreen (called from kv)
        global pad_title
        self.manager.get_screen("editing").ids.filename_label.text = 'pad_title'
        self.manager.current = "editing"

    def return_button_id_on_press(self, *args):
        print(self.ids)

    def back_to_cp(self):  # set untitled if back to chordpad on start
        pass

    def set_filename_label(self):  # set label for the opened file as filename
        pass

    def save_changes(self):
        pass


class ChordpadScreen(Screen):  # editing mode screen
    def savetxt(self):
        global cptxt
        cptxt = self.ids.chordpad.text

    def put_text(self, item):  # intro, verse, etc. auto enter ili ne
        if self.ids.chordpad.text == "":
            self.ids.chordpad.insert_text(f"{item}: ")
        else:
            self.ids.chordpad.insert_text(f"\n{item}: ")

    def check_if_saved(self):
        if self.ids.chordpad.text != "" and self.ids.filename_label.text == "Untitled - Chordpad":
            self.savetxt()
            SaveAsDialog().open()

        elif active_file != self.ids.chordpad.text:
            self.savetxt()
            SaveChangesDialog().open()

        else:
            self.manager.get_screen("menu").ids.filechooser._update_files()
            self.manager.current = "menu"


class ReadingModeScreen(Screen):
    pass


class ScreenOrganize(ScreenManager):
    pass


class ChordpadApp(App):
    def build(self):
        return ScreenOrganize()


if __name__ == '__main__':
    ChordpadApp().run()
