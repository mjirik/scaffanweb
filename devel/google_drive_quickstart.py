# https://developers.google.com/drive/api/v3/quickstart/python
#
# conda install -c conda-forge google-api-python-client

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io
from pathlib import Path
from loguru import logger

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/drive.file']

def iterate_files(
        credentials_json='credentials_mjirik_gapps.json',
        token_pickle='token.pickle',
        drive_id="0AHtTDixl96VzUk9PVA",  # my Zeiss Scann ID
        dir_id='1OsKfZlp_s6RPHXXei8LsZunTNjPsBwMb',
        file_extension=None
        ):
    """

    :param credentials_json: path to credentials in json format. It can be obtained by activating Google API
    :param token_pickle: path to token in pickle. It can be created automatically interactively by first run.
    :param drive_id: Google Drive ID
    :param dir_id: Google Directory ID
    :return:
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    q = f"'{dir_id}' in parents"
    if file_extension:
        q += f" and fileExtension = '{file_extension}'"
    # Call the Drive v3 API
    results = service.files().list(
        driveId=drive_id,
        # q="name = '11_2019_11_13__-7.czi'",
        # q="mimeType = 'application/vnd.google-apps.folder'", # list all directories
        # q="'1pStkl9_vEQJHTAc0OIbP4X39GmcBhVBJ' in parents", # all files in Moulisova-Jena
        # q="'1OsKfZlp_s6RPHXXei8LsZunTNjPsBwMb' in parents", # all files in scaffan_import
        q=q, # all files in scaffan_import

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

        file_id = item["id"]
        name = item['name']
        drive_service = service
        request = drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug("Download %d%%." % int(status.progress() * 100))
        yield fh, name


def main():
    dfilespath = "download2"
    for fh, name in iterate_files():
        dfpath = Path(dfilespath)
        dfpath.mkdir(parents=True, exist_ok=True)
        opath = dfpath / name
        if opath.exists():
            logger.debug(f"File '{opath}' exists. Skipping download.")
        else:
            with io.open(opath, 'wb') as f:
                fh.seek(0)
                f.write(fh.read())


if __name__ == '__main__':
    main()