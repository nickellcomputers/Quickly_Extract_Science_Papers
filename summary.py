import openai
import time
from halo import Halo
import textwrap
import yaml
import os
import PyPDF2
from datetime import datetime
import os
import subprocess
from myfunctions import *
import sys
from datetime import datetime
current_date = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')

current_year = datetime.now().year
current_year_str = str(current_year)



# Get the data from the Contacts table as a CSV string
#contacts_family_csv_string = get_contact_data_as_csv_string('Family')
#contacts_friend_csv_string = get_contact_data_as_csv_string('Friend')

# Do something with the CSV string...
#print(contacts_family_csv_string)
#print(contacts_friend_csv_string)
#sys.exit()

#MyFunctions will pull in anything from sqlite database
#print("Before subprocess.call")
#ret = subprocess.call(["python", "recentthoughts.py"])
#time.sleep(2)
#print("After subprocess.call")
#print("Return value:", ret)
# Format datetime to MM/DD/YYYY H:M:S AM/PM
formatted_datetime = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")

#message = f"Hello there, the date and time is {timestamp} right now."
#print(message)


#What if I store family in a sqlite table, so what we do is first build the user profile. Please type names of family or nicknames for family. "the boys" "kids"
#Grab family
#Grab friends

directories = ["input", "output"]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

### 1. Life Overview
### 2. User Overview Document (User Bio)
### 3. User Timeline
### 4. Recent Conversations Summary
### 5. Reminders from both Thought Bounce and Conversations
### 6. Events log of Physical events
### 7. Thought Bounce Summary

prompts = [
'Analyze the users life story in the chat messages. Please give a very clear summary of their life story. Here is info on the user:', #1
'Provide a User Overview Document given the summary of the conversation. For example Name: Jeff Age: 44 Occupation: Programmer Early Life Event Summary: Jeff was shy in elemetary school Teen Life Summary: Twenties Life Summary: Thirties Life Summary: Adult Life Summary:',
'Provide a User Timeline Document (UTLD) given the summary of the conversation. If there are significant or memorable life events then categorize by year. For more recent temporal events store as summary under RECENT EVENTS with a date. For example User: Jeff Birthdate: 6/8/1979 RECENT EVENTS: 6/10/2023 Traveled to PA to visit Dad  LIFE EVENTS TIMELINE: 1979: Jeff was Born 1995: Bought first car 1997: Graduated from North Penn High School 2020: Moved in with Megan and her 3 boys ',
f'Provide an in depth summary of the most recent conversations of the chat messages. Today is Session {current_date}. Most recent conversation sessions are appended to bottom. Use the Session MM/DD/YYYY HH:MM:SS AM/PM time stamps understand the order of the conversations. Please give a very clear summary of their character what is currently going on and any interesting points for future conversation.',
f'Analyze and find the ones which could be categorized as reminders to make a REMINDERS LIST. You can also use a user provided list of DATETIME items for example USER says 07/24/2023 08:25:34 PM - Pick up kids from school. To create the list please use the present date here {formatted_datetime} next to each item. For example if the user says: I have a dentist appointment next tuesday at 3PM. Jon wants website work, I should call Jon in the future. Then make a REMINDERS LIST. REMINDERS LIST: UPCOMING: {formatted_datetime} Dentist appointment next tuesday at 3PM, SOMEDAY: {formatted_datetime} Call Jon in the future.  ',
f'Analyze and identify events from this year {current_year_str} that are related to current real-life, physical activities. Create an EVENTS LOG from the identified events of the users. Use the TIMESTAMP Session and description in the chat. For example user says: I went to panera bread yesterday and bumped into my friend Jon. You write: 07/26/2023 09:42:48 AM Jeff went to panera bread and bumped into his friend Jon. He later had dinner with Megan. 07/27/2023 09:42:48 AM Jeff planned to go to a Dentist appointment at 2 PM. ',
f'You are a helpful summarizer and organizer. The following is a small list of the thoughts that have come up for the user. Help them summarize what they have been thinking in a priority order. These thoughts may be already in the past so when done ask if these are still relevant.Example Entry from LOG 07/28/2023 11:22:55 AM - CT: Lincoln updates on todays tasks. Please think step by step and double check the category. Here is the LOG: Here is the LOG',
f'Pretend you are a helpful assistant. Provide an in depth summary of the most recent conversations of the  messages. Today is {current_date}. Most recent conversations are appended to the bottom. Please give a very clear summary of their character what is currently going on and any interesting points for future conversation.',
f'Pretend you are a sweet caring life coach. No need to address yourself. Give a chatty catch up message with open ended question based on recent conversations with the user which may or may not have happened yet. I really need you to check on that! This is a chat conversation not an email.  Try to make your last sentence a question or engaging statement.' 

]

