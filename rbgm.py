# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import gdata.spreadsheet.service
import time
import requests
import json
import datetime
import string
import gspread
import subprocess

def main():
    """Usage: rbgm.py filename.json

Assumes filename.json is a JSON GroupMe transcript.
    """
    # This is to call main script that brings all data into a JSON file https://groupme.com/join_group/8624579/NeuHP2
    #os.remove("transcript-8636748.json")
    #os.system("groupme-fetch.py 8636748 cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE")  # This is to get complete file
    #This is to get incremental file
    file = open('last_id',"r")
    last_id = file.read()
    file.close()
    cmd="python groupme-fetch-inc.py 8636748 cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE newest "+last_id
    os.system(cmd)

    group = '8636748'
    accessToken='cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE'
    headers = {
        'Accept': 'application/json, text/javascript',
        'Accept-Charset': 'ISO-8859-1,utf-8',
        'Accept-Language': 'en-US',
        'Content-Type': 'application/text',
        'Origin': 'https://web.groupme.com',
        'Referer': 'https://web.groupme.com/groups/'+group,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.45 Safari/537.22',
        'X-Access-Token': accessToken
    }
    url_default= 'https://api.groupme.com/v3/bots/post?bot_id=3ff09702257aae1dd3d1e523de&text=' #Add your text here
    #r = requests.post(url ,headers=headers)
    
    #Opening same JSON file
    transcriptFile = open("transcript-8636748.json")
    transcript = json.load(transcriptFile)
    transcriptFile.close()
    
    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.spreadsheet.service.SpreadsheetsService()
    # Authenticate using your Google Docs email address and password.
    email='gameroy007@gmail.com'
    passwrd = 'li@gm1981;'

    spreadsheet_key = '1WOzIOrL_bIBNB7DS7jTDoRxHrbyIgGLCltjrjJ186fA'
    # All spreadsheets have worksheets. I think worksheet #1 by default always has a value of 'od6'
    worksheet_id = 'od6'
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = email
    client.password = passwrd
    client.source = 'Example Spreadsheet Writing Application'
    client.ProgrammaticLogin()
    gc = gspread.login(email,passwrd)
    sht1 = gc.open_by_key(spreadsheet_key)
    worksheet=sht1.worksheet("jumpers")

    for message in transcript:
      if last_id != message[u'id']:
        name = message[u'name']
        id = message[u'user_id']
        txt = message[u'text'].encode('utf-8')
        timepart= datetime.datetime.fromtimestamp(message[u'created_at']).strftime('%Y-%m-%d %H:%M')
        txt2 = txt[0:4]   
        if txt2 =='Here' or txt2 =='here' or txt2 =='Away' or txt2 =='away':
            print (txt)
            dict = {}
            dict['timestamp'] = timepart
            dict['jumpercodeandlvl'] = txt
            dict['groupmename'] = name
            dict['id'] = id
            dict['others'] = txt2.upper()
          # print dict
            try :  # This block will try to find entry in sreadsheet. If find one it will update it else insert a new entry
                cell = worksheet.find(id)
                if cell.row >0:
                  worksheet.update_cell(cell.row, 2, txt)
                  worksheet.update_cell(cell.row, 1, timepart)
                  worksheet.update_cell(cell.row, 5, txt2.upper())
                  status = "Status of "+name+ " updated to "+txt2   # This is to show status change or current status
                  url=url_default+status   
                  r = requests.post(url ,headers=headers)
                  

            except :
                entry = client.InsertRow(dict,spreadsheet_key,worksheet_id)
                status = "Status of "+name+ " entered as "+txt2  # This is to show new guy entered in room
                url=url_default+status 
                r = requests.post(url ,headers=headers)                
        txt3 = txt[0:9]
        stringlist="List of Available Jumpers "+'\n'
        if txt3 =='Available' or txt3 =='available': 
           try :
               cell_list = worksheet.findall('HERE')
               for  cell in cell_list:
                    val = worksheet.cell(cell.row,3).value
                    stringlist=stringlist+val +'\n'
               url=url_default+stringlist   
               r = requests.post(url ,headers=headers)
               print r.status_code
           except :
               url=url_default + "No One is Available"    
               r = requests.post(url ,headers=headers)
        #This is help sectoin
        txt3 = txt[0:4]
        if txt3.upper()=='HELP':
            message='This is a response form  bot. Please type "here" to announce you are available to jump.'+'\n'+ 'Please type "away" to announce you will be unavailable to jump'+'\n'+ 'Please type "available" to see how many jumpers will be unavailable to jump'+'\n'+'Type "help" for this help. For real help PM K007'
            url=url_default +message
            r = requests.post(url ,headers=headers)   
    #Keeping last id into a file
    transcript = sorted(transcript, key=lambda k: k[u'created_at'])
    last_id = transcript[-1][u'id']
    file = open('last_id',"w")
    file.write(last_id)
    file.close()
    
    #Keeping a backup of whole processed file
    transcriptFile = open("transcript-8636748-backup.json", 'w')
    json.dump(transcript, transcriptFile, ensure_ascii=False)
    transcriptFile.close()

    #Keeping last record into the main file
    file = open('transcript-8636748.json',"w")
    file.write('[')
    file.close()
    transcript = sorted(transcript, key=lambda k: k[u'created_at'])
    transcript = transcript[-1]
    transcriptFile = open("transcript-8636748.json", 'a')
    json.dump(transcript, transcriptFile, ensure_ascii=False)
    transcriptFile.close()
    file = open('transcript-8636748.json',"a")
    file.write(']')
    file.close()


if __name__ == '__main__':
    main()
    sys.exit(0)
