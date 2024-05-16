import tkinter as tk
from tkinter import ttk
import customtkinter
from tkextrafont import Font

import threading
from SecondPage import second_page
# Create the main window
terminateAllWindows = False
root = tk.Tk()
root.title("Enhance IT")
font = Font(file="Fonts\Jua.ttf", family="Jua")

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

logo = tk.PhotoImage(file="Images\Camera.png")
logo_label = tk.Label(root, image=logo, bg='#242424')
logo_label.grid(row=3, column=0, pady=(0,0))

# Create label for "Enhance IT"
label = tk.Label(root, text="Enhance IT", font=('Jua', 36, 'bold'), fg="white", bg='#242424')
label.grid(row=4,column=0)


# Progress bar widget
progress = customtkinter.CTkProgressBar(root, orientation="horizontal", width=600, height = 20, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
# progress = ttk.Progressbar(root, style="CustomColor.Horizontal.TProgressbar", orient='horizontal', length=600, mode='determinate')
progress.grid(row=6, column=0, pady=(0,0))
progress.set(0)

label_loading = tk.Label(root, text="Creating Load Balancer....", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
label_loading.place(x = 198, y = 480)

# Function to simulate loading
# def bar():
#     import time
#     for i in range(100):
#         time.sleep(0.05)  # Simulate real loading
#         progress['value'] += 1
#         root.update_idletasks()

# progress['value'] = 20
# root.after(100, bar)
continue_button_image = tk.PhotoImage(file="Images\continue-button-image.png")
def simulate_loading():
    global progress
    global label_loading

    fault_check_interval = 360
    scale_interval = 360
    threshold = 5
    target_group_arn = 'arn:aws:elasticloadbalancing:eu-central-1:058264462378:targetgroup/target-group-2/1628f616d766de4d'

    label_loading.config(text="Activating Fault Tolerance Feature...")
    for i in range(17):
        progress.step()
        root.after(50)
    # thread = threading.Thread(target=fault_tolerance, args=(target_group_arn,2,fault_check_interval,))
    # thread.start()

    label_loading.config(text="Activating Scalability Feature...")
    for i in range(17):
        progress.step()
        root.after(50)
    # threadScale = threading.Thread(target=scale, args = (scale_interval,threshold,target_group_arn,))
    # threadScale.start()

    label_loading.config(text="Getting Things Ready...")
    while True:
        progress.step()
        root.after(50)  # Adjust the delay as needed
        if progress.get() > 0.95:
            progress.place_forget()
            label_loading.place_forget()
            hiding_progress_image = tk.PhotoImage(file="Images\hide-background.png")
            hiding_progress_label = tk.Label(root, image=hiding_progress_image, bg='#242424')
            hiding_progress_label.place(x = 140, y = 400)
            button = tk.Button(root, image=continue_button_image, command=open_new_window, borderwidth=0, highlightthickness=0, highlightbackground="#242424", activebackground="#242424")
            button.place(x = 372, y = 450)
            break

def on_closing():
    global terminateAllWindows
    terminateAllWindows = True
    root.destroy()

def open_new_window():
    # second_page(root, font)
    root.destroy()

# Start loading progress
thread = threading.Thread(target=simulate_loading)
thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing)
# Start the GUI
root.mainloop()

if terminateAllWindows == False:
    second_page()