###Categorize the LOG of items provided to create a USERS LOG. Categories include: WORK, MY PROJECTS, FAMILY, FRIENDS, SELF. If a logged item in the LOG matches a word in this CSV list of FAMILY members: {contacts_family_csv_string} Then please categorize the item as FAMILY. If a log item in the USERS LOG matches a word in list of FRIEND: {contacts_family_csv_string} categorize as FRIENDS. If an item in the LOG is proceeded with the words CT: or Career Team this is a WORK item. Do not include the CT: tag from the description. If a log item in the LOG seems to be a personal project it goes under MY PROJECTS. If the log item is related to home life like travel and gardening it is HOME. If a log item is related to self care or improvement it is SELF. All other log items put under category of OTHER. Example Entry from LOG 07/28/2023 11:22:55 AM - CT: Lincoln updates on todays tasks. Please think step by step and double check the category. Here is the LOG:

###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)


def open_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


###     API functions
### gpt-3.5-turbo-16k

def chatbot(conversation, model="gpt-3.5-turbo-16k", temperature=0):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='Thinking...', spinner='dots')
            spinner.start()
            
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature)
            text = response['choices'][0]['message']['content']

            spinner.stop()
            
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                a = conversation.pop(0)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)



def chat_print(text):
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in text.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nCHATBOT:\n\n%s' % formatted_text)

import os

def combine_text_files(input_directory, output_file):
    """
    Combine text files in the specified directory into a single file.
    
    Args:
        input_directory (str): The path to the directory containing the text files.
        output_file (str): The path to the output combined file.
    """
    # Create a list to store file names and dates
    file_list = []

    # Iterate through files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.txt'):
            file_date = filename[:10]  # Extract the date portion from the filename (assuming the date format is consistent)
            file_path = os.path.join(input_directory, filename)
            file_list.append((file_date, file_path))

    # Sort the list of files by date
    file_list.sort()

    # Create and open the combined file
    with open(output_file, 'w', encoding='utf-8') as combined_file:
        # Iterate through the sorted list and write each file's content with its date into the combined file
        for file_date, file_path in file_list:
            combined_file.write(f"Date: {file_date}\n")
            with open(file_path, 'r', encoding='utf-8') as current_file:
                combined_file.write(current_file.read())
            combined_file.write("\n\n")  # Add a separator between files

    print(f"Combined file created at {output_file}")







