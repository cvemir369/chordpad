# temp rezolucija
from kivy.config import Config
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '650') #918 650

import sqlite3
import os
from kivy.clock import mainthread
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SwapTransition
from kivy.uix.layout import Layout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button


# create database file
con = sqlite3.connect("chordpad.db")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS chordpad (id TEXT NOT NULL, title TEXT NOT NULL, text TEXT)''')
con.commit()
con.close()

# # create db item
# con = sqlite3.connect("chordpad.db")
# cur = con.cursor()
# cur.execute(''' INSERT INTO chordpad (title, text) VALUES ('chordpad#2', 'C# D E') ''')
# con.commit()
# con.close()

current_pad_text = ''
current_pad_title = ''
current_pad_id = ''


class RenamePadDialog(Popup):
    def rename_chordpad(self):
        global current_pad_id, current_pad_title
        new_file_name = self.ids.rename_name.text
        if new_file_name.strip() == '':
            new_file_name = 'Untitled Chordpad'
        else:
            pass
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute('''UPDATE chordpad SET id = ?, title = ? WHERE id = ?''',
                    (new_file_name, new_file_name, current_pad_id))
        con.commit()
        con.close()
        current_pad_title = new_file_name
        current_pad_id = new_file_name
        self.dismiss()
        App.get_running_app().root.current = "success"
        App.get_running_app().root.get_screen("reading").ids.filename_rlabel.text = current_pad_title
        App.get_running_app().root.get_screen("editing").ids.filename_label.text = current_pad_title
            
    def current_pad_title(self):
        current_pad = f'Rename {current_pad_id}'
        return current_pad
    
    def rename_hint_text(self):
        return current_pad_id


class SaveAsDialog(Popup):  # save dialog popup
    def save_as(self):
        global current_pad_text, current_pad_title, current_pad_id
        file_name = self.ids.filename.text
        if file_name.strip() == '':
            file_name = 'Untitled Chordpad'
        else:
            pass
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute('''INSERT INTO chordpad (id, title, text) VALUES (?, ?, ?)''', (file_name, file_name, text_to_save))
        con.commit()
        con.close()
        current_pad_text = text_to_save
        current_pad_title = file_name
        current_pad_id = file_name
        self.dismiss()
        App.get_running_app().root.current = "success"
        App.get_running_app().root.get_screen("reading").ids.reading_label.text = current_pad_text
        App.get_running_app().root.get_screen("reading").ids.filename_rlabel.text = current_pad_title
        App.get_running_app().root.get_screen("editing").ids.filename_label.text = current_pad_title


class SaveChangesDialog(Popup):
    def save_changes(self):
        global current_pad_text
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute(''' UPDATE chordpad SET text = ? WHERE id = ? ''', (text_to_save, current_pad_id))
        con.commit()
        con.close()
        current_pad_text = text_to_save
        self.dismiss()
        App.get_running_app().root.current = "success"
        App.get_running_app().root.get_screen("reading").ids.reading_label.text = current_pad_text
        
    def current_pad_title(self):
        current_pad = f'Save changes to {current_pad_id}'
        return current_pad


class DeletePadDialog(Popup):
    def delete_pad(self):
        global current_pad_id, current_pad_title, current_pad_text
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute(''' DELETE FROM chordpad WHERE title = ? ''', (current_pad_id,))
        con.commit()
        con.close()
        self.dismiss()
        App.get_running_app().root.current = "success"
        current_pad_title = 'Untitled - Chordpad'
        current_pad_text = ''
        App.get_running_app().root.get_screen("reading").ids.reading_label.text = current_pad_text
        App.get_running_app().root.get_screen("editing").ids.chordpad.text = current_pad_text
        App.get_running_app().root.get_screen("reading").ids.filename_rlabel.text = current_pad_title
        App.get_running_app().root.get_screen("editing").ids.filename_label.text = current_pad_title
        
    def current_pad_title(self):
        current_pad = f'Delete {current_pad_id}'
        return current_pad


class MenuScreen(Screen):  # main menu screen
    @mainthread
    def on_enter(self):
        global current_pad_text, current_pad_title
        self.ids.pads.clear_widgets()
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        cur.execute(''' SELECT id, title, text FROM chordpad ''')
        for item in reversed(cur.fetchall()):
            pad_id = str(item[0])
            pad_title = item[1]
            button = Button(text=pad_title, size_hint=(1, 0.1))
            self.ids.pads.add_widget(button)
            self.ids[pad_id] = button
            button.bind(on_release=self.return_button_id_on_press)
        con.close()

    def return_button_id_on_press(self, instance):
        global current_pad_text, current_pad_id, current_pad_title
        con = sqlite3.connect("chordpad.db")
        cur = con.cursor()
        
        cur.execute(''' SELECT ? FROM chordpad''', (instance.text,))
        current_pad_title = cur.fetchone()[0]
        current_pad_id = list(self.ids.keys())[list(self.ids.values()).index(instance)]
        self.manager.get_screen("editing").ids.filename_label.text = current_pad_title
        self.manager.get_screen("reading").ids.filename_rlabel.text = current_pad_title
        cur.execute(''' SELECT text FROM chordpad WHERE id = ?''', (current_pad_id,))
        current_pad_text = cur.fetchone()[0]
        self.manager.get_screen("editing").ids.chordpad.text = current_pad_text
        self.manager.get_screen("reading").ids.reading_label.text = current_pad_text
        self.manager.current = "reading"
        con.close()

    def new_chordpad(self):
        global current_pad_text, current_pad_id, current_pad_title
        current_pad_text = ''
        current_pad_id = ''
        current_pad_title = "Untitled - Chordpad"
        self.manager.get_screen("editing").ids.chordpad.text = current_pad_text
        self.manager.get_screen("editing").ids.filename_label.text = current_pad_title
        self.manager.get_screen("reading").ids.filename_rlabel.text = current_pad_title

    def back_to_chordpad(self):  # set untitled if back to chordpad on start
        global current_pad_text, current_pad_title
        try:
            if current_pad_text == '':
                current_pad_title = 'Untitled - Chordpad'
                self.manager.get_screen("editing").ids.chordpad.text = current_pad_text
                self.manager.get_screen("editing").ids.filename_label.text = current_pad_title
                self.manager.get_screen("reading").ids.filename_rlabel.text = current_pad_title
        except:
            pass


class ChordpadScreen(Screen):  # editing mode screen
    def put_text(self, item):  # intro, verse, etc. auto enter ili ne
        if self.ids.chordpad.text == "":
            self.ids.chordpad.insert_text(f"{item}: ")
        else:
            self.ids.chordpad.insert_text(f"\n{item}: ")

    def check_if_saved(self):
        global text_to_save
        if self.ids.chordpad.text != "" and self.ids.filename_label.text == "Untitled - Chordpad":
            text_to_save = self.ids.chordpad.text
            SaveAsDialog().open()

        elif current_pad_text != self.ids.chordpad.text:
            text_to_save = self.ids.chordpad.text
            SaveChangesDialog().open()
        else:
            pass

    def delete_pad(self):
        if current_pad_title == 'Untitled - Chordpad':
            pass
        else:
            DeletePadDialog().open()

    def rename_chordpad(self):
        if current_pad_title == 'Untitled - Chordpad':
            pass
        else:
            RenamePadDialog().open()

class ReadingModeScreen(Screen):
    def delete_pad(self):
        if current_pad_title == 'Untitled - Chordpad':
            pass
        else:
            DeletePadDialog().open()


class SuccessScreen(Screen):
    pass


class ScreenOrganize(ScreenManager):
    pass


class ChordpadApp(App):
    def build(self):
        return ScreenOrganize()    


if __name__ == '__main__':
    ChordpadApp().run()
