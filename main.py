import speech_recognition as sr
import pyttsx3
import pyjokes
import threading
from tkinter import scrolledtext
from PIL import ImageTk,Image
import tkinter as tk
import aceDB
import aceFunc
import aceCamera

try:
    import pywhatkit
except Exception as e:
    print("An unexpected error occurred during the import of pywhatkit.")

logged = False
username = ""
last_frame = ""    
root = tk.Tk()
vol = 1.00
rate = 150
voc = 1
ace = pyttsx3.init()
r = sr.Recognizer()

show_password = tk.BooleanVar()   

def on_exit():
    if logged:
        log_out()
    root.destroy()

def get_user_settings():
    global voice, volume, theme
    result = aceDB.get_userSettings(username)
    
    if result:
        voice.set(result[0])
        change_voice()
        volume.set(result[1])
        update_volume(event=None)
        theme.set(result[2])
        change_theme()
    
def get_user_data():
    results = aceDB.get_userData(username)
    
    if results:
        chat_area.configure(state="normal")    
        for row in results:
            result = row[0]
            lines = result.split('\n')
            for line in lines:
                chat_area.insert(tk.END, f"{line}\n")
        chat_area.configure(state="disabled")    
    
def log_out():
    global logged, username 
    content = chat_area.get("1.0", tk.END)
    
    aceDB.logOut(username,voice.get(),volume.get(),theme.get(),content)
    
    chat_area.configure(state="normal")
    chat_area.delete("1.0", tk.END)
    chat_area.configure(state="disabled")
    if setting_frame.winfo_viewable():
        setting_frame.grid_forget()
    logged=False
    username=""    
    main_menu()

def clear_error_message():
    error_label.config(text="")

def log_in_user(uname,pword):
    global logged, username
    if(uname == "" or pword == ""):
        error_label.config(text="All fields must be filled!")
        root.after(3000, clear_error_message)
        return
    flag = aceDB.checkUser(uname)
    if not flag:
        error_label.config(text="User does not exist!")
        root.after(3000, clear_error_message)
        return
    logged = aceDB.login_user(uname,pword)
    if not logged:
        error_label.config(text="Invalid Password!")
        root.after(3000,clear_error_message)
        return
    
    username = uname
    get_user_data()
    get_user_settings()
    main_menu()          

def add_user(uname,pword,cword):
    if uname == "" or pword == "" or cword == "":
        error_label.config(text="All fields must be filled!")
        root.after(3000, clear_error_message)
        return
    elif(cword != pword):
        error_label.config(text="Passwords don't match!")
        root.after(3000, clear_error_message)
        return
    
    flag = aceDB.add_user(uname,pword)
    if not flag:
        error_label.config(text="Username already exists!")
        root.after(3000,clear_error_message)
        return
    
    uname_entry.delete(0, tk.END)
    pass_entry.delete(0,tk.END)
    confirm_pass_entry.delete(0, tk.END)
    setting_menu()

def toggle_password_visibility():
    if show_password.get():
        pass_entry.config(show="")
    else:
        pass_entry.config(show="*")

def change_theme_command():
    current_theme = theme.get()
    new_theme = "light" if current_theme == "dark" else "dark"
    theme.set(new_theme)
    change_theme()

