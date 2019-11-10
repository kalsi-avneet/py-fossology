import json
from collections import namedtuple

from fossology import utils
from fossology.exceptions import FossologyError
from fossology.resources import Upload, Folder, User, Job, folder, job


class Fossology():
    def __init__(self, server, auth):

        api_server = utils._join_url(server, 'api/v1')

        # setup connection
        self.connection = utils.Connection(server=api_server)

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


    def new_upload(self, target_folder, fileInput,
            upload_description=None, public='public'):
        '''Create a new upload on the server'''
        endpoint_fragments = ['uploads']

        target_folder_id = target_folder.folder_id
        target_folder_name = target_folder.folder_name
        headers = {'folderId': target_folder_id,
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
            return Upload(
                upload_id = response_data['message'],
                folder_id = target_folder_id,
                folder_name = target_folder_name,
                description = upload_description,
                connection=self.connection)


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
        return folder(folder_id=folder_id,
                connection=self.connection)


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


    def new_folder(self, parent_folder, folder_name,
                    folder_description=None):
        '''Create a new folder on the server'''

        return parent_folder.create_child_folder(
                            folder_name=folder_name,
                            folder_description=folder_description)

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


    def job(self, job_id):
        '''Gets a single job from the server'''
        return job(job_id=job_id,
                connection=self.connection)


    def get_all_jobs(self, limit=None):
        '''Gets a list of all jobs on the server'''
        jobs = []
        endpoint_fragment = 'jobs'
        headers = {'Content-Type': 'application/json',
                'limit': str(limit)}

        # request a list of all jobs from the server
        server_response = self.connection.get(
                url_fragments=[endpoint_fragment], headers=headers)
        response_code = server_response.status_code


        if response_code == 200:
            response_data = server_response.json()

            # Create new Job objects from the data received
            for job in response_data:
                jobs.append(Job(
                    job_id = job['id'],
                    name = job['name'],
                    queueDate = job['queueDate'],
                    upload_id = job['uploadId'],
                    user_id = job['userId'],
                    group_id = job['groupId'],
                    connection = self.connection))

        return jobs


    def schedule_agents(self, upload, agents):
        '''Schedule agents on an existing upload'''

        return upload.schedule_agents(agents=agents)


    def search(self, search_type=None, filename=None, tag=None,
                filesizemin=None, filesizemax=None, license=None,
                copyright=None):
        '''Search FOSSology for a specific file'''
        search_results = []
        search_result = namedtuple('search_result',
                                    'upload uploadTreeId filename')
        endpoint_fragment = 'search'


        headers = {
                'searchType': search_type,
                'filename': filename,
                'tag': tag,
                'filesizemin': filesizemin,
                'filesizemax': filesizemax,
                'license': license,
                'copyright': copyright
                }


        # Send a search request to the server
        server_response = self.connection.get(url_fragments=[endpoint_fragment],
                    headers=headers)
        response_code = server_response.status_code


        if response_code == 200:
            response_data = server_response.json()

            # append each search result to 'search_results'
            for result in response_data:
                # result contains of the following:
                _filename = result['filename']
                _upload_tree_id = result['uploadTreeId']
                _upload=result['upload']

                # Create an Upload object
                upload=Upload(
                    upload_id = _upload['id'],
                    folder_id = _upload['folderid'],
                    folder_name = _upload['foldername'],
                    description = _upload['description'],
                    upload_name = _upload['uploadname'],
                    upload_date = _upload['uploaddate'],
                    filesize = _upload['filesize'],

                    connection=self.connection)

                # append to the list
                search_results.append(
                        search_result(filename=result['filename'],
                                uploadTreeId=result['uploadTreeId'],
                                upload=upload))

        else:
            error_response = server_response.json()
            raise FossologyError(response_code,
                    error_response['message'],
                    error_response['type'])

        return search_results

