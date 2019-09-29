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

    def upload_file(self, url_fragments, file, *args, **kwargs):

        url = utils._join_url(self.server, *url_fragments)

        with open(file) as fi:
            response = self.session.post(url,
                            files={'fileInput':fi},
                            *args, **kwargs)
        response_code = response.status_code

        # Raise an error if the request was not successful
        if 400 <= response_code <=599 :
            response_data = response.json()
            raise FossologyError(response_code,
                    response_data.get('message'),
                    response_data.get('type'))

        return response


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
    def __init__(self, server, auth):

        api_server = utils._join_url(server, 'api/v1')

        # setup connection
        self.connection = Connection(server=api_server)

        # Add common headers to the connection
        self.connection.headers.update({
            'accept': 'application/json'
            })

        # Request the server for an auth token
        self.generate_auth_token(**auth)

        # (TODO): Setup logger if requested

    def __del__(self):

        # close the connection
        self.connection.close_connection()


    def generate_auth_token(self, username, password, token_expire,
                                token_name=None, token_scope='read'):
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
             'token_name': token_name or utils._generate_unique_name(),
             'token_scope': token_scope,
             'token_expire': token_expire
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


    def new_upload(self, folder_id, fileInput,
            upload_description=None, public='public'):
        '''Create a new upload on the server'''
        endpoint_fragments = ['uploads']

        headers = {'folderId': str(folder_id),
                    'uploadDescription':upload_description,
                    'public':public}

        server_response = self.connection.upload_file(
                url_fragments=endpoint_fragments,
                headers=headers,
                file=fileInput)

        response_code = server_response.status_code

        if response_code == 201:
            response_data = server_response.json()

            # fossology returns an upload ID.
            # Create an upload object with it
            return self.upload(response_data.get('message'))


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


    def folder(self, folder_id):
        '''Gets a single folder from the server'''
        endpoint_fragments = ['folders', folder_id]

        headers = {'Content-Type': 'application/json'}

        # request folder data
        server_response = self.connection.get(
                url_fragments=endpoint_fragments, headers=headers)
        response_code = server_response.status_code

        if response_code == 200:
            response_data = server_response.json()

            # Return a new 'Folder' object
            return Folder(
                    folder_id = response_data['id'],
                    folder_name = response_data['name'],
                    description = response_data['description'],
                    connection = self.connection)


    def get_all_folders(self):
        '''Returns a list of all folders on the server'''
        folders = []
        endpoint_fragment = 'folders'
        headers = {'Content-Type': 'application/json'}

        # Request a list of all accessible folders
        server_response = self.connection.get(
                url_fragments=[endpoint_fragment], headers=headers)
        response_code = server_response.status_code


        if response_code == 200:
            response_data = server_response.json()

            # Create new Folder objects from the data received
            for folder in response_data:
                folders.append(Folder(
                    folder_id = folder['id'],
                    folder_name = folder['name'],
                    description = folder['description'],
                    connection = self.connection))

        return folders


    def new_folder(self, parent_folder_id, folder_name,
                    folder_description=None):
        '''Create a new folder on the server'''
        endpoint_fragments = ['folders']

        headers = {
                'parentFolder': str(parent_folder_id),
                'folderName':folder_name,
                'folderDescription':folder_description}

        server_response = self.connection.post(
                url_fragments=endpoint_fragments,
                headers=headers)

        response_code = server_response.status_code
        response_data = server_response.json()

        if response_code == 201:        # Folder created
            # Create a folder object with received folder id
            return Folder(folder_id=response_data.get('message'),
                            connection=self.connection)
        else:    # includes 200: (Folder with the same name already exists under the same parent)
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])

    def get_all_users(self):
        '''Get a list of all users on the server'''
        users = []
        endpoint_fragment = 'users'
        headers = {'Content-Type': 'application/json'}

        # Request a list of all users
        server_response = self.connection.get(
                url_fragments=[endpoint_fragment], headers=headers)
        response_code = server_response.status_code


        if response_code == 200:
            response_data = server_response.json()

            # Create new User objects from the data received
            for user in response_data:
                users.append(User(
                    user_id = user['id'],
                    name = user['name'],
                    description = user['description'],
                    email = user['email'],
                    access_level = user['accessLevel'],
                    root_folder_id = user['rootFolderId'],
                    email_notification = user['emailNotification'],
                    agents = user['agents'],
                    connection = self.connection))

        return users

    def user(self, user_id):
        '''Gets a single user from the server'''
        endpoint_fragments = ['users', user_id]

        headers = {'Content-Type': 'application/json'}

        # request user data
        server_response = self.connection.get(
                url_fragments=endpoint_fragments, headers=headers)
        response_code = server_response.status_code

        if response_code == 200:
            response_data = server_response.json()

            # Return a new 'User' object
            return User(
                    user_id = response_data['id'],
                    name = response_data['name'],
                    description = response_data['description'],
                    email = response_data['email'],
                    access_level = response_data['accessLevel'],
                    root_folder_id = response_data['rootFolderId'],
                    email_notification = response_data['emailNotification'],
                    agents = response_data['agents'],
                    connection = self.connection)



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



class Folder():
    '''Denotes a single folder on the server'''

    def __init__(self,  folder_id, connection,
            folder_name=None,
            description=None):

        self.folder_id = str(folder_id)
        self.folder_name = folder_name
        self.description = description
        self.connection = connection

        self._endpoint_fragment = 'folders'


    def delete(self):
        '''Delete a folder'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        # request folder deletion
        server_response = self.connection.delete(
                url_fragments=url_fragments)

        response_code = server_response.status_code
        return response_code == 202     # Accepted


    def move(self, parent_folder_id):
        '''Move a folder under a new parent'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'parent': str(parent_folder_id),
                'action':'move'}

        # request to move current folder
        server_response = self.connection.put(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted

    def copy(self, parent_folder_id):
        '''Copy a folder under another parent'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'parent': str(parent_folder_id),
                'action':'copy'}

        # request to copy current folder
        server_response = self.connection.put(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted

    def rename(self, new_name):
        '''Rename a folder'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'name': new_name}

        # request to rename current folder
        server_response = self.connection.patch(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 200

    def edit_description(self, new_description):
        '''Modify a folder's description'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'description': new_description}

        # request to modify current folder description
        server_response = self.connection.patch(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 200

class User():
    '''Denotes a single user on the server'''

    def __init__(self, user_id, name, description, email,
            access_level, root_folder_id, email_notification,
            agents, connection):
        self.user_id=user_id
        self.name=name
        self.description=description
        self.email=email
        self.accessLevel=access_level
        self.rootFolderId=root_folder_id
        self.emailNotification=email_notification
        self.agents=agents
        self.connection=connection

        self._endpoint_fragment = 'users'


    def delete(self):
        '''Delete a user'''
        url_fragments = [self._endpoint_fragment, self.user_id]

        # request user deletion
        server_response = self.connection.delete(
                url_fragments=url_fragments)

        response_code = server_response.status_code
        return response_code == 202     # Accepted
