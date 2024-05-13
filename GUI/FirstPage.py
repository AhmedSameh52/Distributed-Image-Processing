import tkinter as tk
from tkinter import ttk
from Componenets import circular_progress_bar
import customtkinter
from tkextrafont import Font

# Create the main window
root = tk.Tk()
root.title("Enhance IT")
font = Font(file="GUI\Fonts\Jua.ttf", family="Jua")

root.columnconfigure(0, weight=1)  # Expanding column
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)
root.rowconfigure(8, weight=1)
root.rowconfigure(9, weight=1)
root.rowconfigure(10, weight=1)
# root.columnconfigure(1, weight=1)  # Expanding column
# root.columnconfigure(2, weight=0)  # Center content column
# root.columnconfigure(3,weight=1)   # Expanding column
# root.columnconfigure(4,weight=1)   # Expanding column

style = ttk.Style()
style.theme_use('clam')
style.configure("CustomColor.Horizontal.TProgressbar", background='#76ABAE', troughcolor='white')

window_width = 1000
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_cordinate = int((screen_width/2) - (window_width/2))
y_cordinate = int((screen_height/2) - (window_height/2))
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

root.configure(background='#242424')

logo = tk.PhotoImage(file="GUI\Images\Camera.png")
logo_label = tk.Label(root, image=logo, bg='#242424')
logo_label.grid(row=3, column=0, pady=(0,0))

# Create label for "Enhance IT"
label = tk.Label(root, text="Enhance IT", font=('Jua', 36, 'bold'), fg="white", bg='#242424')
label.grid(row=4,column=0)


# Progress bar widget
progress = customtkinter.CTkProgressBar(root, orientation="horizontal", width=600, height = 20, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
# progress = ttk.Progressbar(root, style="CustomColor.Horizontal.TProgressbar", orient='horizontal', length=600, mode='determinate')
progress.grid(row=6, column=0, pady=(0,0))


label_loading = tk.Label(root, text="Creating Load Balancer....", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
label_loading.place(x = 198, y = 480)
8
# Function to simulate loading
# def bar():
#     import time
#     for i in range(100):
#         time.sleep(0.05)  # Simulate real loading
#         progress['value'] += 1
#         root.update_idletasks()

# progress['value'] = 20
# root.after(100, bar)


# Start the GUI
root.mainloop()
