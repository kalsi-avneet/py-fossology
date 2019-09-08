class Uploads():
    '''Class for interacting with uploads on the server'''

    def __init__(self):
        pass

    def get_all_uploads(self):   # -> [Upload]
        pass

    def new_upload(self):        # -> Upload
        pass



class Upload():
    '''Denotes a single upload'''

    def __init__(self, upload_id,
            folder_id=None,
            folder_name=None,
            description=None,
            upload_name=None,
            upload_date=None,
            filesize=None):

        self.upload_id = upload_id,
        self.folder_id = folder_id,
        self.folder_name = folder_name,
        self.description = description,
        self.upload_name = upload_name,
        self.upload_date = upload_date,
        self.filesize = filesize


    def delete(self, upload_id) -> bool:
        pass

    def move(self, upload_id, destination_folder_id) -> bool:
        pass

    def copy(self, upload_id, destination_folder_id) -> bool:
        pass
