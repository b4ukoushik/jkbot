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
    - Then traverse through it for words like intelneeded
    - Then search intel spreadsheet and then displays latest one.
    """
    #Static Variables
    accessToken = 'cEwWJrcBEP9Slai4Ua4dUbZHRdjdOaJBB2xpWyeE'
    spreadsheet_key = '0AnVgNUkwYakUdC01QUxQdHUxcGVIODJ4YnVqY2RoLVE'

    if len(sys.argv) < 3:
        print '2 argumenst needed. intel-gm.py group_id and bot_id'
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

    print 'variable update starts'
    #Opening same JSON file
    transcriptFile = open(json_file)
    transcript = json.load(transcriptFile)
    transcriptFile.close()

    # Create a client class which will make HTTP requests with Google Docs server.
    client = gdata.spreadsheet.service.SpreadsheetsService()
    # Authenticate using your Google Docs email address and password.
    email='gameroy007@gmail.com'
    passwrd = 'li@gm1981;'
    last_id_file='last_id'+group
    intel_data ='NA'

   # All spreadsheets have worksheets. I think worksheet #1 by default always has a value of 'od6'
    worksheet_id = 'od6'
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = email
    client.password = passwrd
    client.source = 'Example Spreadsheet Writing Application'
    client.ProgrammaticLogin()
    gc = gspread.login(email,passwrd)
    sht1 = gc.open_by_key(spreadsheet_key)
    worksheet_old=sht1.worksheet("Black_Market")
    worksheet=sht1.worksheet("Downtown_Domination")

    print 'starting main FOR loop'
    for message in transcript:
      if last_id != message[u'id']:
        name = message[u'name']
        id = message[u'user_id']
        txt = message[u'text'].encode('utf-8','ignore')
        timepart= datetime.datetime.fromtimestamp(message[u'created_at']).strftime('%Y-%m-%d %H:%M')
        # Intel Needed loop. Command : INTEL NEEDED Synd_Name 
        txt2 = txt[0:13]
        if txt2.upper() =='INTEL NEEDED ':
            print (txt)
            syndname=txt[13:]
            print syndname
            # This block will try to find entry in sreadsheet. If find one it will push it to GM else look into history
            cell_list = worksheet.findall(syndname)
            cell_list=sorted(cell_list,reverse=True)
            for cell in cell_list:
                if cell.row>0 and cell.col !=4 :
                     intel_data = worksheet.cell(cell.row,3).value
                     print 'inside try-for'
                     print cell.value
                     intel_data = '***LIVE Intel***'+syndname +'\n' + intel_data
                     break
            if intel_data =='NA' :
                intel_data = 'LIVE Intel not available or Synd Name '+ syndname +' was typed wrong. Please check and try again. Else type "OLD INTEL NEEDED <exact synd name>" to get old intel.'
                
            print intel_data
            msg = intel_data  
            url=url_default + msg
            r = requests.post(url ,headers=headers)    

        #This is to gather old intel.
        txt3 = txt[0:17]        
        if txt3.upper() =='OLD INTEL NEEDED ':
            syndname=txt[17:]
            cell_list = worksheet_old.findall(syndname)
            cell_list=sorted(cell_list,reverse=True)
            for cell in cell_list:
                if cell.row>0 and cell.col !=4 :
                    intel_data = worksheet_old.cell(cell.row,3).value
                    intel_data = '***LAST WARs Intel***'+ syndname +'\n' + intel_data
                    print cell.row
                    break

            if intel_data =='NA' :
                intel_data='Old Intel is not available for ' + syndname
            print intel_data
            msg = intel_data  # This is to push consolidated intel
            url=url_default + msg
            r = requests.post(url ,headers=headers)

        #This is help sectoin
        txt3 = txt[0:4]
        if txt3.upper()=='HELP':
            message='This facility provides intels as requested.'+'\n'+'Mandatory - Add synd tag to GM name. Type -'+'\n'+ '"intel needed <exact synd name>" - to search for intel.'+'\n'+'"OLD intel needed <exact synd name> if you want old intel'+'\n'+ '"help" for this help. For real help PM K007.'
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
                                                   


