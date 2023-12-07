import customtkinter as ctk
from tkinter import messagebox
import subprocess
import mysql.connector

class UserAuthentication:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def _connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def login(self, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()

        conn = self._connect()
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE username = %s AND password = %s"

        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        conn.close()

        if result:
            if username == "iah" and password == "12":
                messagebox.showinfo("Login Successful", "You have successfully logged in.")
                Admin()
            else:
                messagebox.showinfo("Login Successful", "You have successfully logged in.")
                HomePage()
        else:
            messagebox.showerror("Login Failed", "Login failed. Please check your credentials.")

    def register(self, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Registration Error", "Username and password are required.")
            return

        conn = self._connect()
        cursor = conn.cursor()

        check_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            messagebox.showerror("Registration Error", "Username already exists.")
        else:
            insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            try:
                cursor.execute(insert_query, (username, password))
                conn.commit()
                messagebox.showinfo("Registration Successful", "You have successfully registered.")
            except mysql.connector.Error as err:
                messagebox.showerror("Registration Failed", f"Registration failed: {err}")

        cursor.close()
        conn.close()

def HomePage():
    login_window.destroy()
    subprocess.run(['python', 'HomePage.py'])

def Admin():
    login_window.destroy()
    subprocess.run(['python', 'Admin.py'])

login_window = ctk.CTk()
login_window.title('PawfectMatch')
login_window.geometry('450x300+710+360')
login_window.iconbitmap("paw-icon.ico")
ctk.set_appearance_mode("dark")

login_window.resizable(width=False, height=False)

login_frame = ctk.CTkFrame(login_window, fg_color='#213256')
login_frame.place(relwidth=1, relheight=1)

login_font = ctk.CTkFont(family='Balsamiq Sans', size=52, weight='bold')

login_label = ctk.CTkLabel(login_frame, text='PawfectMatch', text_color="#FFFFFF", pady=14, font=login_font)
login_label.place(relx=0.5, rely=0, anchor='n')

entry_font = ctk.CTkFont(family='Balsamiq Sans', size=16, weight='bold')

username_entry = ctk.CTkEntry(login_frame, placeholder_text='Username', width=280, height=35,
                               text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF',
                               border_color='#213256', corner_radius=50, font=entry_font)

password_entry = ctk.CTkEntry(login_frame, placeholder_text='Password', width=280, height=35,
                               text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF',
                               corner_radius=50, border_color='#213256', show="*", font=entry_font)

button_font = ctk.CTkFont(family='Balsamiq Sans', size=17, weight='bold')

username_entry.place(relx=0.5, rely=0.35, anchor='n')
password_entry.place(relx=0.5, rely=0.51, anchor='n')

authentication = UserAuthentication("127.0.0.1", "root", "", "pawfectmatch")

login_button = ctk.CTkButton(login_frame, text='Login', text_color='#FFFFFF', fg_color='#FF847A',
                              font=button_font, corner_radius=200, hover_color='#BD5145', width=130,
                              height=40, command=lambda: authentication.login(username_entry, password_entry))

register_button = ctk.CTkButton(login_frame, text='Register', text_color='#FFFFFF', fg_color='#07CDC2',
                                 font=button_font, corner_radius=200, hover_color='#0D8680', width=130,
                                 height=40, command=lambda: authentication.register(username_entry, password_entry))

login_button.place(relx=0.33, rely=0.72, anchor='n')
register_button.place(relx=0.67, rely=0.72, anchor='n')

login_window.mainloop()
