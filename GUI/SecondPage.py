import tkinter as tk
from tkinter import ttk
from Componenets import circular_progress_bar
import customtkinter
from tkextrafont import Font
from tkinter import filedialog
from PIL import Image
import threading

awsInstancesDemo = {"1":  "healthy", "2": "healthy","3": "healthy", "4": "healthy", "5": "healthy"}
logMessages =[
    ("EC2 Instances are Now Processing the Images", "processing"),
    ("Images Uploaded to S3 Bucket", "finished"),
    ("EC2 Instance 4 Is Healthy and Ready to Execute", "healthy"),
    ("EC2 Instance 4 Created Successfully", "finished"),
    ("EC2 Instance 3 Went Down, Creating New Instance Soon....", "not healthy"),
    ("EC2 Instance 3 Is Healthy and Ready to Execute", "healthy"),
]

images_uploaded = []
systemStatus = 0

upload_image_label = None
image_finished_label = None
download_images_button = None

def second_page():
    # print("asdadasd")
    # first_page.quit()
    def rebuild_middle_screen():
        global download_images_button
        global image_finished_label
        global upload_image_label
        print(22222)
        if systemStatus == 0:
            upload_image_label = tk.Label(root, text="Upload Image and Choose an Operation", font=('Jua', 26), fg="white", bg='#242424')
            upload_image_label.place(x=330, y=230)

        elif systemStatus == 1:
            # Remove previous widgets if exist
            try:
                upload_image_label.place_forget()
                progress_inside.place_forget()
                progress_bar_label.place_forget()
            except NameError:
                pass

            progress_inside = customtkinter.CTkProgressBar(root, orientation="horizontal", width=600, height=15, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
            progress_inside.place(x=325, y=280)
            progress_bar_label = tk.Label(root, text="Processing...", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            progress_bar_label.place(x=323, y=230)

        elif systemStatus == 2:
            # Remove previous widgets if exist
            try:
                upload_image_label.place_forget()
                progress_inside.place_forget()
                progress_bar_label.place_forget()
            except NameError:
                pass

            image_finished_label = tk.Label(root, text="Images Finished Processing", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            image_finished_label.place(x=300, y=230)

            download_images = tk.PhotoImage(file="GUI/Images/download-images-button.png")
            download_images_button = tk.Button(root, image=download_images, borderwidth=0, highlightthickness=0, highlightbackground="#242424", activebackground="#242424")
            download_images_button.place(x=700, y=225)

    def submit_images():
        global systemStatus
        systemStatus = 1
        print(31221)
        rebuild_middle_screen()

    def imageUploader():
        global images_uploaded
        images_uploaded = []
        fileTypes = [("Image files", "*.png;*.jpg;*.jpeg")]
        paths = filedialog.askopenfilenames(filetypes=fileTypes)

        # if files are selected
        if paths:
            for path in paths:
                img = Image.open(path)
                images_uploaded.append(img)
        upload_images_button.config(image=button_photo_images_uploaded_successfully)



    def bind_mouse_events(widget):
        """ Bind mouse events to the widget and all its descendants """
        widget.bind("<ButtonPress-1>", on_mouse_down)
        widget.bind("<B1-Motion>", on_mouse_move)

        # Apply the same bindings to all child widgets
        for child in widget.winfo_children():
            bind_mouse_events(child)

    def on_mouse_down(event):
        canvas.scan_mark(event.x, 0)

    def on_mouse_move(event):
        if event.state & 0x100:
            canvas.scan_dragto(event.x, 0, gain=1)


    def bind_mouse_events_logs(widget):
        """ Bind mouse events to the widget and all its descendants """
        widget.bind("<ButtonPress-1>", on_mouse_down_logs)
        widget.bind("<B1-Motion>", on_mouse_move_logs)

        # Apply the same bindings to all child widgets
        for child in widget.winfo_children():
            bind_mouse_events_logs(child)

    def on_mouse_down_logs(event):
        canvas_logs.scan_mark(0, event.y)

    def on_mouse_move_logs(event):
        # Only scroll if the left mouse button is held down
        if event.state & 0x100:  # 0x100 corresponds to the left mouse button being down
            canvas_logs.scan_dragto(0, event.y, gain=1)

    def populateframe(frame):
        # Example data: You would generate these based on your instances' health
        for id, health  in awsInstancesDemo.items():
            instanceframe = tk.Frame(frame, bd=0, relief=tk.RIDGE, bg="#242424")
            label_image = tk.Label(instanceframe, image=cloud_server, bg='#242424')
            label_image.pack(padx=22)
            label_ID_text = tk.Label(instanceframe, text="ID: " + id, bg='#242424', font=font, foreground="#EEEEEE")
            label_ID_text.pack()

            if health == "healthy":
                label_healthy_image = tk.Label(instanceframe, image=healthy_image, bg='#242424')
                label_healthy_image.pack()
            else:
                label_not_healthy_image = tk.Label(instanceframe, image=not_healthy_image, bg='#242424')
                label_not_healthy_image.pack()

            instanceframe.pack(side=tk.LEFT, padx=10, pady=10)
            bind_mouse_events(instanceframe)

    def populateLogsFrame(frame):
        for i, (message, messageType) in enumerate(logMessages):
            log_image = None
            if logMessages[i][1] == 'processing':
                log_image = processing_log_image
            elif logMessages[i][1] == 'finished':
                log_image = finished_log_image
            elif logMessages[i][1] == 'healthy':
                log_image = healthy_log_image
            elif logMessages[i][1] == 'not healthy':
                log_image = not_healthy_log_image
            instanceframe = tk.Frame(frame, bd=0, relief=tk.RIDGE, bg="#242424")
            label_image = tk.Label(instanceframe, image=log_image, bg='#242424')  # Example image reference
            label_image.pack(padx=0)
            label_text = tk.Label(instanceframe, text=logMessages[i][0], bg='#76ABAE', font=font, foreground="#31363F")
            label_text.place(relx=0.1, rely=0.47, anchor="w")
            # if health == "healthy":
            #     label_healthy_image = tk.Label(instanceframe, image=healthy_image, bg='#242424')  # Example healthy image reference
            #     label_healthy_image.pack()
            # else:
            #     label_not_healthy_image = tk.Label(instanceframe, image=not_healthy_image, bg='#242424')  # Example not healthy image reference
            #     label_not_healthy_image.pack()
            instanceframe.pack(side=tk.TOP, padx=10, pady=10)
            bind_mouse_events_logs(instanceframe)
    def on_Advanced_combobox_select(event):
        print(f"Advanced Selected: {Advancedcombobox.get()}")

    def on_Basic_combobox_select(event):
        print(f"Basic Selected: {BasicCombobox.get()}")

    # Create the main window
    root = tk.Tk()
    root.title("Enhance IT")
    font = Font(file="GUI\Fonts\Jua.ttf", family="Jua")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("CustomColor.Horizontal.TProgressbar", background='#76ABAE', troughcolor='white')
    style.configure('TCombobox', foreground='black', font=("Jua", 12))
    style.configure('Advanced.TCombobox', fieldbackground='lightblue', background='lightblue', arrowcolor='blue')
    style.configure('Basic.TCombobox', fieldbackground='yellow', background='yellow', arrowcolor='orange')

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
    upload_images_button = tk.Button(root, image=button_photo_upload_images, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F", command=imageUploader)
    upload_images_button.place(x = 47, y = 200)

    apply_image = tk.PhotoImage(file="GUI/Images/apply-button.png")
    apply_button = tk.Button(root, image=apply_image, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F", command=submit_images)
    apply_button.place(x = 25, y = 500)

    rebuild_middle_screen()


    cloud_server = tk.PhotoImage(file="GUI/Images/cloud-server.png")
    healthy_image = tk.PhotoImage(file="GUI/Images/healthy.png")
    not_healthy_image = tk.PhotoImage(file="GUI/Images/not-healthy.png")

    Advanced_options = ['Morphological Opening ', 'Morphological Closing', 'Hough Transform', 'Draw Contours']

    Basic_options=['edge_detection',  'color_inversion', 'blur', 'rotate 90', 'rotate 180', 'rotate 270', 'resize 265x265' ,'resize 512x512' ]

    Advancedcombobox = ttk.Combobox(root , style="TCombobox",values=Advanced_options,state="readonly",font=font)
    Advancedcombobox.place(x=47,y=350)  # Place the combobox in the window
    Advancedcombobox.set("Advanced Operation")
    Advancedcombobox.bind("<<ComboboxSelected>>", on_Advanced_combobox_select)

    BasicCombobox =  ttk.Combobox(root , style="TCombobox",values=Basic_options,state="readonly",font=font)
    BasicCombobox.set("Basic Operation")
    BasicCombobox.place(x=47,y=425)  # Place the combobox in the window
    BasicCombobox.bind("<<ComboboxSelected>>", on_Basic_combobox_select)


    style = ttk.Style()
    style.theme_use('clam')  # Using a theme that allows color customization
    style.configure("Horizontal.TScrollbar", gripcount=0,
                    background="#31363f", darkcolor="#31363f", lightcolor="#31363f",
                    troughcolor="#76ABAE", bordercolor="#242424", arrowcolor="#76ABAE")
    style.map('Horizontal.TScrollbar',
        background=[('pressed', '!disabled', '#31363f'), ('active', '#31363f')])

    main_frame = tk.Frame(root, height=200, width=600)  # Set the size of the area for the canvas and scrollbar
    main_frame.pack_propagate(False)  # Prevents the frame from resizing to fit its contents
    main_frame.place(x=300, y=20)


    # Create a Canvas and a Scrollbar within the main frame
    canvas = tk.Canvas(main_frame, borderwidth=0, bg="#242424", highlightthickness=0, highlightbackground="#242424")

    canvas.bind("<ButtonPress-1>", on_mouse_down)  # Left button mouse down
    canvas.bind("<B1-Motion>", on_mouse_move)  # Left button being held down and moved

    frame = tk.Frame(canvas, background="#242424", border=0, borderwidth=0)  # This frame will hold your instances
    bind_mouse_events(frame)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #canvas.place(x=300, y=30)
    indent = 0
    if len(awsInstancesDemo) == 4:
        indent = 130
    elif len(awsInstancesDemo) == 3:
        indent = 90
    elif len(awsInstancesDemo) == 2:
        indent = 160
    elif len(awsInstancesDemo) == 1:
        indent = 240
    canvas.create_window((indent,0), window=frame, anchor="nw")

    frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

    populateframe(frame)  # Add your widgets to the fram

    logs_label = tk.Label(root, text="LOGS", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
    logs_label.place(x = 280, y = 315)


    # LOGS FRAME
    processing_log_image = tk.PhotoImage(file="GUI/Images/processing-log-image.png")
    finished_log_image = tk.PhotoImage(file="GUI/Images/finished-log-image.png")
    healthy_log_image = tk.PhotoImage(file="GUI/Images/healthy-log-image.png")
    not_healthy_log_image = tk.PhotoImage(file="GUI/Images/not-healthy-log.png")


    # Configure the style for a vertical scrollbar
    styleLogs = ttk.Style()
    styleLogs.theme_use('clam')  # Using a theme that allows color customization
    styleLogs.configure("Vertical.TScrollbar", gripcount=0,
                        background="#31363f", darkcolor="#31363f", lightcolor="#31363f",
                        troughcolor="#76ABAE", bordercolor="#242424", arrowcolor="#76ABAE")
    style.map('Vertical.TScrollbar',
        background=[('pressed', '!disabled', '#31363f'), ('active', '#31363f')])

    main_frame_logs = tk.Frame(root, height=200, width=700)  # Set the size of the area for the canvas and scrollbar
    main_frame_logs.pack_propagate(False)  # Prevents the frame from resizing to fit its contents
    main_frame_logs.place(x=270, y=360)

    canvas_logs = tk.Canvas(main_frame_logs, borderwidth=0, bg="#242424", highlightthickness=0, highlightbackground="#242424")

    canvas_logs.bind("<ButtonPress-1>", on_mouse_down_logs)  # Left button mouse down
    canvas_logs.bind("<B1-Motion>", on_mouse_move_logs)  # Left button being held down and moved

    frame_logs = tk.Frame(canvas_logs, background="#242424")  # This frame will hold your instances

    # Create a vertical scrollbar
    # scrollbar_logs = ttk.Scrollbar(main_frame_logs, orient="vertical", command=canvas_logs.yview, style="Vertical.TScrollbar")
    # canvas_logs.configure(yscrollcommand=scrollbar_logs.set)
    # scrollbar_logs.pack(side=tk.RIGHT, fill=tk.Y)  # Adjust scrollbar to the right side
    canvas_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas_logs.create_window((0, 0), window=frame_logs, anchor="nw")

    frame_logs.bind("<Configure>", lambda event, canvas=canvas_logs: canvas.configure(scrollregion=canvas.bbox("all")))

    bind_mouse_events_logs(frame_logs)

    populateLogsFrame(frame_logs)  # Populate the frame with logs
    # first_page.destroy()
    root.mainloop()

