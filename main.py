#---------------------------------------- Imports ------------------------------------------------------
import tkinter as tk
from tkinter import ttk
import customtkinter
from tkextrafont import Font
import threading
import boto3
import time
from configure_ec2 import configure_ec2_instance
from upload_script_ec2 import upload_script_ec2
import io
import aiohttp
import asyncio
from tkinter import filedialog
from PIL import Image
from config import *
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
#---------------------------------------- GLOBAL VARIABLES ---------------------------------------------
terminateAllWindows = False
awsInstances = {"i-1412412dwqdqddwwwdwdw41412a":  "healthy", "i-1412412dwqdqddwwwdwdw41412adsaddas": "healthy","i-1412412dwqdqddwwwdwdw41412a231312": "healthy", "i-1412412dwqdqddwwwdwdw41412assadxz": "healthy", "i-1412412dwqdqddwwwdwdw41412a12sqA": "healthy"}
logs = []
imagesUploaded= []
imagesNames = []
numRequests = 0
systemStatus = 0
upload_image_label = None
image_finished_label = None
download_images_button = None
progress = None
label_loading = None
continue_button_image = None
imageOperation = None
imageParameter = None
processing_log_image = None
finished_log_image = None
healthy_log_image = None
not_healthy_log_image = None
font = None
canvas_logs = None
canvas = None
cloud_server = None
healthy_image = None
not_healthy_image = None
second_frame_instances = None
second_frame_logs = None
root = None
download_images = None
hide_progress_image = None
images = []
button_photo_upload_images = None
upload_images_button = None
global hide_progress_label

#---------------------------------------- FUNCTIONS DECLERATION ----------------------------------------
def init():
    session = boto3.Session(
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key,
    region_name = region_name
    )
    client = session.client('elbv2')
    ec2 = session.resource('ec2')
    ec2_client = session.client('ec2')
    s3_client = session.client('s3')
    s3_resource = session.resource('s3')
    return client,ec2,ec2_client,s3_client,s3_resource

def create_json_data(image_keys, operation, parameter):
    json_data = []
    for key in image_keys:
        json_data.append({
            'imagekey': key,
            'imageoperation': operation,
            'imageparameter': parameter
        })
    return json_data

async def send_post_request(session, url, json_data):
    async with session.post(url, json=json_data) as response:
        print(f"POST /data {json_data['imagekey']}: {await response.text()}")

async def send_to_load_balancer(operation, parameter):
    global imagesUploaded
    global load_balancer_url
    image_keys = imagesUploaded
    url = load_balancer_url
    for id, health in awsInstances.items():
        if health == "healthy":
            logs.insert(0, (f'EC2 Instance {id} is Now Processing the Images','processing'))
            populateLogsFrame()
    # List of JSON data payloads to be sent
    json_datas = create_json_data(image_keys, operation, parameter)
    print(json_datas)
    async with aiohttp.ClientSession() as session:
        tasks = [send_post_request(session, url, json) for json in json_datas]
        await asyncio.gather(*tasks)

def upload_to_s3():
    global imagesUploaded
    global imagesNames
    global images

    _,_,_,s3_client,_ = init()
    for index, image in enumerate(images):
        # Get the image format and extension
        format = image.format if image.format else 'JPEG'
        extension = format.lower()

        object_name = f'test-case-{index+1}.{extension}'
        imagesUploaded.append(object_name)

        # Convert the PIL image to a BytesIO object
        image_buffer = io.BytesIO()
        image.save(image_buffer, format=format)
        image_buffer.seek(0)

        # Use upload_fileobj to upload file-like objects
        s3_client.upload_fileobj(image_buffer, bucket_name, object_name)

        logs.insert(0, ('Image uploaded to S3!', 'finished'))
        populateLogsFrame()  # Assuming you handle your UI updates here

