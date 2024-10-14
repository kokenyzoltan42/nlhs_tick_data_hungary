import os
import gdown


class GoogleDataDownloader:
    def __init__(self, file_url, file_name):
        self.data_folder = "data"
        self.file_path = os.path.join(self.data_folder, file_name)
        self.download(file_url=file_url)

    def download(self, file_url):
        os.makedirs(self.data_folder, exist_ok=True)
        if not os.path.isfile(self.file_path):
            gdown.download(url=file_url, output=self.file_path,
                           fuzzy=True)
