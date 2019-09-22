import json
from requests import Session


from fossology.common import _util
from fossology.exceptions import FossologyError,\
        FossologyInvalidCredentialsError

class Connection():
    def __init__(self):
        self.session = Session()
        self.headers = self.session.headers

    def delete(self, args, **kwargs):
        return self.session.delete(args, **kwargs)

    def get(self, args, **kwargs):
        return self.session.get(args, **kwargs)

    def patch(self, args, **kwargs):
        return self.session.patch(args, **kwargs)

    def post(self, args, **kwargs):
        return self.session.post(args, **kwargs)

    def put(self, args, **kwargs):
        return self.session.put(args, **kwargs)


    def close_connection(self):
        self.session.close()

class Fossology():
    def __init__(self, server):

        self.util = _util()

        # Remove trailing slashes from servername
        if server.endswith('/'):
            server = server[:-1]

        self.server = server
        self.api_server = self.util._join_url(self.server, 'api/v1')

        # setup connection
        self.connection = Connection()

        # Add common headers to the connection
        self.connection.headers.update({
            'accept': 'application/json'
            })

        # (TODO): Setup logger if requested

    def __del__(self):

        # close the connection
        self.connection.close_connection()


    def generate_auth_token(self, username, password, expire, scope='read'):
        '''Requests a new token from the fossology server'''

        auth_endpoint = 'tokens'
        endpoint = self.util._join_url(self.api_server, auth_endpoint)

        headers = {'Content-Type': 'application/json'}

        payload = json.dumps({"username": username,
             'password': password,
             'token_name': self.util._generate_unique_name(),
             'token_scope': scope,
             'token_expire': expire
             })


        # request a token from the server
        server_response = self.connection.post(endpoint, headers=headers, data=payload)

        response_data = server_response.json()


        # Raise error or return success based on the response code
        response_code = server_response.status_code

        if response_code == 201:        # Token generated
            # Extract token and update headers
            token = response_data['Authorization']
            self.connection.headers.update({'Authorization':token})
            return True
        elif response_code == 404:
            raise FossologyInvalidCredentialsError()
        else:
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])


    def get_all_uploads(self):
        '''Returns a list of all uploads on the server'''
        uploads = []
        uploads_endpoint = 'uploads'
        endpoint = self.util._join_url(self.api_server, uploads_endpoint)

        headers = {'Content-Type': 'application/json'}

        # request a list of all uploads from the server
        server_response = self.connection.get(endpoint, headers=headers)

        response_data = server_response.json()


        # Raise error or return success based on the response code
        response_code = server_response.status_code

        if response_code != 200:
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])

        # Create new Upload objects from the data received
        for upload in response_data:
            uploads.append(Upload(
                upload_id = upload['id'],
                folder_id = upload['folderid'],
                folder_name = upload['foldername'],
                description = upload['description'],
                upload_name = upload['uploadname'],
                upload_date = upload['uploaddate'],
                filesize = upload['filesize']))


        return uploads


    def new_upload(self):
        '''Create a new upload on the server'''
        pass

    def upload(self, upload_id):
        '''Gets a single upload from the server'''
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