def create_ec2_instance(target_group_arn):
    global awsInstances
    global logs
    client,ec2,ec2_client,_,_= init()

    # Create EC2 instance
    instances = ec2.create_instances(
        ImageId=vm_ami_id,  # Ensure this AMI ID is available in 'eu-central-1'
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='myEC2Key'  # Ensure you have this key pair in 'eu-central-1'
    )
    # Wait for the instance to be in a running state
    instance = instances[0]
    instance.wait_until_running()
    instance_id = instance.id
    logs.insert(0, (f'EC2 Instance with id {instance_id} Created Successfully!','finished'))
    populateLogsFrame()
    time.sleep(20)

    # Refresh to get the latest data
    instance.load()
    # Retrieve and print the public IP address
    public_ip_address = instance.public_ip_address

    print(f"EC2 Instance {instance.id} created and running.")
    configure_ec2_instance(public_ip_address,keyName)
    response = client.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[
        {
            'Id': instance.id,
            'Port': 80  # Specify the port on which the target receives traffic, adjust if needed
        }
    ]
    )
    def instanceReady():
        global awsInstances
        time.sleep(20)
        logs.insert(0,(f'EC2 instance {instance_id} is healthy and ready to execute!', 'healthy'))
        populateLogsFrame()
        awsInstances = get_instance_health_dict(target_group_arn)
        populateframe()
    thread = threading.Thread(target=instanceReady)
    thread.start()
    upload_script_ec2(public_ip_address,keyName)
    print("Instance registered to target group:", response)

def get_number_of_instances_in_target_group(target_group_arn):
    # Initialize the ELBv2 client
    client,_,_,_,_ = init()

    # Describe target health to get information about targets in the target group
    response = client.describe_target_health(TargetGroupArn=target_group_arn)
    instance_count = len(response['TargetHealthDescriptions'])
    return instance_count