def ace_action(message=None):
    global voc
    if message:
        words = message.lower()
    else:
        words = ace_listen().lower()
        
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, f"You : {words}\n")
    chat_area.configure(state="disabled")
    
    internet = aceFunc.is_internet_available()
    
    while(True):
           
        if("camera" in words or "open camera" in words):
            ace_talk("Opening camera")
            threading.Thread(target=aceCamera.update).start()
        
        elif("ace" in words or "assistant" in words):
            ace_talk("At your service!")   
             
        elif("will you be my" in words or "am i your" in words or "we are" in words):
            if("friend" in words or "buddy" in words):
                ace_talk("Well certainly, as of today we're friends.")
            elif("enemy" in words or "enemies" in words or "rival" in words):
                ace_talk("Beware, thou shall not like this rivalry.")
            else:
                ace_talk("I wish if it was that simple.")
        
        elif("date" in words):
            ace_talk(aceFunc.get_date())
            
        elif("day" in words):
            ace_talk(aceFunc.get_day())

        elif("time" in words):
            ace_talk(aceFunc.get_time())
        
        elif("tell news" in words or "news" in words or "headlines" in words):
            if internet:
                ace_talk("Here are today's headlines")
                news = aceFunc.fetch_news(words)
                
                chat_area.configure(state="normal")
                for item in news:
                    chat_area.insert(tk.END, item + "\n")
                chat_area.configure(state="disabled")                
            else:
                ace_talk("Sorry, no connection available")
    
        elif("exit" in words or "close" in words):
            ace_talk("See you soon")
            on_exit()
        
        elif("joke" in words or "tell a joke" in words):
            ace_talk(pyjokes.get_joke())
        
        elif("i love you" in words or "i am in love with you" in words):
            ace_talk("I am sorry but I cannot help u with that.")
               
        elif("search for" in words or "on google" in words):
            sch = words
            if("search for" in sch):
                sch = sch.split("search for")[-1]
            if("on google" in sch):
                sch = sch.split("on google")[0]
            if internet:
                try:
                    ace_talk(f"Here are the results on {sch}")
                    pywhatkit.search(sch)
                except Exception:
                    ace_talk("Unexpected error occurred.")
            else:
                ace_talk("Sorry for the inconvenience, internet is not currently available, please check your connection and try again.")
        
        elif("wikipedia" in words or "wiki" in words):
            if internet:
                ace_talk(aceFunc.wiki(words))
            else:
                ace_talk("Sorry for the inconvenience, internet is not currently available, please check your connection and try again.")            
        
        elif("play" in words or "on youtube" in words):
            play = words.split("on youtube")[0]
            play = play.split("play")[-1]
            if internet:
                try: 
                    ace_talk(f"Playing {play} on youtube.")
                    pywhatkit.playonyt(play)
                except Exception:
                    ace_talk("Unexpected error occurred.")
            else:
                ace_talk("Sorry for the inconvenience, internet is not currently available, please check your connection and try again.")
        
        elif("change voice" in words or "your voice" in words):
            voc = 1 - voc
            ace_talk("Hello!, Voice changed.")
        
        elif("..." in words):
            break
        
        elif("change theme" in words):
            change_theme_command()
            ace_talk("Theme Changed.")
        
        elif("open" in words):
            if internet:
                ace_talk(aceFunc.open_site(words))
            else:
                ace_talk("Sorry for the inconvenience, internet is not currently available, please check your connection and try again.")
        
        elif aceFunc.identify_math_exp(words):
            if internet:
                ace_talk(aceFunc.math_function(words))
            else:
                ace_talk("Internet is not currently available, please check your connection and try again.")
        
        elif aceFunc.identify_curse_words(words):
            ace_talk("Please talk to me appropriately.")
        
        elif aceFunc.identify_question(words):
            if("what can you do" in words):
                ace_talk("I can perform various basic tasks such as opening websites, making online searches, playing musics/videos, tell jokes and vice versa.")
            elif("who i am" in words or "who am i" in words):
                if logged:
                    ace_talk(f"You are {username}, my friend.")
                else:
                    ace_talk("If you talk, then definitely you're a human.")
            elif("your name" in words or "who are you" in words):
                if logged:
                    ace_talk(f"My name's Ace, and I'm here to assist you, {username}.")
                else:
                    ace_talk("My name's Ace. I'm looking forward to work alongside you.")
            elif("who made you" in words or "who created you" in words or "who are your creators" in words):
                ace_talk("I have been created by Ishaan Kumar and Sania Nisha.")
            elif("is love" in words or "what do you think about love" in words):
                ace_talk("It is the 7th sense that destroys all the other 6 senses.")
            else:
                if internet:
                    ace_talk(aceFunc.wolfram_function(words))
                else:
                    ace_talk("Sorry for the inconvenience, internet is not currently available, please check your connection and try again.")
        
        elif aceFunc.identify_greet(words):
            ace_talk(aceFunc.greet(logged,username)) 
        
        else:
            ace_talk("Sorry! I can't do that.")
        break
        
def display_listening():
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, f"ACE : Listening\n")
    chat_area.configure(state="disabled")
    root.update()

def display_recognizing():
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, f"ACE : Recognizing\n")
    chat_area.configure(state="disabled")
    root.update()
    
def ace_listen():
    display_listening()
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src)
        r.pause_threshold = 0.85
        audio = r.listen(src)
    
    display_recognizing()
    try:
        words = r.recognize_google(audio,language="en-in")
    except sr.RequestError as e:
        return "..."
    except sr.UnknownValueError:
        return "..."
      
    return words

def send_message(message):
    if(message == "Enter Message..." or message.strip() == ""):
        return
    if message.strip():
        chat_entry.delete(0, tk.END)
        
        threading.Thread(target=ace_action, args=(message,)).start()

def ace_talk(text):
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, f"ACE : {text}\n")
    root.update()
    
    voices = ace.getProperty("voices")
    
    ace.setProperty('voice',voices[voc].id)
    ace.setProperty('rate',rate)
    ace.setProperty('volume',vol)
    try:
        ace.say(text)
        ace.runAndWait()
    except Exception as e:
        chat_area.insert(tk.END, "ACE : Wait, processing another instance.\n")
    chat_area.configure(state="disabled")

def change_voice():
    global voc
    ch = voice.get()
    if(ch == "female"):
        voc = 1
    else:
        voc = 0

def update_volume(event):
    global vol
    vol = float(volume.get())/100

def voice_rate(*args):
    global rate
    ch = voice_speed.get()
    if(ch=="0.5x"):
        rate = 50
    elif(ch=="0.75x"):
        rate = 75
    elif(ch=="1.0x"):
        rate = 100
    elif(ch=="1.5x"):
        rate = 150
    else:
        rate = 200

def change_theme():
    bg_color = "#FFFFFF" if theme.get() == 'light' else "#1c1c1c"
    fg_color = "#000000" if theme.get() == 'light' else "#8C52FF"
    active_fg_color = "#000000" if theme.get() == "light" else "#FFFFFF"
    
    root.config(
        bg="#dfd4e8" if theme.get() == 'light' else "#232324"
    )
    main_frame.config(bg=bg_color)
    setting_frame.config(bg=bg_color)
    chat_frame.config(bg=bg_color)
    login_frame.config(bg=bg_color)
    signup_frame.config(bg=bg_color)
    ace_button.config(bg=bg_color,activebackground=bg_color)
    setting_button.config(bg=bg_color,activebackground=bg_color)
    back_button.config(bg=bg_color,activebackground=bg_color)
    send_button.config(bg=bg_color,activebackground=bg_color)
    chat_button.config(bg=bg_color,activebackground=bg_color)
    login_button.config(fg=bg_color,activeforeground=bg_color)
    signup_button.config(fg=bg_color,activeforeground=bg_color)
    back.config(fg=bg_color,activeforeground=bg_color)
    chat_area.config(
        bg="#DFB2FF" if theme.get() == "light" else "#232324",
        fg=fg_color
    )
    chat_entry.config(
        bg="#DFB2FF" if theme.get() == "light" else "#232324",
        fg=fg_color,
        insertbackground=fg_color
    )
    uname_entry.config(
        bg="#DFB2FF" if theme.get() == "light" else "#232324",
        fg=fg_color,
        insertbackground=fg_color
    )
    pass_entry.config(
        bg="#DFB2FF" if theme.get() == "light" else "#232324",
        fg="black" if theme.get() == "light" else "#4fe873",
        insertbackground=fg_color
    )
    confirm_pass_entry.config(
        bg="#DFB2FF" if theme.get() == "light" else "#232324",
        fg="black" if theme.get() == "light" else "#4fe873",
        insertbackground=fg_color
    )
    label.config(bg=bg_color)
    desc.config(bg=bg_color)
    theme_label.config(bg=bg_color)
    voice_label.config(bg=bg_color)
    volume_label.config(bg=bg_color)
    voice_speed_label.config(bg=bg_color)
    uname_label.config(bg=bg_color)
    pass_label.config(bg=bg_color)
    confirm_pass_label.config(bg=bg_color)
    error_label.config(bg=bg_color)
    show_checkbox.config(
        bg=bg_color,
        selectcolor=bg_color,
        fg="black" if theme.get() == "light" else "#4fe873",
        activeforeground="black" if theme.get() == "light" else "#4fe873",
        activebackground=bg_color
    )
    theme_dark.config(bg=bg_color,activebackground=bg_color,activeforeground=active_fg_color,selectcolor=bg_color)
    theme_light.config(bg=bg_color,activebackground=bg_color,activeforeground=active_fg_color,selectcolor=bg_color)
    vc_male.config(bg=bg_color,activebackground=bg_color,selectcolor=bg_color)
    vc_female.config(bg=bg_color,activebackground=bg_color,selectcolor=bg_color)
    voice_speed_options.config(bg=bg_color,activebackground=bg_color,activeforeground=active_fg_color)
    voice_speed_options["menu"].config(bg=bg_color,activebackground=bg_color,activeforeground=active_fg_color)
    volume.config(bg=bg_color,activebackground=bg_color)

def on_entry_click(event):
    if(chat_entry.get() == "Enter Message..."):
        chat_entry.delete(0, tk.END)
        
def on_focus_out(event):
    if(chat_entry.get() == ""):
        chat_entry.insert(0, "Enter Message...")

def clicked():
    if main_frame.winfo_viewable():
        main_frame.grid_forget()
        chat_menu()
    if chat_frame.winfo_viewable():
        if aceFunc.is_internet_available():
            ace_action()
        else:
            ace_talk("Sorry, due to no internet connection voice recognition cannot be performed.")
            
def back_function():
    global last_frame
    if chat_frame.winfo_viewable():
        chat_frame.grid_forget()
        main_menu()
    if setting_frame.winfo_viewable():
        setting_frame.grid_forget()
        if last_frame == 'main':
            main_menu()
        else:
            chat_menu()
    if login_frame.winfo_viewable():
        login_frame.grid_forget()
        setting_menu()
    if signup_frame.winfo_viewable():
        signup_frame.grid_forget()
        setting_menu()
        
    uname_entry.delete(0, tk.END)
    pass_entry.delete(0, tk.END)
    confirm_pass_entry.delete(0, tk.END)
    
def setting_menu():
    global last_frame
    if logged:
        root.geometry("360x430")
    else:
        root.geometry("360x480")
    if signup_frame.winfo_viewable():
        signup_frame.grid_forget()
    if chat_frame.winfo_viewable():
        chat_frame.grid_forget()
        last_frame = "chat"
    if main_frame.winfo_viewable():
        main_frame.grid_forget()
        last_frame = "main"
    setting_frame.grid(row=0,column=0,padx=20,pady=20)
    
    label.config(text="Settings",font=("Berlin Sans FB",42))
    label.grid(in_=setting_frame,row=0,column=0,columnspan=3,padx=20,pady=20)
    
    voice_label.grid(in_=setting_frame,row=1,column=0,sticky='W',padx=5)
    volume_label.grid(in_=setting_frame,row=2,column=0,sticky='W',padx=5)
    voice_speed_label.grid(in_=setting_frame,row=3,column=0,sticky='W',padx=5)
    theme_label.grid(in_=setting_frame,row=4,column=0,sticky='W',padx=5)
    
    back_button.config(command=lambda: back_function())
    back_button.grid(in_=setting_frame,row=7,column=0,columnspan=3,padx=10,pady=10)
    
    vc_male.config(command=lambda: change_voice())
    vc_male.grid(in_=setting_frame,row=1,column=1,sticky='W',padx=5)
    vc_female.config(command=lambda: change_voice())
    vc_female.grid(in_=setting_frame,row=1,column=2,sticky='W',padx=5)
    
    volume.config(command=lambda event: update_volume(event))
    volume.grid(in_=setting_frame,row=2,column=1,columnspan=2,padx=5,ipadx=40,pady=5)
    
    voice_speed_options.grid(in_=setting_frame,row=3,column=1,columnspan=2,padx=5,pady=5)
    voice_speed.trace_add("write", voice_rate)
    
    theme_dark.config(command=lambda: change_theme())
    theme_dark.grid(in_=setting_frame,row=4,column=1,sticky='W',padx=5)
    theme_light.config(command=lambda: change_theme())
    theme_light.grid(in_=setting_frame,row=4,column=2,sticky='W',padx=5)
    
    if logged:
        login_button.config(text="Log Out",command=lambda: log_out())
        login_button.grid(in_=setting_frame,row=5,column=0,columnspan=3,padx=5,pady=5,sticky="")
        signup_button.grid_forget()
    else:
        login_button.config(text="Log In",command=lambda: login_menu())
        login_button.grid(in_=setting_frame,row=5,column=0,columnspan=3,padx=5,pady=5,sticky="")
        signup_button.config(command=lambda: signup_menu())
        signup_button.grid(in_=setting_frame,row=6,column=0,columnspan=3,padx=5,pady=5,sticky="")
    
def chat_menu():
    root.geometry("485x690")
    if main_frame.winfo_viewable():
        main_frame.grid_forget()
    chat_frame.grid(row=0,column=0,padx=20,pady=20)
        
    chat_area.grid(in_=chat_frame,row=0,column=0,columnspan=3,padx=10,pady=10,sticky="nsew")
    
    chat_entry.grid(in_=chat_frame,row=1,column=0,columnspan=3,padx=10,pady=10,sticky="nsw")
    
    send_button.config(command=lambda: send_message(chat_entry.get()))
    send_button.grid(in_=chat_frame,row=1,column=2,padx=5,pady=5,sticky='E')
    
    ace_button.config(command=lambda: clicked())
    ace_button.grid(in_=chat_frame,row=2,column=1,padx=10,pady=10)
    
    back_button.config(command=lambda: back_function())
    back_button.grid(in_=chat_frame,row=2,column=0,columnspan=1,padx=10,pady=10)
    
    setting_button.config(command=lambda: setting_menu())
    setting_button.grid(in_=chat_frame,row=2,column=2,padx=10,pady=10)

def main_menu():
    root.geometry("360x420")
    if login_frame.winfo_viewable():
        login_frame.grid_forget()
        uname_entry.delete(0, tk.END)
        pass_entry.delete(0,tk.END)
    main_frame.grid(row=0,column=0,padx=20,pady=20)
    
    label.config(text="ACE",font=("Bauhaus 93",42),width=9)
    label.grid(in_=main_frame,row=0,column=0,columnspan=3,padx=20,pady=20)
    
    if logged:
        desc.config(text=f"Logged in as {username}") 
    else:
        desc.config(text="Hola!")
    desc.grid(in_=main_frame,row=3,column=1)
    
    ace_button.config(command=lambda: clicked())
    ace_button.grid(in_=main_frame,row=2,column=1,padx=10,pady=10)
    
    setting_button.config(command=lambda: setting_menu())
    setting_button.grid(in_=main_frame,row=4,column=1,padx=10,pady=10)
    
    chat_button.config(command=lambda: chat_menu())
    chat_button.grid(in_=main_frame,row=5,column=1,padx=10,pady=10)

def signup_menu():
    root.geometry("490x405")
    if setting_frame.winfo_viewable():
        setting_frame.grid_forget()
    signup_frame.grid(row=0,column=0,padx=20,pady=20)
    
    label.config(text="Sign Up",font=("Bauhaus 93",42))
    label.grid(in_=signup_frame,row=0,column=0,columnspan=2,padx=20,pady=20)
    
    uname_label.grid(in_=signup_frame,row=1,column=0,padx=5,pady=5,sticky='W')
    uname_entry.grid(in_=signup_frame,row=1,column=1,padx=5,pady=5)
    pass_label.grid(in_=signup_frame,row=2,column=0,padx=5,pady=5,sticky='W')
    pass_entry.grid(in_=signup_frame,row=2,column=1,padx=5,pady=5)
    confirm_pass_label.grid(in_=signup_frame,row=3,column=0,padx=5,pady=5,sticky='W')
    confirm_pass_entry.grid(in_=signup_frame,row=3,column=1,padx=5,pady=5)
    
    show_checkbox.grid(in_=signup_frame,row=4,column=1,padx=5,pady=5,sticky='W')
    
    error_label.grid(in_=signup_frame,row=6,column=1,padx=5,pady=5,sticky='W')
    
    signup_button.config(command=lambda: add_user(uname_entry.get(),pass_entry.get(),confirm_pass_entry.get()))
    signup_button.grid(in_=signup_frame,row=7,column=1,columnspan=1,padx=5,pady=5,sticky='W')
    
    back.config(command=lambda: back_function())
    back.grid(in_=signup_frame,row=7,column=0,padx=5,pady=5,sticky='E')

def login_menu():
    root.geometry("410x360")
    if setting_frame.winfo_viewable():
        setting_frame.grid_forget()
    login_frame.grid(row=0,column=0,padx=20,pady=20)
    
    label.config(text="Log In",font=("Bauhaus 93",42))
    label.grid(in_=login_frame,row=0,column=0,columnspan=2,padx=20,pady=20)
    
    uname_label.grid(in_=login_frame,row=1,column=0,padx=5,pady=5,sticky='W')
    uname_entry.grid(in_=login_frame,row=1,column=1,padx=5,pady=5)
    pass_label.grid(in_=login_frame,row=2,column=0,padx=5,pady=5,sticky='W')
    pass_entry.grid(in_=login_frame,row=2,column=1,padx=5,pady=5)
    
    show_checkbox.grid(in_=login_frame,row=3,column=1,padx=5,pady=5,sticky='W')
    
    error_label.grid(in_=login_frame,row=4,column=1,padx=5,pady=5,sticky='W')
    
    login_button.config(text="Log In",command=lambda: log_in_user(uname_entry.get(),pass_entry.get()))
    login_button.grid(in_=login_frame,row=5,column=1,columnspan=1,padx=5,pady=5,sticky='W')
    
    back.config(command=lambda: back_function())
    back.grid(in_=login_frame,row=5,column=0,padx=5,pady=5,sticky='E')

ace_icon = ImageTk.PhotoImage(file=r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Ace_Icon_Logo.png")
root.title("ACE")
root.config(bg="#232324")
root.iconphoto(False,ace_icon)

signup_frame = tk.Frame(root,bg="#1c1c1c")
login_frame = tk.Frame(root,bg="#1c1c1c")
main_frame = tk.Frame(root,bg="#1c1c1c")
setting_frame = tk.Frame(root,bg="#1c1c1c")
chat_frame = tk.Frame(root,bg="#1c1c1c")

label = tk.Label(bg="#1c1c1c",fg="#8C52FF")
desc = tk.Label(text="",font=("Berlin Sans FB",16),bg="#1c1c1c",fg="#8C52FF")

voice_label = tk.Label(text="Voice:",font=("Consolas",12,"bold"),bg="#1c1c1c",fg="#8C52FF")
volume_label = tk.Label(text="Volume:",font=("Consolas",12,"bold"),bg="#1c1c1c",fg="#8C52FF")
voice_speed_label = tk.Label(text="Voice Speed:",font=("Consolas",12,"bold"),bg="#1c1c1c",fg="#8C52FF")
theme_label = tk.Label(text="Theme:",font=("Consolas",12,"bold"),bg="#1c1c1c",fg="#8C52FF")
 
ace_button_image = ImageTk.PhotoImage(Image.open(r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Ace_Logo.png"))
ace_button = tk.Button(image=ace_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")

setting_button_image = ImageTk.PhotoImage(Image.open(r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Setting_Logo.png"))
setting_button = tk.Button(image=setting_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")

chat_button_image = ImageTk.PhotoImage(Image.open(r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Ace_Chat.png"))
chat_button = tk.Button(image=chat_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")

send_button_image = ImageTk.PhotoImage(Image.open(r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Send_Logo.png"))
send_button = tk.Button(image=send_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")

back_button_image = ImageTk.PhotoImage(Image.open(r"D:\Core\BCA\Project\Final Year\Voice Assistant\GUI Images\Back_Logo.png"))
back_button = tk.Button(image=back_button_image,border=0,bg="#1c1c1c",activebackground="#1c1c1c")

login_button = tk.Button(text="",border=0,fg="#1c1c1c",bg="#8C52FF",activeforeground="#1c1c1c",activebackground="#8C52FF",font=("Bahnschrift",16),width=8)
signup_button = tk.Button(text="Sign Up",border=0,fg="#1c1c1c",bg="#8C52FF",activeforeground="#1c1c1c",activebackground="#8C52FF",font=("Bahnschrift",16),width=8)

back = tk.Button(text="Back",border=0,fg="#1c1c1c",bg="#8C52FF",activeforeground="#1c1c1c",activebackground="#8C52FF",font=("Bahnschrift",16),width=8)

uname_label = tk.Label(text="Username",font=("Bahnschrift",16),bg="#1c1c1c",fg="#8C52FF")
pass_label = tk.Label(text="Password:",bg="#1c1c1c",fg="#8C52FF",font=("Bahnschrift",16))
confirm_pass_label  = tk.Label(text="Confirm Password:",bg="#1c1c1c",fg="#8C52FF",font=("Bahnschrift",16))

uname_entry = tk.Entry(insertbackground="#8C52FF",bg="#232324",fg="#8C52FF",font=("Bahnschrift",16))
pass_entry = tk.Entry(insertbackground="#8C52FF",bg="#232324",show="*",fg="#4fe873",font=("Bahnschrift",16))
confirm_pass_entry = tk.Entry(insertbackground="#8C52FF",bg="#232324",show="*",fg="#4fe873",font=("Bahnschrift",16))

show_checkbox = tk.Checkbutton(bg="#1c1c1c",fg="#4fe873",activebackground="#1c1c1c",activeforeground="#4fe873",selectcolor="#1c1c1c",text="Show Password",variable=show_password,font=("Bahnschrift",12),command=lambda: toggle_password_visibility())

error_label = tk.Label(text="",fg="red",bg="#1c1c1c",font=("Bahnschrift",16))

chat_area = scrolledtext.ScrolledText(font=("Consolas",12),bg="#232324",wrap=tk.WORD,fg="#8C52FF",width=45,height=25,state="disabled")

chat_entry = tk.Entry(insertbackground="#8C52FF",bg="#232324",fg="#8C52FF",font=("Consolas",12),width=40)
chat_entry.insert(0, "Enter Message...")
chat_entry.bind("<FocusIn>", lambda event: on_entry_click(event))
chat_entry.bind("<FocusOut>", lambda event: on_focus_out(event))
chat_entry.bind("<Return>", lambda event: send_message(chat_entry.get()))

voice = tk.StringVar(value="female")
vc_male = tk.Radiobutton(text="Male",value="male",variable=voice,bg="#1c1c1c",font=("Consolas",12),fg="#8C52FF",activebackground="#1c1c1c",activeforeground="#0066ff",selectcolor="#1c1c1c")
vc_female = tk.Radiobutton(text="Female",value="female",variable=voice,bg="#1c1c1c",font=("Consolas",12),fg="#8C52FF",activebackground="#1c1c1c",activeforeground="#ff33cc",selectcolor="#1c1c1c")

volume = tk.Scale(from_=0,to=100,orient="horizontal",resolution=0.5,bg="#1c1c1c",fg="#8C52FF",font=("Consolas",12),highlightthickness=0,troughcolor="#8C52FF",activebackground="#1c1c1c")
volume.set(100)

voice_speed = tk.StringVar(root)
voice_speed.set("1.5x")
voice_speed_options = tk.OptionMenu(root,voice_speed,"0.5x","0.75x","1.0x","1.5x","2.0x")
voice_speed_options.config(bg="#1c1c1c",highlightthickness=0,fg="#8C52FF",font=("Consolas",12),activebackground="#1c1c1c",activeforeground="white",width=5)
voice_speed_options["menu"].config(bg="#1c1c1c",fg="#8C52FF",font=("Consolas",12),activebackground="#1c1c1c",activeforeground="white")

theme = tk.StringVar(value="dark")
theme_dark = tk.Radiobutton(text="Dark",value="dark",variable=theme,font=("Consolas",12),bg="#1c1c1c",fg="#8C52FF",activeforeground="white",activebackground="#1c1c1c",selectcolor="#1c1c1c")
theme_light = tk.Radiobutton(text="Light",value="light",variable=theme,font=("Consolas",12),bg="#1c1c1c",fg="#8C52FF",activeforeground="white",activebackground="#1c1c1c",selectcolor="#1c1c1c")

root.protocol("WM_DELETE_WINDOW", on_exit)

main_menu()
root.mainloop()