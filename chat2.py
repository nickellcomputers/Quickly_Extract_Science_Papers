import os
from openai import OpenAI
from time import time, sleep
from halo import Halo
import textwrap
import sys
import yaml
from datetime import datetime
import webbrowser
import urllib.parse

# Use readline for better input() editing, if available
try:
  import readline
except ImportError:
  pass


###     file operations


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def save_list_to_file(file_path, content_list, mode='w'):
    with open(file_path, mode) as file:
        for item in content_list:
            file.write(f"{item}\n")

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)

def append_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)


def open_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


###     API functions gpt-4-0613
###     gpt-3.5-turbo-16k


def chatbot(conversation, model="gpt-4o", temperature=0):
    max_retry = 7
    retry = 0
    while True:
        try:
            spinner = Halo(text='AI', spinner='dots')
            spinner.start()
            
            response = client.chat.completions.create(model=model, 
            messages=conversation, 
            temperature=temperature)
            
            
                
            #text = response['choices'][0]['message']['content']
            text = response.choices[0].message.content
            spinner.stop()
            
            return text, response.usage.total_tokens

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


###     CHAT FUNCTIONS


def get_user_input():
    # get user input
    text = input('\n\n\nUSER:\n\n')
    
    # check if scratchpad updated, continue
    if 'DONE' in text:
        print('\n\n\nThank you for participating in this survey! Your results have been saved. Program will exit in 5 seconds.')
        
        #Get the summary of the conversation
        conversation_summary1 = compose_conversation(ALL_MESSAGES, text, system_message_summary)
        response1 = generate_chat_response(ALL_MESSAGES, conversation_summary1, model="gpt-4-0613")

        print('SUMMARY1:' + response1)
        #conversation_summary2 = compose_conversation(ALL_MESSAGES2, text, system_message_summary)
        #response2 = generate_chat_response(ALL_MESSAGES2, conversation_summary2)
        #print('SUMMARY2:' + response2)
        #conversation_summary3 = compose_conversation(ALL_MESSAGES3, text, system_message_summary)
        #response3 = generate_chat_response(ALL_MESSAGES3, conversation_summary3)
        #print('SUMMARY3:' + response3)
        
        #FULL SUMMARY
        #conversation_summary4 = compose_conversation(response1+response2+response3, text, system_message_summary)
        #response4 = generate_chat_response(response1+response2+response3, conversation_summary)
        
        
        save_file('chat_logs/chat_full_summary.txt', response1 + '\n')
        
        append_file('chat_logs/chat_full_summary_alltime.txt', 'Session ' + datetime.now().strftime('%m/%d/%Y %I:%M:%S %p') + ': ' + response1 + '\n')
        append_file('../Journal_Summarizer/input/chat_full_summary_alltime.txt', 'Session ' + datetime.now().strftime('%m/%d/%Y %I:%M:%S %p') + ': ' + response1 + '\n')

        
        sleep(5)
        exit(0)
    if text == '':
        # empty submission, probably on accident
        None
    else:
        return text


def compose_conversation(ALL_MESSAGES, text, system_message):
    # continue with composing conversation and response
    ALL_MESSAGES.append({'role': 'user', 'content': text})
    conversation = list()
    conversation += ALL_MESSAGES
    conversation.append({'role': 'system', 'content': system_message})
    return conversation

def compose_conversation2(ALL_MESSAGES2, text, system_message):
    # continue with composing conversation and response
    ALL_MESSAGES2.append({'role': 'user', 'content': text})
    conversation = list()
    conversation += ALL_MESSAGES2
    conversation.append({'role': 'system', 'content': system_message})
    return conversation

def compose_conversation3(ALL_MESSAGES3, text, system_message):
    # continue with composing conversation and response
    ALL_MESSAGES3.append({'role': 'user', 'content': text})
    conversation = list()
    conversation += ALL_MESSAGES3
    conversation.append({'role': 'system', 'content': system_message})
    return conversation
    
def generate_chat_response(ALL_MESSAGES, conversation, model="gpt-3.5-turbo-16k", temperature=0):
    # generate a response
    response, tokens = chatbot(conversation, model=model, temperature=temperature)

    if tokens > 7800:
        z = ALL_MESSAGES.pop(0)
        print(z)
        print("tokens: "+z)
    ALL_MESSAGES.append({'role': 'assistant', 'content': response})
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in response.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print('\n\n\nJOURNAL:\n\n%s' % formatted_text)
    return formatted_text