def scale(scale_interval,threshold, target_group):
    global numRequests
    global awsInstances
    while True:
        print ('checking to scale..')
        numVmsRunning = get_number_of_instances_in_target_group(target_group)
        if numRequests % 5 ==0: # 5 requests per vm
            numVms = (numRequests // threshold)
        else:
            numVms = (numRequests // threshold) + 1
        desiredVms = numVms - numVmsRunning
        print(f'numVmsRunning= {numVmsRunning}, numVms = {numVms}, desiredVms = {desiredVms}, numRequests = {numRequests}')
        if desiredVms < 0 :
            desiredVms = desiredVms * -1

            for i in range(desiredVms):
                if numVmsRunning <= 2:
                    break
                terminate_instance(list(awsInstances.keys())[i])

                numVmsRunning = numVmsRunning -1
        else:
            for i in range (desiredVms):
                thread = threading.Thread(target=create_ec2_instance, args=(target_group,))
                thread.start()
        time.sleep(20)
        awsInstances = get_instance_health_dict(target_group)
        populateframe()
        numRequests = 0
        time.sleep(scale_interval)

def terminate_instance(instance_id):
    # Terminate the instance
    _,ec2,_,_,_= init()
    instance = ec2.Instance(instance_id)
    instance.terminate()
    logs.insert(0,(f'EC2 instance with ID {instance_id} has been terminated','not healthy'))
    populateLogsFrame()

def get_instance_health_dict(target_group_arn):
    client,_,_,_,_ = init()

    # Call describe_target_health to get the health status of instances in the target group
    response = client.describe_target_health(TargetGroupArn=target_group_arn)

    # Dictionary to hold instance health status
    health_dict = {}

    # Process the response
    for target_health_description in response['TargetHealthDescriptions']:
        # Add the target ID and its health state to the dictionary
        health_dict[target_health_description['Target']['Id']] = target_health_description['TargetHealth']['State']

    new_health_dict = {}
    for key, value in health_dict.items():
        # Get the last 6 characters of the current key
        last_six_chars = key[-6:]
        # Create a new key in the format i-abcdef
        new_key = f"i-{last_six_chars}"
        # Add the new key-value pair to the new dictionary
        new_health_dict[new_key] = value
    return new_health_dict

def fault_tolerance(target_group_arn, threshold,check_interval):
    global awsInstances
    global logs
    while True:
        client,_,_,_,_= init()
        response = client.describe_target_health(TargetGroupArn=target_group_arn)

        healthy_count = sum(1 for target in response['TargetHealthDescriptions']
                            if target['TargetHealth']['State'] == 'healthy')

        print(f"healthy instances count: {healthy_count}")
        awsInstances = get_instance_health_dict(target_group_arn)
        populateframe()
        for instance_id, health_state in awsInstances.items():
            if health_state== 'healthy':
                logs.insert(0,(f'EC2 instance {instance_id} is healthy and ready to execute!', 'healthy'))
                populateLogsFrame()
            else:
                logs.insert(0, (f'EC2 instance {instance_id} went down, Creating another instance..', 'not healthy'))
                populateLogsFrame()
                terminate_instance(instance_id)
        if healthy_count < threshold:
            print("Unhealthy instance count is below the threshold. Creating an EC2 instance...")
            for i in range(threshold - healthy_count):
                thread = threading.Thread(target=create_ec2_instance, args=(target_group_arn,))
                thread.start()

        else:
            print("No need to create a new instance. The number of unhealthy instances is not below the threshold.")
        time.sleep(check_interval)

def populateframe():
    global second_frame_instances
    global awsInstances
    global cloud_server
    global healthy_image
    global not_healthy_image
    global root
    global canvas

    main_frame = tk.Frame(root, height=200, width=600)  # Set the size of the area for the canvas and scrollbar
    main_frame.pack_propagate(False)  # Prevents the frame from resizing to fit its contents
    main_frame.place(x=300, y=20)


    # Create a Canvas and a Scrollbar within the main frame
    canvas = tk.Canvas(main_frame, borderwidth=0, bg="#242424", highlightthickness=0, highlightbackground="#242424")

    canvas.bind("<ButtonPress-1>", on_mouse_down)  # Left button mouse down
    canvas.bind("<B1-Motion>", on_mouse_move)  # Left button being held down and moved

    second_frame_instances = tk.Frame(canvas, background="#242424", border=0, borderwidth=0)  # This frame will hold your instances
    bind_mouse_events(second_frame_instances)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    indent = 0
    if len(awsInstances) == 4:
        indent = 130
    elif len(awsInstances) == 3:
        indent = 90
    elif len(awsInstances) == 2:
        indent = 160
    elif len(awsInstances) == 1:
        indent = 240
    canvas.create_window((indent,0), window=second_frame_instances, anchor="nw")

    second_frame_instances.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

    for id, health  in awsInstances.items():
        instanceframe = tk.Frame(second_frame_instances, bd=0, relief=tk.RIDGE, bg="#242424")
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

def populateLogsFrame():
    global second_frame_logs
    global logs
    global processing_log_image
    global finished_log_image
    global healthy_log_image
    global not_healthy_log_image
    global root
    global canvas_logs

    main_frame_logs = tk.Frame(root, height=200, width=700)  # Set the size of the area for the canvas and scrollbar
    main_frame_logs.pack_propagate(False)  # Prevents the frame from resizing to fit its contents
    main_frame_logs.place(x=270, y=360)

    canvas_logs = tk.Canvas(main_frame_logs, borderwidth=0, bg="#242424", highlightthickness=0, highlightbackground="#242424")

    canvas_logs.bind("<ButtonPress-1>", on_mouse_down_logs)  # Left button mouse down
    canvas_logs.bind("<B1-Motion>", on_mouse_move_logs)  # Left button being held down and moved

    second_frame_logs = tk.Frame(canvas_logs, background="#242424")  # This frame will hold your instances

    canvas_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas_logs.create_window((0, 0), window=second_frame_logs, anchor="nw")

    second_frame_logs.bind("<Configure>", lambda event, canvas=canvas_logs: canvas.configure(scrollregion=canvas.bbox("all")))

    bind_mouse_events_logs(second_frame_logs)

    for i, (message, messageType) in enumerate(logs):
        log_image = None
        if logs[i][1] == 'processing':
            log_image = processing_log_image
        elif logs[i][1] == 'finished':
            log_image = finished_log_image
        elif logs[i][1] == 'healthy':
            log_image = healthy_log_image
        elif logs[i][1] == 'not healthy':
            log_image = not_healthy_log_image
        instanceframe = tk.Frame(second_frame_logs, bd=0, relief=tk.RIDGE, bg="#242424")
        label_image = tk.Label(instanceframe, image=log_image, bg='#242424')  # Example image reference
        label_image.pack(padx=0)
        label_text = tk.Label(instanceframe, text=logs[i][0], bg='#76ABAE', font=font, foreground="#31363F")
        label_text.place(relx=0.1, rely=0.47, anchor="w")
        instanceframe.pack(side=tk.TOP, padx=10, pady=10)
        bind_mouse_events_logs(instanceframe)

def bind_mouse_events(widget):
    """ Bind mouse events to the widget and all its descendants """
    widget.bind("<ButtonPress-1>", on_mouse_down)
    widget.bind("<B1-Motion>", on_mouse_move)

    # Apply the same bindings to all child widgets
    for child in widget.winfo_children():
        bind_mouse_events(child)

def on_mouse_down(event):
    global canvas
    canvas.scan_mark(event.x, 0)

def on_mouse_move(event):
    global canvas
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
    global canvas_logs
    canvas_logs.scan_mark(0, event.y)

def on_mouse_move_logs(event):
    global canvas_logs
    # Only scroll if the left mouse button is held down
    if event.state & 0x100:  # 0x100 corresponds to the left mouse button being down
        canvas_logs.scan_dragto(0, event.y, gain=1)

def second_page():
    global logs
    global awsInstances
    global imageOperation
    global imageParameter
    global imagesUploaded
    global imagesNames
    global font
    global canvas_logs
    global canvas
    global cloud_server
    global healthy_image
    global not_healthy_image
    global processing_log_image
    global finished_log_image
    global healthy_log_image
    global not_healthy_log_image
    global second_frame_logs
    global second_frame_instances
    global systemStatus
    global root
    global download_images
    global hide_progress_image
    global button_photo_upload_images
    global upload_images_button
    global hide_progress_label

    def rebuild_middle_screen():
        global download_images_button
        global image_finished_label
        global upload_image_label
        global root
        global systemStatus
        global download_images
        global hide_progress_image
        global hide_progress_label

        def simulateProgressBar():
            global systemStatus
            while True:
                progress_inside.step()
                time.sleep(0.2)
                if progress_inside.get() > 0.95:
                    systemStatus = 2
                    rebuild_middle_screen()
                    break
        if systemStatus == 0:
            upload_image_label = tk.Label(root, text="Upload Image and Choose an Operation", font=('Jua', 26), fg="white", bg='#242424')
            upload_image_label.place(x=330, y=230)

        elif systemStatus == 1:
            # Remove previous widgets if exist
            try:
                upload_image_label.place_forget()
                progress_inside.place_forget()
                progress_bar_label.place_forget()
                image_finished_label.forget()
                download_images_button.forget()
            except NameError:
                pass
            hide_progress_image = tk.PhotoImage(file="Images/hide-inside-progress-bar2.png")
            hide_progress_label = tk.Label(root, image=hide_progress_image, font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            hide_progress_label.place(x=300, y=225)
            progress_inside = customtkinter.CTkProgressBar(root, orientation="horizontal", width=600, height=15, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
            progress_inside.place(x=325, y=280)
            progress_bar_label = tk.Label(root, text="Processing...", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            progress_bar_label.place(x=323, y=230)
            progress_inside.set(0)
            thread = threading.Thread(target=simulateProgressBar)
            thread.start()

        elif systemStatus == 2:
            # Remove previous widgets if exist
            try:
                upload_image_label.place_forget()
                progress_inside.place_forget()
                progress_bar_label.place_forget()
            except NameError:
                pass
            hide_progress_image = tk.PhotoImage(file="Images/hide-inside-progress-bar.png")
            hide_progress_label = tk.Label(root, image=hide_progress_image, font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            hide_progress_label.place(x=325, y=280)
            image_finished_label = tk.Label(root, text="Images Finished Processing", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
            image_finished_label.place(x=300, y=230)

            download_images = tk.PhotoImage(file="Images/download-images-button.png")
            download_images_button = tk.Button(root, image=download_images, borderwidth=0, highlightthickness=0, highlightbackground="#242424", activebackground="#242424", command=downloadImages)
            download_images_button.place(x=700, y=225)

    def submit_images():
        global systemStatus
        global imageOperation
        global imageParameter
        global imagesUploaded
        global numRequests
        global imagesNames
        global button_photo_upload_images
        global upload_images_button
        if len(imagesNames) == 0:
            return
        numRequests = len(imagesNames)
        imageParameter = parameter_entry.get()
        upload_images_button.config(image=button_photo_upload_images)
        systemStatus = 1
        thread = threading.Thread(target=rebuild_middle_screen)
        thread.start()
        thread = threading.Thread(target=submit_images_thread_function)
        thread.start()
        imagesNames = []

    def submit_images_thread_function():
        global imageOperation
        global imageParameter
        asyncio.run(send_to_load_balancer(imageOperation, imageParameter))

    def get_downloads_folder():
        if os.name == 'nt':  # For Windows
            return os.path.join(os.getenv('USERPROFILE'), 'Downloads')
        else:  # For macOS and Linux
            return os.path.join(os.path.expanduser('~'), 'Downloads')

    def downloadImages():
        global bucket_name
        global imagesNames
        global imagesUploaded
        _,_,_,s3,_= init()
        local_folder = get_downloads_folder()

        if not os.path.exists(local_folder):
            os.makedirs(local_folder)

        for image_name in imagesUploaded:
            try:
                image_key = image_name.replace('.png', '', 1)
                processed_image_name = image_key + '_processed.jpg'

                filename = os.path.basename(processed_image_name)
                local_path = os.path.join(local_folder, filename)

                print(f"Downloading {processed_image_name} to {local_path}")
                s3.download_file(bucket_name, processed_image_name, local_path)
                print(f"Successfully downloaded {processed_image_name}")

            except NoCredentialsError:
                print("Credentials not available for AWS S3.")
                break

            except PartialCredentialsError:
                print("Incomplete credentials for AWS S3.")
                break

            except Exception as e:
                print(f"An error occurred: {e}")

    def imageUploader():
        global imagesUploaded
        global imagesNames
        global images
        fileTypes = [("Image files", "*.png;*.jpg;*.jpeg")]
        paths = filedialog.askopenfilenames(filetypes=fileTypes)
        if not paths:
            return
        images = []
        imagesNames = []
        imagesUploaded = []

        # if files are selected
        if paths:
            for path in paths:
                img = Image.open(path)
                newPath = path.split('/')[-1]
                imagesNames.append(newPath)
                images.append(img)
        thread = threading.Thread(target=upload_to_s3)
        thread.start()
        upload_images_button.config(image=button_photo_images_uploaded_successfully)

    def on_Advanced_combobox_select(choice):
        global imageOperation
        imageOperation = choice
        BasicCombobox.set("Basic Operation")
        print(f"Advanced Selected: {choice}")

    def on_Basic_combobox_select(Bchoice):
        global imageOperation
        imageOperation = Bchoice
        Advancedcombobox.set("Advanced Operation")
        print(f"Basic Selected: {Bchoice}")

    # Create the main window
    root = tk.Tk()
    root.resizable(False, False)
    root.title("Enhance IT")

    font = Font(file="Fonts\Jua.ttf", family="Jua")

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

    left_menu = tk.PhotoImage(file="Images/left-menu.png")
    left_menu_label = tk.Label(root, image=left_menu, bg='#242424')
    # logo_label.grid(row=0, column=0, padx=100)
    left_menu_label.place(relx=0, y=0, anchor='nw')

    camera_small = tk.PhotoImage(file="Images/camera-small.png")
    camera_small_label = tk.Label(root, image=camera_small, bg='#31363F')
    camera_small_label.place(x = 70, y = 50)

    label_name = tk.Label(root, text="Enhance IT", font=('Jua', 20, 'bold'), fg="white", bg='#31363F')
    label_name.place(x = 50, y = 160)

    button_photo_upload_images = tk.PhotoImage(file="Images/upload-images-button.png")
    button_photo_images_uploaded_successfully = tk.PhotoImage(file="Images/images-uploaded-successfully-button.png")
    upload_images_button = tk.Button(root, image=button_photo_upload_images, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F", command=imageUploader)
    upload_images_button.place(x = 47, y = 200)

    apply_image = tk.PhotoImage(file="Images/apply-button.png")
    apply_button = tk.Button(root, image=apply_image, borderwidth=0, highlightthickness=0, highlightbackground="#31363F",activebackground="#31363F", command=submit_images)
    apply_button.place(x = 18, y = 500)

    rebuild_middle_screen()


    cloud_server = tk.PhotoImage(file="Images/cloud-server.png")
    healthy_image = tk.PhotoImage(file="Images/healthy.png")
    not_healthy_image = tk.PhotoImage(file="Images/not-healthy.png")

    Advanced_options = ['closing', 'opening', 'line_detection', 'contour']

    Basic_options=['edge_detection',  'color_inversion', 'blur', 'rotate', 'resize']

    Advancedcombobox = customtkinter.CTkComboBox(root ,values=Advanced_options,state="readonly",font=('Jua',14),width=200,dropdown_font=('Jua',14),
                                                 fg_color='#76ABAE',text_color='black',button_color='#76ABAE',dropdown_fg_color='#76ABAE',
                                                 dropdown_text_color='black',border_color="#76ABAE",dropdown_hover_color="#65989B",button_hover_color="#65989B",command=on_Advanced_combobox_select)
    Advancedcombobox.place(x=20,y=350)  # Place the combobox in the window
    Advancedcombobox.set("Advanced Operation")

    BasicCombobox =  customtkinter.CTkComboBox(root ,values=Basic_options,state="readonly",font=('Jua',14),width=200,dropdown_font=('Jua',14),
                                                 fg_color='#76ABAE',text_color='black',button_color='#76ABAE',dropdown_fg_color='#76ABAE',
                                                 dropdown_text_color='black',border_color="#76ABAE",dropdown_hover_color="#65989B",button_hover_color="#65989B",command=on_Basic_combobox_select)
    BasicCombobox.set("Basic Operation")
    BasicCombobox.place(x=20,y=400)

    parameter_entry = customtkinter.CTkEntry(master=root,
                               width=200,
                               height=30,
                               corner_radius=10, bg_color='#31363F', fg_color="#31363f", font=("Jua", 14), text_color="#EEEEEE", border_color="#76ABAE", placeholder_text="Image Parameter")
    parameter_entry.place(x=120, y=465, anchor=tk.CENTER)

    style = ttk.Style()
    style.theme_use('clam')  # Using a theme that allows color customization
    style.configure("Horizontal.TScrollbar", gripcount=0,
                    background="#31363f", darkcolor="#31363f", lightcolor="#31363f",
                    troughcolor="#76ABAE", bordercolor="#242424", arrowcolor="#76ABAE")
    style.map('Horizontal.TScrollbar',
        background=[('pressed', '!disabled', '#31363f'), ('active', '#31363f')])

    populateframe()  # Add your widgets to the fram

    logs_label = tk.Label(root, text="LOGS", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
    logs_label.place(x = 280, y = 315)


    # LOGS FRAME
    processing_log_image = tk.PhotoImage(file="Images/processing-log-image.png")
    finished_log_image = tk.PhotoImage(file="Images/finished-log-image.png")
    healthy_log_image = tk.PhotoImage(file="Images/healthy-log-image.png")
    not_healthy_log_image = tk.PhotoImage(file="Images/not-healthy-log.png")


    # Configure the style for a vertical scrollbar
    styleLogs = ttk.Style()
    styleLogs.theme_use('clam')  # Using a theme that allows color customization
    styleLogs.configure("Vertical.TScrollbar", gripcount=0,
                        background="#31363f", darkcolor="#31363f", lightcolor="#31363f",
                        troughcolor="#76ABAE", bordercolor="#242424", arrowcolor="#76ABAE")
    style.map('Vertical.TScrollbar',
        background=[('pressed', '!disabled', '#31363f'), ('active', '#31363f')])

    populateLogsFrame()  # Populate the frame with logs
    root.mainloop()






#---------------------------------------- MAIN CODE ----------------------------------------------------
def firstPage():
    global progress
    global label_loading
    global continue_button_image

    def on_closing():
        global terminateAllWindows
        terminateAllWindows = True
        rootMainPage.destroy()

    def open_new_window(scale_interval, threshold, fault_check_interval):
        global target_group_arn
        thread = threading.Thread(target=fault_tolerance, args=(target_group_arn,2,fault_check_interval,))
        thread.start()
        threadScale = threading.Thread(target=scale, args = (scale_interval,threshold,target_group_arn,))
        threadScale.start()
        rootMainPage.destroy()

    def simulate_loading(rootMainPage):
        global progress
        global label_loading
        global target_group_arn
        global continue_button_image
        fault_check_interval = 240
        scale_interval = 260
        threshold = 5
        target_group_arn = target_group_arn

        label_loading.config(text="Activating Fault Tolerance Feature...")
        for i in range(17):
            progress.step()
            rootMainPage.after(50)

        label_loading.config(text="Activating Scalability Feature...")
        for i in range(17):
            progress.step()
            rootMainPage.after(50)

        label_loading.config(text="Getting Things Ready...")
        while True:
            progress.step()
            rootMainPage.after(50)  # Adjust the delay as needed
            if progress.get() > 0.95:
                progress.place_forget()
                label_loading.place_forget()
                hiding_progress_image = tk.PhotoImage(file="Images\hide-background.png")
                hiding_progress_label = tk.Label(rootMainPage, image=hiding_progress_image, bg='#242424')
                hiding_progress_label.place(x = 140, y = 400)
                button = tk.Button(rootMainPage, image=continue_button_image, command=lambda: open_new_window(scale_interval, threshold, fault_check_interval), borderwidth=0, highlightthickness=0, highlightbackground="#242424", activebackground="#242424")
                button.place(x = 372, y = 450)
                break

    rootMainPage = tk.Tk()
    rootMainPage.title("Enhance IT")
    rootMainPage.resizable(False, False)
    font = Font(file="Fonts\Jua.ttf", family="Jua")

    rootMainPage.columnconfigure(0, weight=1)
    rootMainPage.rowconfigure(0, weight=1)
    rootMainPage.rowconfigure(1, weight=1)
    rootMainPage.rowconfigure(2, weight=1)
    rootMainPage.rowconfigure(3, weight=1)
    rootMainPage.rowconfigure(4, weight=1)
    rootMainPage.rowconfigure(5, weight=1)
    rootMainPage.rowconfigure(6, weight=1)
    rootMainPage.rowconfigure(7, weight=1)
    rootMainPage.rowconfigure(8, weight=1)
    rootMainPage.rowconfigure(9, weight=1)
    rootMainPage.rowconfigure(10, weight=1)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("CustomColor.Horizontal.TProgressbar", background='#76ABAE', troughcolor='white')

    window_width = 1000
    window_height = 600
    screen_width = rootMainPage.winfo_screenwidth()
    screen_height = rootMainPage.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    rootMainPage.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    rootMainPage.configure(background='#242424')

    logo = tk.PhotoImage(file="Images\Camera.png")
    logo_label = tk.Label(rootMainPage, image=logo, bg='#242424')
    logo_label.grid(row=3, column=0, pady=(0,0))

    # Create label for "Enhance IT"
    label = tk.Label(rootMainPage, text="Enhance IT", font=('Jua', 36, 'bold'), fg="white", bg='#242424')
    label.grid(row=4,column=0)


    # Progress bar widget
    progress = customtkinter.CTkProgressBar(rootMainPage, orientation="horizontal", width=600, height = 20, progress_color='#76ABAE', fg_color="#EEEEEE", corner_radius=100)
    # progress = ttk.Progressbar(root, style="CustomColor.Horizontal.TProgressbar", orient='horizontal', length=600, mode='determinate')
    progress.grid(row=6, column=0, pady=(0,0))
    progress.set(0)

    label_loading = tk.Label(rootMainPage, text="Creating Load Balancer....", font=('Jua', 20, 'bold'), fg="white", bg='#242424')
    label_loading.place(x = 198, y = 480)

    continue_button_image = tk.PhotoImage(file="Images\continue-button-image.png")

    # Start loading progress
    thread = threading.Thread(target=simulate_loading, args=(rootMainPage,))
    thread.start()

    rootMainPage.protocol("WM_DELETE_WINDOW", on_closing)
    # Start the GUI
    rootMainPage.mainloop()

firstPage()
if terminateAllWindows == False:
    second_page()


