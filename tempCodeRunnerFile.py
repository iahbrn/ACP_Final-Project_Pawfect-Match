import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import mysql.connector
import subprocess
from PIL import Image, ImageTk
from customtkinter.windows.widgets.image import CTkImage

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def create_dogs_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dogs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(25),
                breed VARCHAR(25),
                age INT,
                weight DECIMAL(5, 1),
                gender VARCHAR(6),
                color VARCHAR(25),
                image_path VARCHAR(255)
            )
        ''')
        self.conn.commit()

    def create_approved_survey_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS approved_survey (
                adopter_name VARCHAR(255),
                email VARCHAR(255),
                dog_name VARCHAR(25),
                ans_1 VARCHAR(3),
                ans_2 VARCHAR(3),
                ans_3 VARCHAR(3),
                ans_4 VARCHAR(3),
                ans_5 VARCHAR(3),
                ans_6 VARCHAR(3),
                ans_7 VARCHAR(3),
                ans_8 VARCHAR(3),
                ans_9 VARCHAR(3),
                ans_10 VARCHAR(3)
            )
        ''')
        self.conn.commit()

image_path = tk.StringVar()

class DogManager:
    def __init__(self, cursor, conn, window, dog_list, name_entry, breed_entry, age_entry, weight_entry, gender_entry, color_entry, button_frame):
        self.cursor = cursor
        self.conn = conn
        self.window = window
        self.dog_list = dog_list
        self.name_entry = name_entry
        self.breed_entry = breed_entry
        self.age_entry = age_entry
        self.weight_entry = weight_entry
        self.gender_entry = gender_entry
        self.color_entry = color_entry
        self.button_frame = button_frame

    def insert_dog(self):
        name = self.name_entry.get()
        breed = self.breed_entry.get()
        age_text = self.age_entry.get()
        weight_text = self.weight_entry.get()
        gender = self.gender_entry.get()
        color = self.color_entry.get()

        if not name or not breed or not age_text or not weight_text or not gender or not color:
            messagebox.showerror("Error", "All fields must be filled.")
        else:
            try:
                age = int(age_text)
                weight = float(weight_text)
            except ValueError:
                messagebox.showerror("Error", "Age and Weight must be valid numbers.")
                return

            image_path_value = image_path.get()
            self.cursor.execute('''
                INSERT INTO dogs (name, breed, age, weight, gender, color, image_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (name, breed, age, weight, gender, color, image_path_value))

            self.conn.commit()

            self.update_dog_list()
            self.clear_entries()

    def update_dog_list(self):
        try:
            self.dog_list.delete(*self.dog_list.get_children())

            self.cursor.execute('SELECT id, name, breed, age, weight, gender, color, image_path FROM dogs')

            rows = self.cursor.fetchall()

            for row in rows:
                self.dog_list.insert("", "end", values=row)
                self.display_image(row[-1])
        except mysql.connector.Error as err:
            print(f"Database error: {err}")

    def clear_dog_list(self):
        for row in self.dog_list.get_children():
            self.dog_list.delete(row)

    def on_select(self, event):
        selected_item = self.dog_list.selection()
        if selected_item:
            dog_id = self.dog_list.item(selected_item)["values"][0]
            image_path = self.dog_list.item(selected_item)["values"][-1]
            self.show_image(image_path)

    def clear_entries(self):
        for entry_widget in [self.name_entry, self.breed_entry, self.age_entry, self.weight_entry, self.gender_entry, self.color_entry]:
            if entry_widget.get():
                entry_widget.delete(0, tk.END)\
                
    def update_dog(self):
        selected_item = self.dog_list.selection()
        if not selected_item:
            return

        dog_id = self.dog_list.item(selected_item)["values"][0]

        self.cursor.execute('SELECT name, breed, age, weight, gender, color FROM dogs WHERE id=%s', (dog_id,))
        row = self.cursor.fetchone()

        if not row:
            return

        name = self.name_entry.get()
        breed = self.breed_entry.get()
        gender = self.gender_entry.get()
        color = self.color_entry.get()

        age = None
        weight = None

        if name:
            self.cursor.execute('UPDATE dogs SET name=%s WHERE id=%s', (name, dog_id))
        if breed:
            self.cursor.execute('UPDATE dogs SET breed=%s WHERE id=%s', (breed, dog_id))
        if gender:
            self.cursor.execute('UPDATE dogs SET gender=%s WHERE id=%s', (gender, dog_id))
        if color:
            self.cursor.execute('UPDATE dogs SET color=%s WHERE id=%s', (color, dog_id))

        age_text = self.age_entry.get()
        weight_text = self.weight_entry.get()

        if age_text:
            try:
                age = float(age_text)
                self.cursor.execute('UPDATE dogs SET age=%s WHERE id=%s', (age, dog_id))
            except ValueError:
                pass

        if weight_text:
            try:
                weight = float(weight_text)
                self.cursor.execute('UPDATE dogs SET weight=%s WHERE id=%s', (weight, dog_id))
            except ValueError:
                pass

        image_path_value = image_path.get()
        if image_path_value:
            self.cursor.execute('UPDATE dogs SET image_path=%s WHERE id=%s', (image_path_value, dog_id))

        self.conn.commit()
        self.update_dog_list()
        self.clear_entries()

    def delete_dog(self):
        selected_item = self.dog_list.selection()
        if not selected_item:
            return

        dog_id = self.dog_list.item(selected_item)["values"][0]

        self.cursor.execute('DELETE FROM dogs WHERE id=%s', (dog_id,))
        self.conn.commit()
        self.update_dog_list()
        self.clear_entries()

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.ppm")])
        image_path.set(file_path)

        image_label = tk.Label(self.button_frame)
        image_label.place(relx=0.08, rely=0.55)
        photo = self.display_image(file_path)

        if photo:
            image_label.config(image=photo)
            image_label.image = photo
        else:
            messagebox.showerror("Image Error", "Failed to display the selected image.")

        self.display_image(file_path)

    def display_image(self, image_path):
        if image_path:
            try:
                image = Image.open(image_path)
                image = image.resize((230, 230))
                photo = ImageTk.PhotoImage(image)
                return photo

            except Exception as e:
                messagebox.showerror("Image Error", f"Error displaying image: {str(e)}")
        return None

    def show_image(self):
        selected_item = self.dog_list.selection()

        image_label = tk.Label(self.button_frame)
        image_label.place(relx=0.08, rely=0.55)
        
        if selected_item:
            image_path = self.dog_list.item(selected_item)["values"][-1]  # Assuming the last column is image_path
            photo = self.display_image(image_path)
            if photo:
                image_label.config(image=photo)
                image_label.image = photo
            else:
                messagebox.showerror("Error!", "No image has been associated with this dog.")
        else:
            messagebox.showerror("No dog selected", "Please select a dog from the list before clicking 'Show Image'.")

    def back(self):
        self.window.destroy()
        subprocess.run(['python', 'LoginForm.py'])
