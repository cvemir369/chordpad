''''
* kada napravis novi cp u edit modu, ides na Save, treba da posle cuvanja
updatuje label na ime fajla
* kada je fajl otvoren, vratis se u menu i hoces opet da otvoris isti,
klikom na isti fajl nista se ne desava
'''

#temp rezolucija
#from kivy.config import Config
#Config.set('graphics', 'width', '423')
#Config.set('graphics', 'height', '918')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.layout import Layout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.stacklayout import StackLayout
from kivy.uix.popup import Popup
import os
import sqlite3

active_file = ""
file_name = ""

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

class SaveAsDialog(Popup): # save dialog popup
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


class ChordpadScreen(Screen): # editing mode screen
    def savetxt(self):
        global cptxt
        cptxt = self.ids.chordpad.text
        
    def put_text(self, item): # intro, verse, etc. auto enter ili ne
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


class MenuScreen(Screen): # main menu screen

    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(self.MenuItems(orientation='vertical'))
        
    class MenuItems(BoxLayout):
        def __init__(self, **kw):
            super().__init__(**kw)
            self.add_widget(Label(text="Chordpad by cvemir369", size_hint=(1, 0.1)))
            self.list_all_pads()
            self.add_widget(Button(text="New chordpad", size_hint=(1, 0.2)))
            self.add_widget(Button(text="Back to chordpad", size_hint=(1, 0.2)))
    
        def list_all_pads(self):
            con = sqlite3.connect("chordpad.db")
            cur = con.cursor()
            cur.execute(''' SELECT * FROM chordpad ''')
            for pad_title in cur.fetchall():
                self.add_widget(Button(text=(str(pad_title[0]))))
            con.close()

    def open_clicked(self, cp): # opens file in ReadingModeScreen (called from kv)
        global active_file, selected_file_path
        for selected_path in cp:
            selected_file_path = selected_path
            with open(selected_path, 'r') as f:
                active_file = f.read()
                return(active_file)

    def back_to_cp(self): # set untitled if back to chordpad on start
        if self.manager.get_screen("editing").ids.chordpad.text == "":
            self.manager.get_screen("editing").ids.filename_label.text = "Untitled - Chordpad"
            self.manager.get_screen("reading").ids.filename_rlabel.text = "Untitled - Chordpad"
        else:
            pass
        
    def set_filename_label(self): # set label for the opened file as filename
        for item in self.ids.filechooser.selection:
            item_split = item.split('\\')
            item_split = item_split[-1].split('.')
            self.manager.get_screen("editing").ids.filename_label.text = f"{item_split[0]} - Chordpad"
            self.manager.get_screen("reading").ids.filename_rlabel.text = f"{item_split[0]} - Chordpad"

    def save_changes(self):
        global active_file
        with open(os.path.join(gl(), f"{selected_file_path}"), "w") as f:
                f.write(cptxt)
        active_file = cptxt


class ReadingModeScreen(Screen):
    pass


class ScreenOrganize(ScreenManager):
    pass


class ChordpadApp(App):
    def build(self):
        return ScreenOrganize()


if __name__ == '__main__':
    ChordpadApp().run()
