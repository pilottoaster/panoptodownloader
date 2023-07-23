import sqlite3
import os
import requests
from tqdm.auto import tqdm
import re

con = sqlite3.connect('panopto.db')
cur = con.cursor()


def is_file_downloaded(url):
    cur.execute("SELECT downloaded FROM videos WHERE url=?", (url,))
    result = cur.fetchone()
    return result and result[0]  # Return True if the file has already been downloaded


def set_file_downloaded(url, downloaded=True):
    cur.execute("UPDATE videos SET downloaded = ? WHERE url = ?", (downloaded, url))
    con.commit()


def get_unique_filename(directory, filename, extension):
    # Replace invalid characters in filename with "-"
    sanitized_filename = re.sub(r'[<>:"/\\|?*]', '-', filename)

    counter = 1
    while os.path.exists(os.path.join(directory, sanitized_filename + f"_{counter}" + extension)):
        counter += 1
    return sanitized_filename + f"_{counter}"


def download_file(name, url):
    if not is_file_downloaded(url):
        dir_dl = "D:\\panoptovideos"
        if not os.path.isdir(dir_dl):
            os.makedirs(dir_dl)

        original_filename = name
        name = get_unique_filename(dir_dl, name, '.mp4')
        filepath = os.path.join(dir_dl, name + '.mp4')
        r = requests.get(url, stream=True)
        try:
            total_size = int(r.headers['Content-Length'])
            with open(filepath, 'wb') as f:
                pbar = tqdm(unit="B", total=total_size, unit_scale=True, unit_divisor=1000, colour='green')
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:  # filters out the keep-alive new chunks
                        f.write(chunk)
                        pbar.update(len(chunk))
                pbar.close()
        except Exception as e:
            print(f'Error occurred while downloading {name}: {e}')
            set_file_downloaded(url, downloaded=False)  # Mark the file as not downloaded in the database
            return

        print(f'Download of {name} complete.')
        set_file_downloaded(url)  # Mark the file as downloaded in the database
    else:
        print(f'{name} is already downloaded. Skipping download.')
