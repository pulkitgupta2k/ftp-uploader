import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import shutil
import os
import json
import ftplib
from pprint import pprint
import glob
from creds import *

def get_links():
    with open("links.json") as f:
        links = json.load(f)
    return links

def ftp_upload(ftp, sheet):
    ftp.cwd('/www/agrifoods/')

    sheet = f"{sheet}.zip"
    data = open(f"zips/{sheet}", 'rb')
    ftp.storbinary(f"STOR {sheet}", data)
    data.close()
    print("uploaded")

def get_gsheets():
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
    client = gspread.authorize(creds)
    spreadsheets = client.openall()
    for i, spreadsheet in enumerate(spreadsheets):
        spreadsheets[i] = spreadsheet.title
    return spreadsheets


def download_gsheet(url):
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name, scope)
    client = gspread.authorize(creds)
    # spreadsheet = client.open(sheet)
    spreadsheet = client.open_by_url(url)
    sheet = spreadsheet.title
    print(sheet)
    try:
        os.makedirs('downloads/{}'.format(sheet))
    except:
        pass

    flag = 0
    titles = []
    for worksheet in spreadsheet.worksheets():
        titles.append(worksheet.title)
        try:
            export_data = worksheet.get_all_values()
            try:
                with open("downloads/{}/{}.csv".format(sheet, worksheet.title), "r", encoding='utf8', newline="") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if not rows == export_data:
                    flag = 1
            except Exception as e:
                print(e)
                pass
            with open("downloads/{}/{}.csv".format(sheet, worksheet.title), "w", encoding='utf8', newline="") as f:
                writer = csv.writer(f)
                writer.writerows(export_data)
        except Exception as e:
            print(e)
            pass
    
    for filename in os.listdir(f"downloads/{sheet}/"):
        if filename[:-4] not in titles:
            os.remove(f"downloads/{sheet}/{filename}")
            flag = 1

    shutil.make_archive("zips/{}".format(sheet), 'zip',
                        'downloads/{}'.format(sheet))

    return [flag, sheet]


def driver():
    links = get_links()
    ftp = ftplib.FTP(ftp_host)
    ftp.login(username, password)
    for link in links:
        ret = download_gsheet(link)
        if ret[0]:
            ftp_upload(ftp, ret[1])
    ftp.quit()