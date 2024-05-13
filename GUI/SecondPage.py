import tkinter as tk
from tkinter import ttk
from Componenets import circular_progress_bar
import customtkinter
from tkextrafont import Font

systemStatus = 0
# Create the main window
root = tk.Tk()
root.title("Enhance IT")
font = Font(file="GUI\Fonts\Jua.ttf", family="Jua")

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)
root.columnconfigure(5, weight=1)
root.columnconfigure(6, weight=1)
root.columnconfigure(7, weight=1)
root.columnconfigure(8, weight=1)
root.columnconfigure(9, weight=1)
root.columnconfigure(10, weight=1)
root.columnconfigure(11, weight=1)
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
root.rowconfigure(11, weight=1)
root.rowconfigure(12, weight=1)
root.rowconfigure(13, weight=1)

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

left_menu = tk.PhotoImage(file="GUI/Images/left-menu.png")
left_menu_label = tk.Label(root, image=left_menu, bg='#242424')
# logo_label.grid(row=0, column=0, padx=100)
left_menu_label.place(relx=0, y=0, anchor='nw')

camera_small = tk.PhotoImage(file="GUI/Images/camera-small.png")
camera_small_label = tk.Label(root, image=camera_small, bg='#31363F')
camera_small_label.place(x = 70, y = 50)

label_name = tk.Label(root, text="Enhance IT", font=('Jua', 20, 'bold'), fg="white", bg='#31363F')
label_name.place(x = 50, y = 160)

button_photo_upload_images = tk.PhotoImage(file="GUI/Images/upload-images-button.png")
button_photo_images_uploaded_successfully = tk.PhotoImage(file="GUI/Images/images-uploaded-successfully-button.png")
upload_images_button = tk.Button(root, image=button_photo_upload_images, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F")
upload_images_button.place(x = 47, y = 200)

apply_image = tk.PhotoImage(file="GUI/Images/apply-button.png")
apply_button = tk.Button(root, image=apply_image, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F")
apply_button.place(x = 25, y = 500)

systemStatus = 2

if systemStatus == 0:
    upload_image_label = tk.Label(root, text="Upload Image and Choose an Operation", font=('Jua', 24), fg="white", bg='#242424')
    upload_image_label.place(x = 350, y = 230)

elif systemStatus == 1:
    progress_inside = customtkinter.CTkProgressBar(root, orientation="horizontal", width=600, height = 15, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
    # progress = ttk.Progressbar(root, style="CustomColor.Horizontal.TProgressbar", orient='horizontal', length=600, mode='determinate')
    progress_inside.place(x = 325, y = 280)
    progress_bar_label = tk.Label(root, text="Processing...", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
    progress_bar_label.place(x = 323, y = 230)
elif systemStatus == 2:
    image_finished_label = tk.Label(root, text="Images Finished Processing", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
    image_finished_label.place(x = 300, y = 230)

    download_images = tk.PhotoImage(file="GUI/Images/download-images-button.png")
    download_images_button = tk.Button(root, image=download_images, borderwidth=0, highlightthickness=0, highlightbackground="#242424",activebackground="#242424")
    download_images_button.place(x = 700, y = 225)

def populateframe(frame):
    # Example data: You would generate these based on your instances' health
    statuses = [('Healthy', 'green'), ('Healthy', 'green'), ('Dead', 'red'), ('Healthy', 'green'), ('Healthy', 'green'), ('Healthy', 'green')]

    for i, (status, color) in enumerate(statuses, start=1):
        instanceframe = tk.Frame(frame, bd=2, relief=tk.RIDGE, bg="#242424")
        label = tk.Label(instanceframe, text=f"EC2 Instance {i}\n{status}", bg=color)
        label.pack(padx=10, pady=10)
        instanceframe.pack(side=tk.LEFT, padx=10, pady=10)

style = ttk.Style()
style.theme_use('clam')  # Using a theme that allows color customization
style.configure("Horizontal.TScrollbar", gripcount=0,
                background="#31363f", darkcolor="#31363f", lightcolor="#31363f",
                troughcolor="#76ABAE", bordercolor="#242424", arrowcolor="#76ABAE")

main_frame = tk.Frame(root, height=200, width=600)  # Set the size of the area for the canvas and scrollbar
main_frame.pack_propagate(False)  # Prevents the frame from resizing to fit its contents
main_frame.place(x=300, y=20)

# Create a Canvas and a Scrollbar within the main frame
canvas = tk.Canvas(main_frame, borderwidth=0, bg="#242424", highlightthickness=0, highlightbackground="#242424")
frame = tk.Frame(canvas, background="#242424", border=0, borderwidth=0)  # This frame will hold your instances

# Adding Scrollbar
scrollbar = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview, style="Horizontal.TScrollbar", )
canvas.configure(xscrollcommand=scrollbar.set,)

scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#canvas.place(x=300, y=30)
canvas.create_window((300,30), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

populateframe(frame)  # Add your widgets to the fram

logs_label = tk.Label(root, text="LOGS", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
logs_label.place(x = 280, y = 310)

root.mainloop()