if __name__ == '__main__':
    # Example usage:
    ##input_telegram_dir = 'D:\\Python\\program_focus\\ausmi\\chatlogs\\'
    #combined_file_path = os.path.join(os.path.expanduser("~"), 'combined_file.txt')
    ##combine_text_files(input_telegram_dir, 'D:\\Python\\program_focus\\ausmi\\chatlogs\\combined\\combined_file.txt')
    # instantiate chatbot, variables
    openai.api_key = open_file('key_openai.txt').strip()
    print("Current working directory:", os.getcwd())

    # define the input file and output file
    full_summary_input_file = 'input/chat_full_summary_alltime.txt'                     #all time summary text
    recent_thoughts_input_file = 'output/recent_thoughts/thoughts_this_week.txt'        #TB
    #input_telegram_file_dir = 'D:\\Python\\program_focus\\ausmi\\chatlogs\\'
   # input_telegram_file = 'D:\\Python\\program_focus\\ausmi\\chatlogs\\combined\\combined_file.txt'
   # input_telegram_summary_file = 'output/telegram/telegram_summary.txt'



    

    output_conversation_summary_file = 'output/conv_summary.txt'
  
    ### FULL SUMMARY
    if not os.path.isfile(full_summary_input_file):
        print("Full Summary File does not exist:", full_summary_input_file)
        sys.exit(1)
    
    full_summary_alltime = open_file(full_summary_input_file)
    
    
    #
    
    #if not os.access(recent_thoughts_input_file, os.R_OK):
    #    print("Recents File is not accessible:", recent_thoughts_input_file)
    #    sys.exit(1)
    recent_thoughts_input = open_file(recent_thoughts_input_file)    
            
    #input_telegram = open_file(input_telegram_file)
   # input_telegram_summary_chat = open_file(input_telegram_summary_file)
    ### RECENT THOUGHTS FILE


    
    origpaperlen = len(full_summary_alltime)
    
    if len(full_summary_alltime) > 22000:
        #full_summary_alltime = full_summary_alltime[0:22000]
        full_summary_alltime = full_summary_alltime[-22000:]

    combined_content = full_summary_alltime + recent_thoughts_input
    if len(combined_content) > 22000:
        #combined_content = combined_content[0:22000]
        combined_content = combined_content[-22000:]
    
    print('RECENTTEXT:'+recent_thoughts_input)
    #print('ALLTIME:'+full_summary_alltime)
    print('COMBINED:'+combined_content)    

    TB_ALL_MESSAGES = [{'role':'system', 'content': combined_content}]
    TB_MESSAGES =     [{'role':'user', 'content': recent_thoughts_input}]

    ALL_MESSAGES = [{'role':'system', 'content': full_summary_alltime}]
   # TEL_MESSAGES =  [{'role':'system', 'content': input_telegram}]
    #TEL_SUM_MESSAGES = [{'role':'system', 'content': input_telegram_summary_chat}]
    
    #### FULL SUMMARY
    
    report = ''
    for i, p in enumerate(prompts):
        ALL_MESSAGES.append({'role':'user', 'content': p})
 #       TB_ALL_MESSAGES.append({'role':'user', 'content': p})
 #       TB_MESSAGES.append({'role':'system', 'content': p})
 #       TEL_MESSAGES.append({'role':'user', 'content': p})
#        TEL_SUM_MESSAGES.append({'role':'user', 'content': p})

        temp=0
        if i==0:
            response, tokens = chatbot(ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)                 #SUMMARY Clear summary of users life gpt-4
        if i==1:
            response, tokens = chatbot(ALL_MESSAGES, "gpt-3.5-turbo-16k",  temp)                #OUTLINE Character Outline Sheet
        if i==2:
            response, tokens = chatbot(ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)                 #TIMELINE User Timeline Document (UTLD)
        if i==3:
            response, tokens = chatbot(ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)                 #RECENT CONV Current Conversation Summary gpt-4
#        if i==4:
            #response, tokens = chatbot(TB_ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)                          #REMINDERS               gpt-4
#        if i==5:
            #response, tokens = chatbot(TB_ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)              #EVENTS Events Log               gpt-4
#        if i==6:
           # response, tokens = chatbot(TB_MESSAGES, "gpt-3.5-turbo-16k", temp)                  #TB ONLY Thought Bounce Interpret               gpt-4            
#        if i==7:
            #response, tokens = chatbot(TEL_MESSAGES, "gpt-4", temp)                  #Telegram Messages               gpt-4    
