import openai
import time
import os


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
           
        return infile.read().strip()

def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def summarize_file(textfilepath,destination_dir):
    total_word_count=0
    openai.api_key = open_file('key_openai.txt')
    no_words=0
    chunk=""
    cnt=0
    print("This might take some time please wait")
    stime=time.time()
    filename="key-points_"+os.path.splitext(os.path.split(textfilepath)[1])[0]+".txt"
    os.chdir(destination_dir)
    with open(textfilepath, 'r') as file:
        text=file.read()
        text_list=text.split(" ")
        s=0
        e=len(text_list)
        while(s<e):
          #4000
            if(no_words+len(text_list[s])<=8000): 
                total_word_count+=len(text_list[s])
                no_words+=len(text_list[s])
                chunk+=text_list[s]+" "
                cnt+=1
            else:
                try:
                    completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo-16k",  messages=[{"role": "user", "content": f"Give key points for '{chunk}'"}] )
                    summary=completion["choices"][0]["message"]["content"]
                except Exception as ex:
                    time.sleep(21)
                    s-=1
                else:
                    with  open(filename,'a+',encoding='utf-8') as file:
                        file.write(f"Word {s-cnt} - {s-1}")
                        file.write("\n")
                        file.write(summary)
                        file.write("\n")
                    print(f"Summarizing key points for words {s-cnt} - {s-1}")
                    s-=1
                    no_words=0
                    chunk=""
                    cnt=0
            s+=1
    if(chunk!=""):
        completion = openai.ChatCompletion.create(model = "gpt-3.5-turbo-16k",  messages=[{"role": "user", "content": f"Give key points for '{chunk}'"}] )
        data=completion["choices"][0]["message"]["content"]
        with  open(filename,'a+',encoding='utf-8') as file:
                file.write(f"Word {s-cnt} - {e}")
                file.write("\n")
                file.write(data)
                file.write("\n")
    print(f"Total word count: {total_word_count}\nKey Points:\n{data}")
    etime=time.time()
    return etime-stime


if __name__=="__main__":
    print("----SUMMARIZE Text Files TO KEYPOINTS---")
    filepath=r'{}'.format(input("Enter path to text file: "))
    des_dir=r'{}'.format(input("Enter destination directory to save summary: "))
    timetake=summarize_file(filepath,des_dir)
    print(f"Time taken to summarize: {timetake}sec\nKey points saved at {des_dir}")

