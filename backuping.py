import zipfile
import os

i = 0

def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

def backup():
    global i
    folder_to_zip = '/home/thibault/delivery/INN/LemanNS/Regions'
    zip_file_path = f'/home/thibault/delivery/INN/LemanNS/backup[{i}].zip'

    zip_folder(folder_to_zip, zip_file_path)
    i += 1