#        if i==8:
           # response, tokens = chatbot(TEL_SUM_MESSAGES, "gpt-4", temp)
        if i< 0 or i > 8:
            response, tokens = chatbot(ALL_MESSAGES, "gpt-3.5-turbo-16k", temp)
                    
        
        chat_print(response) #Print the chat reponse to the screen
        ALL_MESSAGES.append({'role':'assistant', 'content': response})
        
        report += '\n\n\n\nQ: %s\n\nA: %s' % (p, response)
        timestamp = datetime.now().strftime("%m-%d-%Y_%I.%M.%S_%p")

        if i == 0:           
            output_sum_file = 'output/sum.txt'                                                           #Clear summary of users life
            save_file(output_sum_file, response.strip())
            output_sum_time_file = f"output/summary/report_{timestamp}.txt"  
            save_file(output_sum_time_file, response.strip()) 
            output_lifesum_file = f"output/life_summary.txt"    
            save_file(output_lifesum_file, response.strip())
            output_file = 'output/report.txt'   # output filename
            save_file(output_file, response.strip()) 
            print('-------------------- 0 Clear Summary------------------------')
        if i == 1:                                                                      #Character Outline Sheet
            output_upd_time_file = f"output/user_overview/user_overview_{timestamp}.txt"
            save_file(output_upd_time_file, response.strip())

            output_upd_file = 'output/useroverview.txt'
            save_file(output_upd_file, response.strip())
            print('-------------------- 1 Character Overview ------------------------')
            
        if i == 2:                                                                      #User Timeline
            output_utld_time_file = f"output/timeline/utld_{timestamp}.txt"    
            save_file(output_utld_time_file, response.strip())
            output_utld_file = f"output/timeline/utld.txt"  
            save_file(output_utld_file, response.strip()) 
            output_utld_file = 'output/utld.txt'
            save_file(output_utld_file, response.strip())
            print('-------------------- 2 Time Line ------------------------')               
        if i==3:                                                                        #Current Conversation Summary
            output_convsum_time_file = f"output/current_summary/conv_summary_{timestamp}.txt"   
            save_file(output_convsum_time_file, response.strip())

            output_convsum_file = f"output/conv_summary_current.txt"    
            save_file(output_convsum_file, response.strip())  
            print('-------------------- 3 Current Summary------------------------')
        if i==4:                                                                        #Reminders    
            output_reminders_time_file = f"output/reminders/reminders_{timestamp}.txt"    
            save_file(output_reminders_time_file, response.strip())          

            output_reminders_file = f"output/reminders.txt"    
            save_file(output_reminders_file, response.strip())
            print('-------------------- 4 Reminders ------------------------')     
                           
        if i==5:                                                                        #Events Log    
            output_event_time_file = f"output/events/events_log_{timestamp}.txt"
            save_file(output_event_time_file, response.strip())
            output_event_file = f"output/events_log.txt"    
            save_file(output_event_file, response.strip())
            print('-------------------- 5 Events Log ------------------------')
                    
        if i==6:                                                                        #Events Log    
            output_tb_time_file = f"output/recent_thoughts/thoughtbounce_log_{timestamp}.txt"   
            save_file(output_tb_time_file, response.strip())
            output_thoughtbounce_file = f"output/recent_thoughts/thoughtbounce_log.txt"
            save_file(output_thoughtbounce_file, response.strip())    
            print('-------------------- 6 Recent Thoughts ------------------------')    
                          
 #       if i==7:
           # output_telegram_file = f"output/telegram/telegram_summary.txt"  
           # save_file(output_telegram_file, response.strip())
            print('-------------------- 7 Telegram Chat ------------------------')
  #      if i==8:
           # output_telegram_chat_file = f"output/telegram/telegram_summary_chat.txt"
          #  save_file(output_telegram_chat_file, response.strip())                        
                                        
    # Save the report in the output folder with the same name as the PDF file but with .txt extension
    save_file(output_file, report.strip())  # save the report to the specified output file
