#import libs

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import random
import time
import cloudscraper
import warnings

#prepare tools and initialize variables

warnings.filterwarnings("ignore") #ignore warnings

scraper = cloudscraper.CloudScraper() #escape autoban

agents = open('desktop_user_agent.txt').readlines()
user_agents_list = [line[:-2] for line in agents] #escape autoban

URL = 'http://kremlin.ru'

n = 1

df = pd.DataFrame(columns=['doc_type','name','number','date','description','text'])

#define functions

def date_is_too_old(date_start, date):
    return date < date_start

def date_is_too_early(date_finish, date):
    return date > date_finish

def make_date(date):
    d = date.split("-")
    d = datetime.datetime(int(d[0]), int(d[1]), int(d[2]))
    return d

#catch input data

date_start = make_date(input("type start date in yyyy-mm-dd format"))

date_finish = make_date(input("type finish date in yyyy-mm-dd format"))

#check dates

if date_start < date_finish:
    pass
else:
    print('dates aren\'t correct')

#parse

while(1):
    
    #escape autoban
    
    time.sleep(2)
    
    #get n-th page's data
    
    page_url = URL + '/acts/bank/page/'+ str(n)
    response = scraper.get(page_url, headers={'User-Agent': random.choice(user_agents_list)})
    
    print('page ' + str(n) + ' response = ', response)
    
    text = bs(response.text, "lxml")
    
    #find all dates at this page and check them
    
    page_dates = [make_date(str(d).split("\"")[1]) for d in text.find_all('time')]
    
    if False not in [date_is_too_old(date_start, d) for d in page_dates]:
        print('that\'s all, break')
        break
        
    if False not in [date_is_too_early(date_finish, d) for d in page_dates]:
        print('date is too early, continue')
        n += 1
        continue
        
    #find all events at this page
    
    events = text.find_all('h3', 'hentry__title hentry__title_special')
    
    
    for event in events:
        
        #escape autoban
        
        time.sleep(2)
        
        #check event's date
        
        date = make_date(str(event.find('time')).split("\"")[1])
        if date_is_too_early(date_finish, date):
            continue
        if date_is_too_old(date_start, date):
            break
        
        #try to find event's description
            
        description = event.find('span', 'hentry__meta_acts')
        if not description:
            description = bs("")
        description = description.text
        
        #get other variables (name, doc_type, number)
        
        start_name = str(event.find('a')).find('>')+1
        end_name = str(event.find('a')).find('<s')-1
        start_number = str(event.find('a')).find('№')+2
        end_doc_type = str(event.find('a')).find('от ')-1
        
        name = str(event.find('a'))[start_name:end_name]
        
        number = str(event.find('a'))[start_number:end_name]
        
        doc_type = str(event.find('a'))[start_name:end_doc_type]
        
        #get document's text
        
        text_url = URL + str(event.find('a')).split('"')[1]
        
        response = scraper.get(text_url, headers={'User-Agent': random.choice(user_agents_list)})
        
        print('response = ', response)
        
        doc_text = bs(response.text,"lxml").find('div', 'reader_act_body').text
        
        #create and append doc data to table
        
        row = pd.DataFrame({'doc_type':doc_type,'name':name,'number':number,'date':date,'description':description,'text':doc_text})
        
        df = df.append(row ,ignore_index=True)
        
    #go to the next page
    
    n += 1

#import table to .csv

df.to_csv("table.csv", index=False)
