import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.file import Storage
from oauth2client import client
from oauth2client import tools
import io
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from datetime import datetime, timedelta, timezone
import subprocess
import shutil



SCOPES = ['https://www.googleapis.com/auth/drive']

class Drive:
    def __init__(self,image_path,spreadsheet_path):
        self.creds = None
        self.authenticate()
        self.reciept_ids = []
        self.image_path = image_path
        self.spreadsheet_path = spreadsheet_path

    # Authenticate the user
    def authenticate(self):
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        credential_path = os.path.join('C:/credentials', 'token.json')
        store = Storage(credential_path)
        self.creds = store.get()

        if not self.creds or self.creds.invalid:
            print("not valiiiiiiiiiid")
            flow = client.flow_from_clientsecrets('C:/credentials/credentials.json', SCOPES)
            self.creds = tools.run_flow(flow, store)
            return self.creds

    # List files in Google Drive
    def get_folders(self, folder_name=None):
        try:
            service = build("drive", "v3", credentials=self.creds)

            # Define the query to search for folders
            query = "mimeType='application/vnd.google-apps.folder'"
            if folder_name:
                query += f" and name='{folder_name}'"


            # Call the Drive v3 API
            results = (
                service.files()
                .list(q=query, pageSize=10, fields="nextPageToken, files(id, name)")
                .execute()
            )

            items = results.get("files", [])

            if not items:
                print("No folders found.")
                return

            return items

        except HttpError as error:
            # Handle errors from drive API.
            print(f"An error occurred: {error}")

    def download_image(self, file_id, save_path):
        """
        Downloads an image file from Google Drive.

        Args:
            file_id (str): The ID of the image file to download.
            save_path (str): The local path where the image will be saved.

        Returns:
            bool: True if the file is downloaded successfully, False otherwise.
        """
        try:
            # Create Drive API client
            service = build("drive", "v3", credentials=self.creds)

            # Request the file
            request = service.files().get_media(fileId=file_id)
            file_stream = io.BytesIO()
            downloader = MediaIoBaseDownload(file_stream, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%")

            # Write the file to the specified path
            with open(save_path, "wb") as image_file:
                image_file.write(file_stream.getvalue())

            print(f"Image successfully downloaded to: {save_path}")
            return True

        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def get_files_in_folder(self, folder_id, mime_type=None, modified_time=None):
        try:
            service = build("drive", "v3", credentials=self.creds)

            # Define the query to search for files in the folder
            query = f"'{folder_id}' in parents"
            if mime_type:
                query += f" and mimeType='{mime_type}'"

            if modified_time:
                query += f" and modifiedTime > '{modified_time}'"
            # Call the Drive v3 API
            results = (
                service.files()
                .list(q=query, pageSize=100, fields="nextPageToken, files(id, name, mimeType)")
                .execute()
            )

            items = results.get("files", [])

            if not items:
                print("No files found in the folder.")
                return []

            return items

        except HttpError as error:
            # Handle errors from Drive API
            print(f"An error occurred: {error}")
            return []


    def get_new_reciept(self, time_delay):

        folder = drive_api.get_folders("automatic_grocerie_list")
        files = drive_api.get_files_in_folder(folder[0]['id'])
        time_diff = (datetime.now(timezone.utc) - timedelta(hours=time_delay)).isoformat()  # Add 'Z' for UTC timezone
        for file in files:
            if file['name'] == 'kvitton':
                images = drive_api.get_files_in_folder(file['id'],mime_type='image/png',modified_time=time_diff)
                print(f"found {len(images)} new reciepts")
                for image in images:
                    self.reciept_ids.append(image['id'])
        if not os.path.exists(self.image_path):
            os.mkdir(self.image_path)
        for i, _ in enumerate(drive_api.reciept_ids):
            drive_api.download_image(drive_api.reciept_ids[i], f"{self.image_path}/{i}.png")

    def download_google_sheet_as_xlsx(self, sheet_id, save_path):
        """
        Downloads a Google Sheets file and saves it as an .xlsx file.

        Args:
            sheet_id (str): ID of the Google Sheets file.
            save_path (str): Local path to save the .xlsx file.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            service = build("drive", "v3", credentials=self.creds)

            # Request the file as .xlsx format
            request = service.files().export_media(
                fileId=sheet_id, mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            with open(save_path, "wb") as file:
                file.write(request.execute())

            print(f"Google Sheet downloaded as .xlsx: {save_path}")
            return True

        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def upload_xlsx_as_google_sheet(self, file_path, folder_id=None):
        """
        Uploads an .xlsx file to Google Drive and converts it to a Google Sheets file.

        Args:
            file_path (str): Path to the .xlsx file.
            folder_id (str, optional): ID of the folder to upload to.

        Returns:
            str: ID of the uploaded Google Sheet.
        """
        try:
            print("Uploading file to Google Drive...")
            service = build("drive", "v3", credentials=self.creds)
            file_metadata = {
                "name": os.path.basename(file_path),
                "mimeType": "application/vnd.google-apps.spreadsheet"
            }
            if folder_id:
                file_metadata["parents"] = [folder_id]

            # Upload the file
            media = MediaFileUpload(file_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
            print(f"File uploaded successfully: {file.get('name')}")
            return file.get("id")

        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def get_excel_file(self):
        automatic_grocerie_list = drive_api.get_folders("automatic_grocerie_list")
        files = drive_api.get_files_in_folder(folder_id=automatic_grocerie_list[0]['id'])
        print(files)
        for file in files:
            if file['name'] == 'main_food_list':
                file_id = file['id']
                drive_api.download_google_sheet_as_xlsx(file_id, self.spreadsheet_path)
                break

    def dump_excel(self):
        automatic_grocerie_list = drive_api.get_folders("automatic_grocerie_list")
        files = drive_api.get_files_in_folder(folder_id=automatic_grocerie_list[0]['id'])
        for file in files:
            if file['name'] == 'main_food_list':
                file_id = file['id']
                drive_api.delete_file(file_id)
        drive_api.upload_xlsx_as_google_sheet(self.spreadsheet_path, automatic_grocerie_list[0]['id'])

    def delete_file(self, file_id):
        """
        Deletes a file on Google Drive.

        Args:
            file_id (str): The ID of the file to delete.

        Returns:
            bool: True if the file is deleted successfully, False otherwise.
        """
        try:
            service = build("drive", "v3", credentials=self.creds)
            service.files().delete(fileId=file_id).execute()
            print(f"File {file_id} deleted successfully.")
            return True

        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

if __name__ == '__main__':
    image_path = 'tmp/kvitton'
    spreadsheet_path = 'tmp/main_food_list.xlsx'

    if not os.path.exists('tmp'):
        os.mkdir('tmp')
    drive_api = Drive(image_path=image_path,spreadsheet_path=spreadsheet_path)
    drive_api.get_new_reciept(time_delay=24)
    drive_api.get_excel_file()
    subprocess.run(['python', 'create_list.py', '--image_path', image_path, '--spreadsheet_path', spreadsheet_path])
    drive_api.dump_excel()
    shutil.rmtree("tmp")



