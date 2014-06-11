# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import subprocess
import datetime
import string

import requests
import json
import gspread
import gdata.spreadsheet.service

def main():
    """Usage: raidboss-gm.py group_id bot_id

    - Firstly downloads file as transcript-droupid.json.
    - Then traverse through it for words like here, away, available and help. And groupme push accordingly.
    - Create a file to keep backup of processed jason file and last record of chat room.
    - Allowed inputs help - Posts help about this bot facility. here & away- status update of a jumper. available gives everyone available.
    """
    #Static Variables
    accessToken = 'cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE'
    spreadsheet_key = '1WOzIOrL_bIBNB7DS7jTDoRxHrbyIgGLCltjrjJ186fA'

    if len(sys.argv) < 3:
        print '2 argumenst needed. raidboss-gm.py group_id and bot_id'
        sys.exit(0)
    #Dynamic varaiables
    group = sys.argv[1]
    bot_id=sys.argv[2]
    json_file='transcript-'+group+'.json'
    last_id_file='last_id'+group
    
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
    url_default= 'https://api.groupme.com/v3/bots/post?bot_id='+bot_id+'&text=' #Add your text here
    
    #r = requests.post(url ,headers=headers)
    #This is to call main script that brings all data into a JSON file https://groupme.com/join_group/8624579/NeuHP2
    #os.remove("transcript-8636748.json")
    #os.system("groupme-fetch.py 8636748 cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE")  # This is to get complete file

    try :
        file = open(last_id_file,"r")
        last_id = file.read()
        file.close()
        cmd="python groupme-fetch.py "+group +" "+ accessToken +" newest "+last_id #This is to get incremental file
        os.system(cmd)
    except IOError:
        cmd="python groupme-fetch.py "+group +" "+ accessToken #This is to get complete file
        os.system(cmd)
        last_id = 1

    print 'variable update loop'
    #Opening same JSON file
    transcriptFile = open(json_file)
    transcript = json.load(transcriptFile)
    transcriptFile.close()
    
    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.spreadsheet.service.SpreadsheetsService()
    # Authenticate using your Google Docs email address and password.
    email='gameroy007@gmail.com'
    passwrd = 'li@gm1981;'

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

    print 'starting main FOR loop'
    for message in transcript:
      if last_id != message[u'id']:
        name = message[u'name']
        id = message[u'user_id']
        txt = message[u'text'].encode('utf-8')
        timepart= datetime.datetime.fromtimestamp(message[u'created_at']).strftime('%Y-%m-%d %H:%M')
        txt2 = txt[0:4]   
        if txt2.upper() =='HERE' or txt2.upper() =='AWAY':
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
                  print 'inside update loop'

            except :
                entry = client.InsertRow(dict,spreadsheet_key,worksheet_id)
                status = "Status of "+name+ " entered as "+txt2  # This is to show new guy entered in room
                url=url_default+status 
                r = requests.post(url ,headers=headers)
                print 'inside insert loop'
        txt3 = txt[0:9]
        stringlist="List of Available Jumpers "+'\n'
        if txt3.upper() =='AVAILABLE': 
           try :
               cell_list = worksheet.findall('HERE')
               cell_list=sorted(cell_list,reverse=True)
               for  cell in cell_list:
                    val = worksheet.cell(cell.row,3).value
                    stringlist=stringlist+val +'\n'
               print 'inside available loop' 
               print len(stringlist)     

               # This is to handle GM message more than 450 character. Need better way to do this
               str1=stringlist[0:440]
               str2=stringlist[441:880]
               str3=stringlist[881:1320]
               str4=stringlist[1321:1761]
               str5=stringlist[1762:2201]  
               """print 'str1'+ str1
               print 'str2'+ str2
               print 'str3'+ str3
               print 'str4'+ str4
               print 'str5'+ str5 """
               if str1:
                   url=url_default+str1
                   r = requests.post(url ,headers=headers)
               if str2:
                   url=url_default+str2
                   r = requests.post(url ,headers=headers)
               if str3:
                   url=url_default+str3
                   r = requests.post(url ,headers=headers)
               if str4:
                   url=url_default+str4
                   r = requests.post(url ,headers=headers)
               if str5:
                   url=url_default+str5
                   r = requests.post(url ,headers=headers)
                # This is to handle GM message more than 450 character complete

           except :
               url=url_default + "No One is Available"    
               r = requests.post(url ,headers=headers)
               
        #This is help sectoin
        txt3 = txt[0:4]
        if txt3.upper()=='HELP':
            message='This facility tracks jumpers and their status.'+'\n'+'Mandatory - Add mafia code of jumper(s) to GM name.'+'\n'+ 'Type "here" to announce you are available to jump.'+'\n'+ 'Type "away" to announce you will be unavailable to jump'+'\n'+ 'Type "available" to see how many jumpers are available to jump.'+'\n'+'Type "help" for this help. For real help PM K007.'
            url=url_default + message
            r = requests.post(url ,headers=headers)   
    #Keeping last id into a file
    transcript = sorted(transcript, key=lambda k: k[u'created_at'])
    last_id = transcript[-1][u'id']
    file = open(last_id_file,"w")
    file.write(last_id)
    file.close()
    
    #Keeping a backup of whole processed file
    json_file_bkp=json_file+'-backup'
    transcriptFile = open(json_file_bkp, 'w')
    json.dump(transcript, transcriptFile, ensure_ascii=False)
    transcriptFile.close()

    #Keeping last record into the main file
    file = open(json_file,"w")
    file.write('[')
    file.close()
    transcript = sorted(transcript, key=lambda k: k[u'created_at'])
    transcript = transcript[-1]
    transcriptFile = open(json_file, 'a')
    json.dump(transcript, transcriptFile, ensure_ascii=False)
    transcriptFile.close()
    file = open(json_file,"a")
    file.write(']')
    file.close()
    print 'End of program'

if __name__ == '__main__':
    main()
    sys.exit(0)
