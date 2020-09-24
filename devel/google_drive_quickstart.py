# https://developers.google.com/drive/api/v3/quickstart/python
#
# conda install -c conda-forge google-api-python-client

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly']

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_mjirik_gapps.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    driveId = "0AHtTDixl96VzUk9PVA" # my Zeiss Scann ID
    # Call the Drive v3 API
    results = service.files().list(
        driveId=driveId,
        # q="name = '11_2019_11_13__-7.czi'",
        # q="mimeType = 'application/vnd.google-apps.folder'", # list all directories
        q="'1pStkl9_vEQJHTAc0OIbP4X39GmcBhVBJ' in parents", # all files in Moulisova-Jena
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        corpora="drive",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == '__main__':
    main()