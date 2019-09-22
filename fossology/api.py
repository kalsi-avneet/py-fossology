import json
from requests import Request, Session


from fossology import utils
from fossology.exceptions import FossologyError,\
        FossologyInvalidCredentialsError

class Connection():
    def __init__(self, server):
        self.server = server

        self.session = Session()
        self.headers = self.session.headers

    def _send_request(self, prepped_request):
        '''Sends a received prepared request

        Returns a response object if successful, or
            throws a FossologyError
        '''
        response = self.session.send(prepped_request)
        response_code = response.status_code

        # Raise an error if the request was not successful
        if 400 <= response_code <=599 :
            response_data = response.json()
            raise FossologyError(response_code,
                    response_data.get('message'),
                    response_data.get('type'))

        return response


    def delete(self, url_fragments, *args, **kwargs):
        url = utils._join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='DELETE', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def get(self, url_fragments, *args, **kwargs):
        '''Wrapper around a sessions GET request
        '''
        url = utils._join_url(self.server, *url_fragments)

        prepared_request = self.session.prepare_request(
                Request(method='GET', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def patch(self, url_fragments, *args, **kwargs):
        url = utils._join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='PATCH', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def post(self, url_fragments, *args, **kwargs):
        '''Wrapper around a sessions POST request
        '''
        url = utils._join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='POST', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def put(self, url_fragments, *args, **kwargs):
        url = utils._join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='PUT', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def close_connection(self):
        self.session.close()

class Fossology():
    def __init__(self, server):

        api_server = utils._join_url(server, 'api/v1')

        # setup connection
        self.connection = Connection(server=api_server)

        # Add common headers to the connection
        self.connection.headers.update({
            'accept': 'application/json'
            })

        # (TODO): Setup logger if requested

    def __del__(self):

        # close the connection
        self.connection.close_connection()


    def generate_auth_token(self, username, password, expire, scope='read'):
        '''Requests a new token from the fossology server

        Adds the token to the session if successful, else
            raises a FossologyError
        '''

        # Create the URL for this endpoint
        endpoint_fragment = 'tokens'

        headers = {'Content-Type': 'application/json'}

        # Prepare data to send with the request
        payload = json.dumps({"username": username,
             'password': password,
             'token_name': utils._generate_unique_name(),
             'token_scope': scope,
             'token_expire': expire
             })

        # request a token from the server
        server_response = self.connection.post(
                url_fragments=[endpoint_fragment],
                headers=headers, data=payload)
        response_code = server_response.status_code

        if response_code == 201:        # Token generated
            response_data = server_response.json()
            # Extract token and update headers
            token = response_data['Authorization']
            self.connection.headers.update({'Authorization':token})
            return True
        else:
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])


    def get_all_uploads(self):
        '''Returns a list of all uploads on the server'''
        uploads = []
        endpoint_fragment = 'uploads'
        headers = {'Content-Type': 'application/json'}

        # request a list of all uploads from the server
        server_response = self.connection.get(
                url_fragments=[endpoint_fragment], headers=headers)
        response_code = server_response.status_code


        if response_code == 200:
            response_data = server_response.json()

            # Create new Upload objects from the data received
            for upload in response_data:
                uploads.append(Upload(
                    upload_id = upload['id'],
                    folder_id = upload['folderid'],
                    folder_name = upload['foldername'],
                    description = upload['description'],
                    upload_name = upload['uploadname'],
                    upload_date = upload['uploaddate'],
                    filesize = upload['filesize'],
                    connection = self.connection))


        return uploads


    def new_upload(self):
        '''Create a new upload on the server'''
        pass

    def upload(self, upload_id):
        '''Gets a single upload from the server'''
        endpoint_fragments = ['uploads', upload_id]

        headers = {'Content-Type': 'application/json'}

        # request upload data from server
        server_response = self.connection.get(
                url_fragments=endpoint_fragments, headers=headers)
        response_code = server_response.status_code

        if response_code == 200:
            response_data = server_response.json()

            # Return a new Upload object from the data received
            return Upload(
                upload_id = response_data['id'],
                folder_id = response_data['folderid'],
                folder_name = response_data['foldername'],
                description = response_data['description'],
                upload_name = response_data['uploadname'],
                upload_date = response_data['uploaddate'],
                filesize = response_data['filesize'],
                connection=self.connection)




class Upload():
    '''Denotes a single upload'''

    def __init__(self, upload_id, connection,
            folder_id=None,
            folder_name=None,
            description=None,
            upload_name=None,
            upload_date=None,
            filesize=None):

        self.upload_id = upload_id
        self.folder_id = folder_id
        self.folder_name = folder_name
        self.description = description
        self.upload_name = upload_name
        self.upload_date = upload_date
        self.filesize = filesize
        self.connection = connection

        self._endpoint_fragment = 'uploads'


    def delete(self):
        '''Delete an upload'''
        url_fragments = [self._endpoint_fragment, self.upload_id]

        # request upload deletion
        server_response = self.connection.delete(
                url_fragments=url_fragments)

        response_code = server_response.status_code
        return response_code == 202     # Accepted



    def move(self, destination_folder_id):
        '''Move an upload to another folder'''
        url_fragments = [self._endpoint_fragment, self.upload_id]

        headers = {'folderId': str(destination_folder_id)}

        # request to move current upload
        server_response = self.connection.patch(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted

    def copy(self, destination_folder_id) -> bool:
        '''Move an upload to another folder'''
        url_fragments = [self._endpoint_fragment, self.upload_id]

        headers = {'folderId': str(destination_folder_id)}

        # request to move current upload
        server_response = self.connection.put(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted
