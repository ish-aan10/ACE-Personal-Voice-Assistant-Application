import nltk
import re
import requests
from newsapi import NewsApiClient
import os
import webbrowser
import threading
import time
import wikipedia
import datetime
import random
import wolframalpha

wolf_api_key = os.environ.get('WOLF_API_ID')
news_api_key = os.environ.get('NEWS_API_ID')
client = wolframalpha.Client(app_id=wolf_api_key)

def identify_curse_words(text):
    
    tokens = nltk.word_tokenize(text.lower())
    curses = ['suck', 'fuck', 'ass' ,'asshole', 'motherfucker', 'moron', 'bitch', 'fucking', 'stupid', 'dick', 'pussy']
    
    for token in tokens:
        if token in curses:
            return True
        
    return False

def identify_greet(text):
    
    greetings = ["hi", "hello", "hey", "howdy", "greetings", "morning", "afternoon", "evening", "greet", "wish"]
    tokens = nltk.word_tokenize(text.lower())
    
    for token in tokens:
        if token in greetings:
            return True
    
    return False

def identify_math_exp(text):
    
    tokens = nltk.word_tokenize(text)
    expr_pattern = r'\d+(\.\d+)?\s*[\+\-\*/]\s*\d+(\.\d+)?'
    
    matches = re.search(expr_pattern, ' '.join(tokens))
    
    if matches:
        return True
    else:
        return False
    
def identify_question(text):
    
    words = nltk.word_tokenize(text)
    first_word = words[0].lower() if words else ""

    if text.strip().endswith("?"):
        return True

    question_words = ["who", "what", "when", "where", "why", "how", "which","weather"]
    if first_word in question_words:
        return True
    
    auxiliary_verbs = ["do", "does", "did", "can", "could", "will", "would", "is", "are", "was", "were",
                       "am", "have", "has", "had", "may", "might", "must", "should", "shall"]
    if first_word in auxiliary_verbs:
        return True

    return False

def greet(logged,username):
    text = ""
    hour = int(datetime.datetime.now().hour)
    
    if(hour >= 0 and hour < 12):
        greeting="Good Morning!"
    elif(hour >= 12 and hour < 16):
        greeting="Good Afternoon!"
    else:
        greeting="Good Evening!"
    
    if logged:
        greeting = greeting + " " + username
    
    greet_text =["How may I assist you?", "ACE!! at your service.","Ready to tackle the day?", "I'm here to help.", "Don't hesitate to ask.", "I'm all ears!", "Your wish is my command", "Let me know what you need.", "How can I make your day better"]
    text = text + greeting +"\n" + greet_text[random.randrange(len(greet_text))]
    return text

def get_date():
    numDate = datetime.date.today()
    strDate = numDate.strftime("%B %d, %Y")
    return f"It's {strDate}"

def get_day():
    numDate = datetime.date.today()
    strDat = numDate.strftime("%A")
    return f"today is {strDat}"

def get_time():
    strTime = datetime.datetime.now().strftime("%I:%M %p")    
    return f"current time is {strTime}"

def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def open_site(words):
    
    site = words.split()
    web_site = ''.join(site[1:])
    
    def open_website():
        time.sleep(2.5)
        webbrowser.open(f"https://www.{web_site}.com")
        
    threading.Thread(target=open_website,).start()
        
    return f"Opening {web_site}"
    
def fetch_news(text):
    
    newsapi = NewsApiClient(api_key=news_api_key)
    news = []
    
    category = ['general', 'business', 'entertainment', 'health', 'science', 'sports', 'technology', 'politics']
    
    specific = ""
    
    tokens = nltk.word_tokenize(text)
    for token in tokens:
        if token in category:
            specific = token
            
    if specific:
        top_headlines = newsapi.get_top_headlines(category=specific,language='en',country='in',page_size=5)
    else:
        top_headlines = newsapi.get_top_headlines(language='en',country='in',page_size=5)
    
    articles = top_headlines['articles']
    for article in articles:
        news.append(f"TITLE:\n{article['title']} \nDESCRIPTION:\n{article['description']} \n")
        
    return news 

def math_function(words):
    flag = False
    strings = ['calculate', 'evaluate', 'what is','result of','find']
    for x in strings:
        if x in words:
            i = words.index(x)
            flag = True
            
    if flag:
        expression = words.split()[i + 1:]
    else:
        expression = words  
               
    result = client.query(' '.join(expression))
    answer_str = next(result.results).text
    try:
        answer = float(answer_str)
        answer = round(answer, 4)
        text = f"The result is: {answer}"
    except ValueError:
        text = f"The result is: {answer_str}"
            
    return text

def wolfram_function(words):
    res = client.query(words)             
    try:
        result_text = next(res.results).text
        text = result_text
    except StopIteration:
        text = "No results found."
        
    return text

def wiki(words):
    query = words.split(" on wikipedia")[-1].strip() or words.split("on wiki")[-1].strip()
    try:
        result = wikipedia.summary(query, sentences = 3)
    except Exception:
        result = "No results found"
    return result