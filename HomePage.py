import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import subprocess
import mysql.connector
from customtkinter.windows.widgets.image import CTkImage

class AdoptionApp:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="pawfectmatch"
        )
        self.cursor = self.conn.cursor()

        self.create_survey_table()

        self.dog_buttons = []

        self.window = ctk.CTk()
        self.window.title('PawfectMatch')
        self.window.geometry('800x570+535+220')
        self.window.iconbitmap("paw-icon.ico")
        ctk.set_appearance_mode("dark")

        self.window.resizable(width=False, height=False)

        self.window_frame = ctk.CTkFrame(self.window, fg_color='#213256',)
        self.window_frame.place(relwidth=1, relheight=1)

        self.dog_frame = ctk.CTkScrollableFrame(self.window, fg_color='#213256', scrollbar_button_color='#FF847A', 
                                                scrollbar_button_hover_color='#FF847A')
        self.dog_frame.place(relwidth=.85, relheight=.72, anchor='n', relx=0.5, rely=0.25)

        self.dog_font = ctk.CTkFont(family='Balsamiq Sans', size=30, weight='bold')

        self.dog_label = ctk.CTkLabel(self.window_frame, text='List of Dogs', text_color="#FFFFFF", fg_color='#FF847A',
                                corner_radius=30, width=350, font=self.dog_font)
        self.dog_label.place(relx=0.5, rely=0.04, anchor='n')

        self.back_font = ctk.CTkFont(family='Balsamiq Sans', size=18, weight='bold')

        self.back_button = ctk.CTkButton(self.window_frame, font=self.back_font, text='Log Out', width=125, 
                                        text_color='#FFFFFF', fg_color='#BD5145', hover_color='#BD4235', command=self.back)
        self.back_button.place(relx=0.036, rely=0.05, anchor='nw') 

        self.search_font = ctk.CTkFont(family='Balsamiq Sans', size=18, weight='bold')
        self.search2_font = ctk.CTkFont(family='Balsamiq Sans', size=14, weight='bold')

        self.search_category = ctk.CTkComboBox(self.window_frame, font=self.search_font, width=230, 
                                            dropdown_font=self.search2_font, values=["Breed", "Age", "Gender", "Color"],
                                            text_color="#213256", dropdown_text_color="#213256", 
                                            dropdown_fg_color='#FFFFFF', dropdown_hover_color='#FF847A', 
                                            fg_color='#FFFFFF', border_color='#FF847A', button_color='#FF847A', 
                                            state="readonly")
        self.search_category.place(relx=0.035, rely=0.162, anchor='nw')
        self.search_category.set("Category")

        self.search_entry = ctk.CTkEntry(self.window_frame, font=self.search_font, width=230, text_color='#293859', 
                                        border_color='#FF847A', fg_color='#FFFFFF')
        self.search_entry.place(relx=0.337, rely=0.162, anchor='nw')

        self.search_button = ctk.CTkButton(self.window_frame, font=self.search_font, text='Search', width=125, 
                                        text_color='#FFFFFF', fg_color='#FF847A', hover_color='#BD5145', 
                                        command=self.search_dogs)
        self.search_button.place(relx=0.64, rely=0.162, anchor='nw')

        self.clear_button = ctk.CTkButton(self.window_frame, font=self.search_font, text='Clear', width=125, 
                                        text_color='#FFFFFF', fg_color='#FF847A', hover_color='#BD5145', 
                                        command=self.clear_filters)
        self.clear_button.place(relx=0.81, rely=0.162, anchor='nw')

        self.dog_buttons, _ = self.create_dog_buttons()

    def create_survey_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS survey (
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

    def adopt_dog(self, dog_id, dog_name):
        response = messagebox.askquestion("Confirmation", f"Are you sure you want to adopt {dog_name}?")

        if response == 'yes':
            self.show_survey_form(dog_id, dog_name)
            self.window.close()
        else:
            pass

    def show_survey_form(self, dog_id, dog_name):
        survey_window = tk.Toplevel(self.window)
        survey_window.title("Adoption Survey")
        survey_window.geometry('883x628+535+220')
        survey_window.grab_set()
        survey_window.resizable(width=False, height=False)

        survey_frame = ctk.CTkScrollableFrame(survey_window, fg_color='#213256')
        survey_frame.place(relwidth=1, relheight=1)

        survey_label = ctk.CTkLabel(survey_frame, text="Survey Form", font=('Balsamiq Sans', 45, 'bold'))
        survey_label.grid(row=0, column=0, columnspan=5, pady=10)

        submit_font = ctk.CTkFont(family='Balsamiq Sans', size=16, weight='bold')

        adopter_name_entry = ctk.CTkEntry(survey_frame, font=submit_font, placeholder_text="Enter your username", width=330,
                                      height=35, text_color='#293859', placeholder_text_color='#213256',
                                      fg_color='#FFFFFF', border_color='#213256', corner_radius=50)
        adopter_name_entry.grid(row=1, column=0, padx=10, pady=5, sticky='w')

        email_entry = ctk.CTkEntry(survey_frame, font=submit_font, placeholder_text="Enter your email address", width=330,
                               height=35, text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF',
                               border_color='#213256', corner_radius=50)
        email_entry.grid(row=2, column=0, padx=10, pady=5, sticky='w')

        questions = [
            "1. Have you owned a dog before?",
            "2. Are you familiar with the responsibilities of dog ownership?",
            "3. Are you aware of the nutritional needs of a dog?",
            "4. Are you willing to provide veterinary care?",
            "5. Can you commit to regular walks and exercise?",
            "6. Are you willing to attend training classes?",
            "7. Can you provide a stable and loving home?",
            "8. Are you familiar with basic dog training principles?",
            "9. Are you comfortable with potential noise and mess?",
            "10. Are you equipped with a secure outdoor space for the dog?"
        ]

        question_vars = [tk.StringVar() for _ in range(len(questions))]

        for i, question_text in enumerate(questions):
            question_label = ctk.CTkLabel(survey_frame, text=question_text, font=('Balsamiq Sans', 16, 'bold'))
            question_label.grid(row=i + 3, column=0, columnspan=3, padx=10, pady=5, sticky='w')

            question_vars[i].set("")

            question_yes = ctk.CTkRadioButton(survey_frame, text="Yes", variable=question_vars[i], value="Yes",
                                          font=('Balsamiq Sans', 16, 'bold'), fg_color='#FFFFFF')
            question_yes.grid(row=i + 3, column=3, padx=50, pady=5)

            question_no = ctk.CTkRadioButton(survey_frame, text="No", variable=question_vars[i], value="No",
                                         font=('Balsamiq Sans', 16, 'bold'), fg_color='#FFFFFF')
            question_no.grid(row=i + 3, column=4, padx=0, pady=5)

            submit_button = ctk.CTkButton(survey_frame, text="Submit", font=('Balsamiq Sans', 18, 'bold'), width=150,
                                  height=30, text_color='#FFFFFF', fg_color='#FF847A', hover_color='#BD5145',
                                  corner_radius=10, command=lambda: self.process_survey(dog_id, dog_name,
                                                                                      adopter_name_entry.get(),
                                                                                      email_entry.get(),
                                                                                      [var.get() for var in
                                                                                       question_vars],
                                                                                      survey_window))
        submit_button.grid(row=len(questions) + 3, column=0, columnspan=5, pady=20)

        survey_window.mainloop()


    def process_survey(self, dog_id, dog_name, adopter_name, email, answers, survey_window):
        if not adopter_name.strip() or not email.strip():
            messagebox.showinfo("Incomplete Form", "Please answer all the questions.")
            return

        if any(answer == "" for answer in answers):
            messagebox.showinfo("Incomplete Survey", "Please answer all the questions.")
            return
        else:
            try:
                self.cursor.execute('''
                    INSERT INTO survey (adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (adopter_name, email, dog_name, *answers))

                self.conn.commit()

                messagebox.showinfo("Wait for Approval", "Your adoption request has been submitted.")

                survey_window.destroy()

            except mysql.connector.Error as err:
                print(f"Error: {err}")
                messagebox.showerror("Database Error", "An error occurred while saving the survey data. Please try again later.")

    def show_dog_details(self, dog_id, image_path):
        details_window = tk.Toplevel(self.window)
        details_window.title("Dog Details")
        details_window.geometry('550x350+710+380')

        details_window.resizable(width=False, height=False)

        details_frame = ctk.CTkFrame(details_window, fg_color='#4E6B9F')
        details_frame.place(relwidth=1, relheight=1)

        img = Image.open(image_path)
        photo = CTkImage(img, size=(200, 200))  
    
        img_label = ctk.CTkLabel(details_frame, image=photo, text='')
        img_label.photo = photo
        img_label.place(relwidth=0.52, relheight=0.82)

        self.cursor.execute('SELECT * FROM dogs WHERE id = %s', (dog_id,))
        dog_details = self.cursor.fetchone()

        details_str = (
            f"Name: {dog_details[1]}\n"
            f"Breed: {dog_details[2]}\n"
            f"Age: {dog_details[3]}\n"
            f"Weight: {dog_details[4]} kg\n"
            f"Gender: {dog_details[5]}\n"
            f"Color: {dog_details[6]}\n"
        )

        details_font = ctk.CTkFont(family='Balsamiq Sans', size=19, weight='bold')
        details2_font = ctk.CTkFont(family='Balsamiq Sans', size=19, weight='bold')

        details_label = ctk.CTkLabel(details_frame, text=details_str, justify='left', font=details_font)
        details_label.place(relx=0.53, rely=0.09)

        adopt_button = ctk.CTkButton(details_frame,
            text="Adopt",
            font=details2_font,
            command=lambda id=dog_id, name=dog_details[1], window=details_window: self.adopt_dog(id, name),
            width=150,
            height=30,
            text_color='#FFFFFF',
            fg_color='#FF847A',
            hover_color='#BD5145'
        )

        adopt_button.place(relx=0.55, rely=0.8)

        back_button = ctk.CTkButton(details_frame, text="Back", font=details_font, command=details_window.destroy, 
                                width=150, height=30, text_color='#FFFFFF', fg_color='#FF847A', hover_color='#BD5145')
        back_button.place(relx=0.15, rely=0.8)

        details_window.mainloop()


    def create_dog_buttons(self, dogs=None):
        if dogs is None:
            self.cursor.execute('SELECT id, name, image_path FROM dogs')
            dogs = self.cursor.fetchall()

        for button in self.dog_buttons:
            button.destroy()

        button_list = []
        image_list = []

        for i, dog in enumerate(dogs):
            dog_id, dog_name, image_path = dog
            img = Image.open(image_path)
            img = CTkImage(img, size=(160, 160))

            image_list.append(img)

            button = ctk.CTkButton(self.dog_frame, text=dog_name, image=img, compound=tk.TOP, fg_color='#213256',
                               bg_color='#213256', hover_color='#FF847A', font=('Balsamiq Sans', 23, 'bold'),
                               text_color='#FFFFFF', width=180, height=225, command=lambda id=dog_id,
                               img_path=image_path: self.show_dog_details(id, img_path))
            button.image = img
            button_list.append(button)

            row = i // 3
            col = i % 3
            button.grid(row=row, column=col, padx=15, pady=5)

        self.dog_buttons = button_list

        return button_list, image_list


    def search_dogs(self):
        search_term = self.search_entry.get().strip()
        category = self.search_category.get()

        if category == "Category":
            messagebox.showerror("Category Error", "Please select a valid category for the search.")
        elif category == "Age" and not search_term.isdigit():
            messagebox.showerror("Input Error", f"Please enter a valid number for {category}.")
        else:
            self.cursor.execute(f"SELECT id, name, image_path FROM dogs WHERE {category.lower()} = %s", (search_term,))
            dogs = self.cursor.fetchall()

            self.create_dog_buttons(dogs)

    def clear_filters(self):
        self.search_entry.delete(0, tk.END)
        self.search_category.set("Category")
        self.create_dog_buttons()

    def back(self):
        self.window.destroy()
        subprocess.run(['python', 'LoginForm.py'])

if __name__ == "__main__":
    app = AdoptionApp()
    app.window.mainloop()
