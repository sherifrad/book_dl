#!/home/sherif/miniconda3/bin/python


#To Do: restore failed downloaded file (wget)
#To Do: if searched by a previous searched  query flash a message to view the old search result.

import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import json
import wget
from termcolor import cprint, colored 
from collections import OrderedDict

headers = {'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}

#===========================def func======================================================

#Coloring some text
def colorify_output(text, text2 = None,COLOR = None, on_COLOR = None):
    output_text = colored('%s'%text,'%s'%COLOR,'%s'%on_COLOR,attrs =[] )
    
    return output_text


#The main function 
def main():

    try:
        book_title = getBookTitle()
        result = search(book_title)
        if result:
            print_result(result)
            download(result)
    except KeyboardInterrupt:
        print('\n')
        print(colorify_output('Bye Bye',COLOR = 'red', on_COLOR = 'on_grey'),'\n')

#check the input
def getBookTitle():
    book_title = ""
    while len(book_title) < 3:
        book_title = input('Please Enter the book title (not less than 3 characters) ==> ')
    return book_title
        

#Get Ids values from the table
def search(book_title):
    value = {'req':book_title}
    qstring = urllib.parse.urlencode(value)

    url = "http://libgen.io/search.php?%s&open=0&res=100&view=simple&phrase=1&column=def" % qstring

    req = urllib.request.Request(url,headers=headers)
    resp = urllib.request.urlopen(req)
    resp_data = resp.read()

    soup = BeautifulSoup(resp_data,"lxml")
    table = soup.find('table',{'class':'c'})
    trs = table.find_all('tr')[1:]
    rows = [tr.find_all('td') for tr in trs]
    ids = [row[0].text for row in rows]
    if not ids:
        print("Book not found")
        try_agian = input('> Do you want to try again?[Y | N] > ')
        if try_agian in 'yY':
            getBookTitle()
            search(book_title)
        else:
            return
    # url = 'http://libgen.io/json.php?ids=%s&fields=Title,Author,MD5,edition,id,year,filesize'%(",".join(ids))
    
    url = 'http://libgen.io/json.php?ids=%s&fields=Title,Author,MD5,edition,id,year,filesize,extension'%(",".join(ids))

    # req = requests.get(url)
    req = urllib.request.Request(url)
    req = urllib.request.urlopen(req)
    req = req.read().decode('utf-8')
    json_resp = json.loads(req)
    return json_resp


#Get detailed book view : Book title,author,id, md5 and edition     
def print_result(result):
            count_id = 0

            for book in result:
                #To Do: filesize in Mb 
                
                book['filesize'] = str(round(int(book['filesize'])/(1024*1024),1)) + ' Mb'
                book['serial_No'] = str(count_id)

                # Dictionary with ordered keys
                main_dict = OrderedDict()
                main_dict['Title'] = book['title']
                main_dict['Author'] = book['author']
                main_dict['edition'] = book['edition']
                main_dict['Extension'] = book['extension']
                main_dict['filesize'] = book['filesize']
                main_dict['year'] = book['year']
                main_dict['id'] = book['id']
                main_dict['MD5'] = book['md5']
                main_dict['serial_No'] = str(count_id)

                print('-----***------')        
                print(colorify_output(count_id, COLOR='yellow', on_COLOR = 'on_grey'))
                print('-----***------')
                for key, value in main_dict.items():
                    key = colored(key, 'red', 'on_grey', ['bold','underline'])
                    # value = colorify_output(value, COLOR ='red', on_COLOR ='on_white')
                    if key == 'md5' or key == 'serial_No':
                        pass
                    else:    
                        print(key, value, sep="\t\t")
                count_id += 1


def download(json_resp):
    """

Downloading the file


    """
    print('==================================================')          
    id = input('Please write the ID of the desired Book ==> ')
    for book in json_resp:

        if id == book["serial_No"]:            
            print('You chose the following Book ==> %s'% book['title'])
            print('Please wait,we are downloading your Book...')
            url = 'http://libgen.io/get.php?md5=%s'%(book['md5'])
            req = urllib.request.Request(url,headers=headers)
            resp = urllib.request.urlopen(req)
            resp_data = resp.read()
            soup = BeautifulSoup(resp_data,"lxml")
            for item in soup.find_all('a'):
                if 'http' in str(item.get('href')):
                    link = item.get('href')
                    print("That's your link: %s"%link)
                    wget.download(link)
                    print('\n') 

if __name__ == "__main__":

    main()
