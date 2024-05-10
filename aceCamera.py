import cv2
import tkinter as tk
from PIL import ImageTk, Image
import datetime

def update():
    window = tk.Tk()
    capture = cv2.VideoCapture(0)
    recording = False
    video_writer = None

    def capture_image():
        ret, frame = capture.read()
        if ret:
            current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"captured_image_{current_datetime}.jpg"
            cv2.imwrite(filename, frame)

    def record_video():
        global recording, video_writer
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"recorded_video_{current_datetime}.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (int(capture.get(3)), int(capture.get(4))))
        recording = True
        record_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)

    def stop_video():
        global recording, video_writer
        recording = False
        try:
            video_writer.release()
        except:
            pass
        record_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

    def open_camera():  
    
        photo_button.config(command=lambda: capture_image())
        record_button.config(command=lambda: record_video())
        stop_button.config(command=lambda: stop_video())
    
        ret, frame = capture.read()
        if ret:
            photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), master=window)
            canvas.create_image(0,0,image=photo,anchor=tk.NW)
            canvas.photo = photo
        window.after(10,open_camera)
    
        if recording:
            video_writer.write(frame)
        
    def on_closing():
        capture.release()
        window.destroy()

    window.config(bg="#1c1c1c")
    window.geometry("625x625")
    window.title("Camera")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    canvas = tk.Canvas(window,width=600,height=480)
    canvas.grid(row=0,column=0,columnspan=3,padx=10,pady=10)

    photo_button_image = ImageTk.PhotoImage(Image.open(r"\GUI Images\Ace_Camera.png"), master=window)
    photo_button = tk.Button(window,image=photo_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")
    photo_button.grid(row=1,column=1,padx=15,pady=15)

    record_button_image = ImageTk.PhotoImage(Image.open(r"\GUI Images\Ace_Recording.png"), master=window)
    record_button = tk.Button(window,image=record_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")
    record_button.grid(row=1,column=0,padx=10,pady=10,sticky='e')

    stop_button_image = ImageTk.PhotoImage(Image.open(r"\GUI Images\Ace_Stop_Recording.png"), master=window)
    stop_button = tk.Button(window,image=stop_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")
    stop_button.grid(row=1,column=2,padx=10,pady=10,sticky='w')

    open_camera()

    window.mainloop()