def draft_email(subject, num_account="1"):
    body = "This is the body"
    body = response
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    email_url = f"https://mail.google.com/mail/u/{num_account}/?fs=1&to=jeffnickell@gmail.com&su={subject}&body={body}&tf=cm"
    webbrowser.open(email_url)    

if __name__ == '__main__':
    # instantiate chatbot, variables
    #openai.api_key = open_file('key_openai.txt').strip()
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key is None:
        raise ValueError("OPENAI_API_KEY is not set")
    client = OpenAI()  # This will automatically pick up OPENAI_API_KEY from the envir    
    system_message = open_file("system.txt")
    system_coach = open_file("system_coach.txt")
    system_sched = open_file("system_sched.txt")                            #List the events from the Schedule List               
    system_message_summary = open_file('system_summary.txt')                #Summarizer between BOT and USER
    ALL_MESSAGES = list()
    ALL_MESSAGES2 = list() #just the current conversation message
    ALL_MESSAGES3 = list()
    user_messages = list()
    bot_response = list()
    both_rem = list()
    
    first_input = True  # flag to check if it's the first input

    while True:
        text = get_user_input()
        
        if not text:
            continue

        # Only replace <<OUT>> and <<USERINFO>> for the first user input
        if first_input:
            # open and read contents of conv_summary_current.txt
            latest_conv = open_file("D:\\Python\\program_focus\\Journal_Summarizer\\output\\conv_summary_current.txt")

            # replace <<OUT>> with latest_conv in system_message
            system_message = system_message.replace("<<OUT>>", latest_conv)

            # open and read contents of useroverview.txt
            user_info = open_file("D:\\Python\\program_focus\\Journal_Summarizer\\output\\useroverview.txt")

            # replace <<USERINFO>> with user_info in system_message
            system_message = system_message.replace("<<USERINFO>>", user_info)

            # open and read contents of thoughts_this_week.txt
            recent_thoughts = open_file('D:\\Python\\program_focus\\Journal_Summarizer\\output\\recent_thoughts\\thoughts_this_week.txt')
            
            
            # replace <<RECENTTHOUGHTS>> with recent_thoughts in system_message
            system_message = system_message.replace("<<RECENTTHOUGHTS>>", recent_thoughts)              
            
            #schedule list            
            schedule_list = open_file('goocal\\weekly_events.txt')
            # replace <<SCHEDULELIST>> with schedule_list in system_message
            
            def suffix(d):
                return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

            def custom_strftime(format, t):
                return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

            now = datetime.now()
            myweekday = custom_strftime('%A', now)
            
            todays_date = custom_strftime('%A, %B {S} %Y', now)


            system_sched = system_sched.replace("<<weekday>>", myweekday)
            system_sched = system_sched.replace("<<todaysdate>>", todays_date)
            

            system_sched = system_sched.replace("<<SCHEDULELIST>>", schedule_list)
              
            
            conversation3 = compose_conversation3(ALL_MESSAGES3, text, system_sched)                        #From the conversation text make a scheduled list
            response_agent3 = generate_chat_response(ALL_MESSAGES3, conversation3, temperature=1)            
            bot_response.append(response_agent3)
    

            first_input = False  # Reset flag to False after the first input

        
        if 'recent tasks' in text.lower():
            # replace <<RECENTTHOUGHTS>> with recent_thoughts in system_message
            system_message = system_message.replace("<<RECENTTHOUGHTS>>", recent_thoughts)  
            conversation = compose_conversation(ALL_MESSAGES, text, system_message)
        else:
            conversation = compose_conversation(ALL_MESSAGES, text, system_message)    
        
        
        user_messages.append(conversation)
        save_file('chat_logs/chat_%s_user.txt' % time(), text + '\n')
                
        response = generate_chat_response(ALL_MESSAGES, conversation)
        
        #skip the COACH for now
        #conversation2 = compose_conversation2(ALL_MESSAGES2, text, system_coach)  
        #response_agent2 = generate_chat_response(ALL_MESSAGES2, conversation2, temperature=1)




        
        bot_response.append(response)
        #bot_response.append(response_agent2)

        save_file('chat_logs/chat_%s_bot.txt' % time(), response + '\n')
        save_list_to_file('conversation.txt', conversation,'a')
        append_file('chat_logs/chat_both.txt', 'User: ' + text + '\n')
        append_file('chat_logs/chat_both.txt', 'Bot: ' + response + '\n')
        
        
        if 'draft email ct' in text.lower():
            draft_email('testsubject','1') 




