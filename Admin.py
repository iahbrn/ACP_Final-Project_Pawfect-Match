import tkinter as tk
import customtkinter as ctk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import mysql.connector
import subprocess
from PIL import Image, ImageTk
from customtkinter.windows.widgets.image import CTkImage

window = ctk.CTk()
window.title('PawfectMatch')
window.geometry("960x700+430+130")
window.iconbitmap("paw-icon.ico")
ctk.set_appearance_mode("dark")

window.resizable(width=False, height=False)

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="pawfectmatch"
)
cursor = conn.cursor()

conn2 = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="pawfectmatch"
)
cursor2 = conn2.cursor()

cursor.execute('''
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

conn.commit()

conn3 = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="pawfectmatch"
)
cursor3 = conn3.cursor()

cursor3.execute('''
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

conn3.commit()

image_path = tk.StringVar()

def insert_dog():
    name = name_entry.get()
    breed = breed_entry.get()
    age_text = age_entry.get()  # Get age as text
    weight_text = weight_entry.get()  # Get weight as text
    gender = gender_entry.get()
    color = color_entry.get()

    # Check if any of the fields is empty
    if not name or not breed or not age_text or not weight_text or not gender or not color:
        messagebox.showerror("Error", "All fields must be filled.")
    else:
        try:
            age = int(age_text)
            weight = float(weight_text)
        except ValueError:
            messagebox.showerror("Error", "Age and Weight must be valid numbers.")
            return
        
        image_path_value = image_path.get()  # Get the selected image path
        cursor.execute('''
            INSERT INTO dogs (name, breed, age, weight, gender, color, image_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (name, breed, age, weight, gender, color, image_path_value))

        conn.commit()

        update_dog_list()
        clear_entries()

def update_dog_list():
    try:
        dog_list.delete(*dog_list.get_children())

        cursor.execute('SELECT id, name, breed, age, weight, gender, color, image_path FROM dogs')

        rows = cursor.fetchall()

        for row in rows:
            dog_list.insert("", "end", values=row)
            display_image(row[-1])  
    except mysql.connector.Error as err:
        print(f"Database error: {err}")

def clear_dog_list():
    for row in dog_list.get_children():
        dog_list.delete(row)
        
def on_select(event):
    selected_item = dog_list.selection()
    if selected_item:
        dog_id = dog_list.item(selected_item)["values"][0]
        # Retrieve the image path
        image_path = dog_list.item(selected_item)["values"][-1] 
        show_image(image_path)

def clear_entries():
    for entry_widget in [name_entry, breed_entry, age_entry, weight_entry, gender_entry, color_entry]:
        if entry_widget.get():
            entry_widget.delete(0, tk.END)


def update_dog():
    selected_item = dog_list.selection()
    if not selected_item:
        return 

    dog_id = dog_list.item(selected_item)["values"][0]

    cursor.execute('SELECT name, breed, age, weight, gender, color FROM dogs WHERE id=%s', (dog_id,))
    row = cursor.fetchone()

    if not row:
        return

    name = name_entry.get()
    breed = breed_entry.get()
    gender = gender_entry.get()
    color = color_entry.get()

    age = None
    weight = None

    if name:
        cursor.execute('UPDATE dogs SET name=%s WHERE id=%s', (name, dog_id))
    if breed:
        cursor.execute('UPDATE dogs SET breed=%s WHERE id=%s', (breed, dog_id))
    if gender:
        cursor.execute('UPDATE dogs SET gender=%s WHERE id=%s', (gender, dog_id))
    if color:
        cursor.execute('UPDATE dogs SET color=%s WHERE id=%s', (color, dog_id))

    age_text = age_entry.get()
    weight_text = weight_entry.get()

    if age_text:
        try:
            age = float(age_text)
            cursor.execute('UPDATE dogs SET age=%s WHERE id=%s', (age, dog_id))
        except ValueError:
            pass  

    if weight_text:
        try:
            weight = float(weight_text)
            cursor.execute('UPDATE dogs SET weight=%s WHERE id=%s', (weight, dog_id))
        except ValueError:
            pass 

    image_path_value = image_path.get()  
    if image_path_value:
            cursor.execute('UPDATE dogs SET image_path=%s WHERE id=%s', (image_path_value, dog_id))

    conn.commit()
    update_dog_list()
    clear_entries()

def delete_dog():
    selected_item = dog_list.selection()
    if not selected_item:
        return  

    dog_id = dog_list.item(selected_item)["values"][0]

    cursor.execute('DELETE FROM dogs WHERE id=%s', (dog_id,))
    conn.commit()
    update_dog_list()
    clear_entries()

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.ppm")])
    image_path.set(file_path)

    image_label = tk.Label(button_frame)
    image_label.place(relx=0.08, rely=0.55)
    photo = display_image(file_path)

    if photo:
        image_label.config(image=photo)
        image_label.image = photo
    else:
        messagebox.showerror("Image Error", "Failed to display the selected image.")

    display_image(file_path)

def display_image(image_path):
    if image_path:
        try:
            image = Image.open(image_path)
            image = image.resize((230, 230)) 
            photo = ImageTk.PhotoImage(image)
            return photo
        
        except Exception as e:
            messagebox.showerror("Image Error", f"Error displaying image: {str(e)}")
    return None

def show_image():
    selected_item = dog_list.selection()

    image_label = tk.Label(button_frame)
    image_label.place(relx=0.08, rely=0.55)
    if selected_item:
        image_path = dog_list.item(selected_item)["values"][-1]  # Assuming the last column is image_path
        photo = display_image(image_path)
        if photo:
            image_label.config(image=photo)
            image_label.image = photo
        else:
            messagebox.showerror("Error!", "No image has been associated with this dog.")
    else:
        messagebox.showerror("No dog selected", "Please select a dog from the list before clicking 'Show Image'.")

def back():
    window.destroy()
    subprocess.run(['python', 'LoginForm.py'])

tab_view = ctk.CTkTabview(window, anchor='w', fg_color='#213256')
tab_view.place(relwidth=1, relheight=1)

dog_tab = tab_view.add("Dogs")
adopt_tab = tab_view.add("Pending")
approve_tab = tab_view.add("Approved")

# Create a frame for the "Dogs" tab
dog_frame = ctk.CTkFrame(dog_tab, fg_color='#213256')
dog_frame.place(relwidth=1, relheight=1)

label_font = ctk.CTkFont(family='Balsamiq Sans', size=35, weight='bold')
dog_label = ctk.CTkLabel(dog_frame, text='List of Dogs', text_color='#FFFFFF', font=label_font)
dog_label.place(relx=0.55, rely=0)

# Button Frame ajdaslkd
button_frame = ctk.CTkFrame(dog_frame, fg_color='#213256')
button_frame.place(relx=0, rely=0, relwidth=0.28, relheight=1)

img = Image.open("Admin.png")
img = CTkImage(img, size=(30, 30))

admin_font = ctk.CTkFont(family='Balsamiq Sans', size=24, weight='bold')

def view_dog():
    window.destroy()
    subprocess.run(['python', 'HomePage.py'])

admin_button = ctk.CTkButton(button_frame, text='Admin', fg_color='#213256', image=img, font=admin_font, hover_color='#213256', command=view_dog)
admin_button.place(relx=0, rely=0.02)

button_font = ctk.CTkFont(family='Balsamiq Sans', size=18, weight='bold')

add_button = ctk.CTkButton(button_frame, text='Add', fg_color='#FF847A', hover_color='#BD5145', 
                           font=button_font, width=180, height=38, corner_radius=20, command=insert_dog)
add_button.place(relx=0.15, rely=0.12)
update_button = ctk.CTkButton(button_frame, text='Update', fg_color='#FF847A', hover_color='#BD5145', 
                           font=button_font, width=180, height=38, corner_radius=20, command=update_dog)
update_button.place(relx=0.15, rely=0.2)
delete_button = ctk.CTkButton(button_frame, text='Delete', fg_color='#FF847A', hover_color='#BD5145', 
                           font=button_font, width=180, height=38, corner_radius=20, command=delete_dog)
delete_button.place(relx=0.15, rely=0.28)
view_button = ctk.CTkButton(button_frame, text='View', fg_color='#FF847A', hover_color='#BD5145', 
                           font=button_font, width=180, height=38, corner_radius=20, command=show_image)
view_button.place(relx=0.15, rely=0.36)
upload_button = ctk.CTkButton(button_frame, text='Upload', fg_color='#FF847A', hover_color='#BD5145', 
                           font=button_font, width=180, height=38, corner_radius=20, command=upload_image)
upload_button.place(relx=0.15, rely=0.44)
logout_button = ctk.CTkButton(button_frame, text='Log Out', fg_color='#213256', hover_color='#213256', 
                           font=button_font, width=180, height=38, corner_radius=20, command=back)
logout_button.place(relx=0.15, rely=0.92)

#List_Frame asdkjasd
list_frame = ctk.CTkFrame(dog_frame, fg_color='#213256')
list_frame.place(relx=0.265, rely=0.09, relwidth=0.719, relheight=0.642)

dog_list = ttk.Treeview(list_frame, columns=("ID", "Name", "Breed", "Age", "Weight", "Gender", "Color"))
heading_font = ctk.CTkFont(family='Balsamiq Sans', size=14, weight='bold')
dog_list.heading("#1", text="ID")
dog_list.heading("#2", text="Name")
dog_list.heading("#3", text="Breed")
dog_list.heading("#4", text="Age")
dog_list.heading("#5", text="Weight")
dog_list.heading("#6", text="Gender")
dog_list.heading("#7", text="Color")
dog_list.place(relx=0, rely=0, relwidth=1, relheight=1) 

dog_list["show"] = "headings"

heading_font = ctk.CTkFont(family='Balsamiq Sans', size=18, weight='bold')  # Adjust the font settings
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", font=heading_font, foreground='#213256')

button_font = ctk.CTkFont(family='Balsamiq Sans', size=15)
style = ttk.Style()
style.configure("Treeview", rowheight=30, font=button_font, background='silver', fieldbackground='silver')
style.map('Treeview', background=[('selected', '#FF847A')])

scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=dog_list.yview)
scrollbar.place(relx=1, rely=0, relheight=1)
dog_list.configure(yscrollcommand=scrollbar.set)

#Entry_Frame asdlkjsalkdas 
entry_frame = ctk.CTkFrame(dog_frame, fg_color='#213256')
entry_frame.place(relx=0.28, rely=0.732, relwidth=0.719, relheight=0.27)

entry_font = ctk.CTkFont(family='Balsamiq Sans', size=17, weight='bold')

name_entry = ctk.CTkEntry(entry_frame, placeholder_text='Name', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
name_entry.place(relx=0.06, rely=0.1)
breed_entry = ctk.CTkEntry(entry_frame, placeholder_text='Breed', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
breed_entry.place(relx=0.51, rely=0.1)
age_entry = ctk.CTkEntry(entry_frame, placeholder_text='Age', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
age_entry.place(relx=0.06, rely=0.4)
weight_entry = ctk.CTkEntry(entry_frame, placeholder_text='Weight', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
weight_entry.place(relx=0.51, rely=0.4)
gender_entry = ctk.CTkEntry(entry_frame, placeholder_text='Gender', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
gender_entry.place(relx=0.06, rely=0.7)
color_entry = ctk.CTkEntry(entry_frame, placeholder_text='Color', width=280, height=40, 
                            text_color='#293859', placeholder_text_color='#213256', fg_color='#FFFFFF', 
                            border_color='#213256', corner_radius=50, font=entry_font)
color_entry.place(relx=0.51, rely=0.7)

column_widths = {
    "#1": 5,  # ID
    "#2": 20,  # Name
    "#3": 80,  # Breed
    "#4": 15,  # Age
    "#5": 15,  # Weight
    "#6": 20,  # Gender
    "#7": 20  # Color
}

dog_list.bind('<Motion>', lambda event: 'break')

# Execute the SELECT query to fetch data from the 
cursor.execute('SELECT id, name, breed, age, weight, gender, color, image_path FROM dogs')

rows = cursor.fetchall()

# Iterate over the rows and insert them into the Treeview
for row in rows:
    dog_list.insert("", "end", values=row)
    # Display the image for this row
    #display_image(row[-1])  # Assuming the last column is image_path

for col, width in column_widths.items():
    dog_list.column(col, width=width, anchor="center")


# Configure grid row and column weights to make the frame expand
for i in range(2):
    window.grid_rowconfigure(i, weight=1)
    window.grid_columnconfigure(0, weight=1)

# Create a frame for the "Adoption" tab
adopt_frame = ctk.CTkFrame(adopt_tab, fg_color='#213256')
adopt_frame.place(relwidth=1, relheight=1)

res_frame = ctk.CTkFrame(adopt_frame) 
res_frame.place(relx=0, rely=0, relwidth=1, relheight=0.85)

adopt_list = ttk.Treeview(res_frame, columns=("Name", "Email", "Dog Name", "1", "2", "3","4", "5", "6", "7", "8", "9", "10"))
heading2_font = ctk.CTkFont(family='Balsamiq Sans', size=14, weight='bold')
adopt_list.heading("#1", text="Name")
adopt_list.heading("#2", text="Email")
adopt_list.heading("#3", text="Dog Name")
adopt_list.heading("#4", text="1")
adopt_list.heading("#5", text="2")
adopt_list.heading("#6", text="3")
adopt_list.heading("#7", text="4")
adopt_list.heading("#8", text="5")
adopt_list.heading("#9", text="6")
adopt_list.heading("#10", text="7")
adopt_list.heading("#11", text="8")
adopt_list.heading("#12", text="9")
adopt_list.heading("#13", text="10")
adopt_list.place(relx=0, rely=0, relwidth=1, relheight=1) 

adopt_list["show"] = "headings"

heading2_font = ctk.CTkFont(family='Balsamiq Sans', size=16, weight='bold')  
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", font=heading2_font, foreground='#213256')

button2_font = ctk.CTkFont(family='Balsamiq Sans', size=14)
style = ttk.Style()
style.configure("Treeview", rowheight=30, font=button2_font, background='silver', fieldbackground='silver')
style.map('Treeview', background=[('selected', '#FF847A')])

def approve_dog():
    selected_item = adopt_list.selection()
    if not selected_item:
        return  # No item selected

    # Retrieve the selected item's dog name from the third column
    dog_name = adopt_list.item(selected_item)["values"][2]

    # Fetch the data from the 'survey' table before deleting
    cursor2.execute('SELECT * FROM survey WHERE dog_name=%s', (dog_name,))
    survey_data = cursor2.fetchone()

    # Insert data into the 'approved_survey' table
    cursor3.execute('INSERT INTO approved_survey (adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
               (survey_data[0], survey_data[1], survey_data[2],
                survey_data[3], survey_data[4], survey_data[5],
                survey_data[6], survey_data[7], survey_data[8],
                survey_data[9], survey_data[10], survey_data[11],
                survey_data[12]))

    # Delete the dog record from the 'dogs' table
    cursor.execute('DELETE FROM dogs WHERE name=%s', (dog_name,))

    # Delete the dog record from the 'survey' table
    cursor2.execute('DELETE FROM survey WHERE dog_name=%s', (dog_name,))

    # Commit the changes to the 'approved_survey' table
    conn3.commit()

    # Commit the changes to both databases
    conn.commit()
    conn2.commit()

    # Clear existing data from the adopt_list
    adopt_list.delete(*adopt_list.get_children())

    # Update the dog list
    update_dog_list2()

    # Fetch the updated data from the 'survey' table
    cursor2.execute('SELECT adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10 FROM survey')
    rows2 = cursor2.fetchall()

    # Iterate over the rows and insert them into the adopt_list
    for row in rows2:
        adopt_list.insert("", "end", values=row)

    # Fetch the updated data from the approved_survey table
    cursor3.execute('SELECT adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10 FROM approved_survey')
    rows3 = cursor3.fetchall()

    # Clear existing data from the approve_list
    approve_list.delete(*approve_list.get_children())

    # Iterate over the rows and insert them into the approve_list
    for row in rows3:
        approve_list.insert("", "end", values=row)

def update_dog_list2():
    try:
        # Clear existing data from the Treeview
        dog_list.delete(*dog_list.get_children())

        # Execute the SELECT statement to fetch the data, including the ID
        cursor.execute('SELECT id, name, breed, age, weight, gender, color, image_path FROM dogs')

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        # Iterate over the rows and insert them into the Treeview
        for row in rows:
            dog_list.insert("", "end", values=row)
            # Display the image for this row
            display_image(row[-1])  # Assuming the last column is image_path

    except mysql.connector.Error as err:
        # Handle database errors, e.g., connection issues, SQL errors
        print(f"Database error: {err}")

def reject_dog():
    selected_item = adopt_list.selection()
    if not selected_item:
        return 
    adopter_name = adopt_list.item(selected_item)["values"][0]

    # Delete the corresponding records from the 'survey' table
    cursor2.execute('DELETE FROM survey WHERE adopter_name=%s', (adopter_name,))
    conn2.commit()

    adopt_list.delete(*adopt_list.get_children())

    # Fetch the updated data from the 'survey' table
    cursor2.execute('SELECT adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10 FROM survey')
    rows2 = cursor2.fetchall()

    # Iterate over the rows and insert them into the adopt_list
    for row in rows2:
        adopt_list.insert("", "end", values=row)

button3_font = ctk.CTkFont(family='Balsamiq Sans', size=20, weight='bold')

approve_button = ctk.CTkButton(adopt_frame, text='Approve', text_color='#FFFFFF', fg_color='#FF847A',
                            font=button3_font, corner_radius=200, hover_color='#BD5145', width=200, 
                            height=40, command=approve_dog)
approve_button.place(relx=0.27, rely=0.9)

reject_button = ctk.CTkButton(adopt_frame, text='Reject', text_color='#FFFFFF', fg_color='#FF847A',
                            font=button3_font, corner_radius=200, hover_color='#BD5145', width=200, 
                            height=40, command=reject_dog)
reject_button.place(relx=0.53, rely=0.9)

column_min_widths2 = {
    "#1": 65,
    "#2": 160,
    "#3": 65,
    "#4": 30,
    "#5": 30,
    "#6": 30,
    "#7": 30,
    "#8": 30,
    "#9": 30,
    "#10": 30,
    "#11": 30,
    "#12": 30,
    "#13": 30
}

adopt_list.bind('<Motion>', lambda event: 'break')

cursor2.execute('SELECT adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10 FROM survey')

rows2 = cursor2.fetchall()

# Iterate over the rows and insert them into the second Treeview
for row in rows2:
    adopt_list.insert("", "end", values=row)

for col, width in column_min_widths2.items():
    adopt_list.column(col, width=width, minwidth=column_min_widths2[col], anchor="center")

for i in range(2):
    window.grid_rowconfigure(i, weight=1)
    window.grid_columnconfigure(0, weight=1)

approve_frame = ctk.CTkFrame(approve_tab, fg_color='#213256')
approve_frame.place(relwidth=1, relheight=1)

approve_list = ttk.Treeview(approve_frame, columns=("Name", "Email", "Dog Name", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), selectmode="none")
heading2_font = ctk.CTkFont(family='Balsamiq Sans', size=14, weight='bold')

# Set column headings
approve_list.heading("#1", text="Name")
approve_list.heading("#2", text="Email")
approve_list.heading("#3", text="Dog Name")
approve_list.heading("#4", text="1")
approve_list.heading("#5", text="2")
approve_list.heading("#6", text="3")
approve_list.heading("#7", text="4")
approve_list.heading("#8", text="5")
approve_list.heading("#9", text="6")
approve_list.heading("#10", text="7")
approve_list.heading("#11", text="8")
approve_list.heading("#12", text="9")
approve_list.heading("#13", text="10")

# Place the Treeview
approve_list.place(relx=0, rely=0, relwidth=1, relheight=1)

# Set Treeview to show only headings
approve_list["show"] = "headings"

# Configure font for headings
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", font=heading2_font, foreground='#213256')

# Configure font and style for Treeview
button2_font = ctk.CTkFont(family='Balsamiq Sans', size=14)
style.configure("Treeview", rowheight=30, font=button2_font, background='silver', fieldbackground='silver')

# Define column widths
column_widths3 = {
    "#1": 25,
    "#2": 160,
    "#3": 25,
    "#4": 1,
    "#5": 1,
    "#6": 1,
    "#7": 1,
    "#8": 1,
    "#9": 1,
    "#10": 1,
    "#11": 1,
    "#12": 1,
    "#13": 1
    }

approve_list.bind('<Motion>', lambda event: 'break')
approve_frame = ctk.CTkFrame(approve_tab, fg_color='#213256')
approve_frame.place(relwidth=1, relheight=1)

approve_list = ttk.Treeview(approve_frame, columns=("Name", "Email", "Dog Name", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"), selectmode="none")
heading2_font = ctk.CTkFont(family='Balsamiq Sans', size=14, weight='bold')

# Set column headings
approve_list.heading("#1", text="Name")
approve_list.heading("#2", text="Email")
approve_list.heading("#3", text="Dog Name")
approve_list.heading("#4", text="1")
approve_list.heading("#5", text="2")
approve_list.heading("#6", text="3")
approve_list.heading("#7", text="4")
approve_list.heading("#8", text="5")
approve_list.heading("#9", text="6")
approve_list.heading("#10", text="7")
approve_list.heading("#11", text="8")
approve_list.heading("#12", text="9")
approve_list.heading("#13", text="10")

# Place the Treeview
approve_list.place(relx=0, rely=0, relwidth=1, relheight=1)

# Set Treeview to show only headings
approve_list["show"] = "headings"

# Configure font for headings
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview.Heading", font=heading2_font, foreground='#213256')

# Configure font and style for Treeview
button2_font = ctk.CTkFont(family='Balsamiq Sans', size=14)
style.configure("Treeview", rowheight=30, font=button2_font, background='silver', fieldbackground='silver')

# Define column widths
column_min_widths = {
    "#1": 70,
    "#2": 150,
    "#3": 90,
    "#4": 30,
    "#5": 30,
    "#6": 30,
    "#7": 30,
    "#8": 30,
    "#9": 30,
    "#10": 30,
    "#11": 30,
    "#12": 30,
    "#13": 30
}

approve_list.bind('<Motion>', lambda event: 'break')

for item in approve_list.get_children():
    approve_list.delete(item)

cursor3.execute('SELECT adopter_name, email, dog_name, ans_1, ans_2, ans_3, ans_4, ans_5, ans_6, ans_7, ans_8, ans_9, ans_10 FROM approved_survey')
rows3 = cursor3.fetchall()

for row in rows3:
    approve_list.insert("", "end", values=row)

for col, width in column_widths3.items():
    approve_list.column(col, width=width, minwidth=column_min_widths[col], anchor="center")

for i in range(2):
    window.grid_rowconfigure(i, weight=1)

for i in range(13):  # Assuming you have 13 columns
    approve_list.grid_columnconfigure(i, weight=1)
            
window.mainloop()

conn.close()
conn2.close()
conn3.close()