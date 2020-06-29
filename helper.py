import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import shutil
import os
import json

def get_links():
    with open("links.json") as f:
        links = json.load(f)
    return links

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
    try:
        os.makedirs('downloads/{}'.format(sheet))
    except:
        shutil.rmtree('downloads/{}'.format(sheet))
        os.makedirs('downloads/{}'.format(sheet))
    print(sheet)

    for worksheet in spreadsheet.worksheets():
        try:
            export_data = worksheet.get_all_values()
            with open("downloads/{}/{}.csv".format(sheet, worksheet.title), "w", encoding='utf8', newline="") as f:
                writer = csv.writer(f)
                writer.writerows(export_data)
        except Exception as e:
            print(e)
            pass
    shutil.make_archive("zips/{}".format(sheet), 'zip',
                        'downloads/{}'.format(sheet))


def driver():
    links = get_links()
    for link in links:
        download_gsheet(link)