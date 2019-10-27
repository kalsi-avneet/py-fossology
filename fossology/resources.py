from fossology.exceptions import FossologyError,\
        FossologyInvalidCredentialsError



def job(job_id, connection):
    '''Gets a single job from the server'''
    endpoint_fragments = ['jobs', job_id]

    headers = {'Content-Type': 'application/json'}

    # request job data
    server_response = connection.get(
            url_fragments=endpoint_fragments, headers=headers)
    response_code = server_response.status_code

    if response_code == 200:
        response_data = server_response.json()

        # Return a new 'Job' object
        return Job(
                job_id = response_data['id'],
                name = response_data['name'],
                queueDate = response_data['queueDate'],
                upload_id = response_data['uploadId'],
                user_id = response_data['userId'],
                group_id = response_data['groupId'],
                connection = connection)

def folder(folder_id, connection):
    '''Gets a single folder from the server'''
    endpoint_fragments = ['folders', folder_id]

    headers = {'Content-Type': 'application/json'}

    # request folder data
    server_response =connection.get(
            url_fragments=endpoint_fragments, headers=headers)
    response_code = server_response.status_code

    if response_code == 200:
        response_data = server_response.json()

        # Return a new 'Folder' object
        return Folder(
                folder_id = response_data['id'],
                folder_name = response_data['name'],
                description = response_data['description'],
                connection =connection)


class Upload():
    '''Denotes a single upload'''

    def __init__(self, upload_id, connection,
            folder_id=None,
            folder_name=None,
            description=None,
            upload_name=None,
            upload_date=None,
            filesize=None):

        self.upload_id = str(upload_id)
        self.folder_id = str(folder_id)
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



    def move(self, destination_folder):
        '''Move an upload to another folder'''
        url_fragments = [self._endpoint_fragment, self.upload_id]

        headers = {'folderId': destination_folder.folder_id}

        # request to move current upload
        server_response = self.connection.patch(
                url_fragments=url_fragments, headers=headers)

        # update local object if successfully updated on server
        if server_response.status_code == 202:
            self.folder_id = destination_folder.folder_id
            self.folder_name = destination_folder.folder_name
            return True

    def copy(self, destination_folder):
        '''Move an upload to another folder'''
        url_fragments = [self._endpoint_fragment, self.upload_id]

        headers = {'folderId': destination_folder.folder_id}

        # request to move current upload
        server_response = self.connection.put(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted

    def schedule_agents(self, agents):
        '''Schedule agents on this upload'''
        url_fragments = ['jobs']

        headers = {'Content-Type': 'application/json',
                    'folderId':self.folder_id,
                    'uploadId':self.upload_id}

        # request the server to schedule an analysis
        server_response = self.connection.post(
                url_fragments=url_fragments, headers=headers,
                data=agents)

        response_code = server_response.status_code

        if response_code == 201:
            response_data = server_response.json()
            # Extract job id and return a job object
            job_id = response_data['message']
            return job(job_id=job_id, connection=self.connection)
        else:
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])


    def request_report_generation(self, reportFormat):
        '''Request a report to be generated for this upload'''
        url_fragments = ['report']

        headers = {'uploadId': str(self.upload_id),
                    'reportFormat':reportFormat}

        # request report generation
        server_response = self.connection.get(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        if response_code == 201:
            response_data = server_response.json()
            report_id = response_data['message'].split('/')[-1]

            return Report(report_id=report_id,
                    reportFormat=reportFormat,
                    connection=self.connection)

        else:
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])



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


    def create_child_folder(self, folder_name,
            folder_description=None):
        '''Create a new folder inside the current folder'''
        url_fragments = [self._endpoint_fragment]

        headers = {
                'parentFolder': self.folder_id,
                'folderName':folder_name,
                'folderDescription':folder_description}

        server_response = self.connection.post(
                url_fragments=url_fragments,
                headers=headers)

        response_code = server_response.status_code
        response_data = server_response.json()

        if response_code == 201:        # Folder created
            # Create a folder object with received folder id
            return folder(folder_id=response_data.get('message'),
                            connection=self.connection)
        else:    # includes 200: (Folder with the same name already exists under the same parent)
            raise FossologyError(response_code,
                    response_data['message'],
                    response_data['type'])


    def delete(self):
        '''Delete a folder'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        # request folder deletion
        server_response = self.connection.delete(
                url_fragments=url_fragments)

        response_code = server_response.status_code
        return response_code == 202     # Accepted


    def move(self, parent_folder):
        '''Move a folder under a new parent'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'parent': parent_folder.folder_id,
                'action':'move'}

        # request to move current folder
        server_response = self.connection.put(
                url_fragments=url_fragments, headers=headers)

        response_code = server_response.status_code
        return response_code == 202     # Accepted

    def copy(self, parent_folder):
        '''Copy a folder under another parent'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'parent': parent_folder.folder_id,
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

        # update local object if successfully updated on server
        if server_response.status_code == 200:
            self.folder_name = new_name
            return True

    def edit_description(self, new_description):
        '''Modify a folder's description'''
        url_fragments = [self._endpoint_fragment, self.folder_id]

        headers = {'description': new_description}

        # request to modify current folder description
        server_response = self.connection.patch(
                url_fragments=url_fragments, headers=headers)

        # update local object if successfully updated on server
        if server_response.status_code == 200:
            self.description = new_description
            return True

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


class Job():
    '''Denotes a single job on the server'''

    def __init__(self, job_id, name, queueDate, upload_id,
            user_id, group_id, connection):
        self.job_id=job_id
        self.name=name
        self.queueDate=queueDate
        self.upload_id=upload_id   # TODO: make this Upload object
        self.user_id=user_id       # TODO: make this a User object
        self.group_id=group_id
        self.connection=connection

        self._endpoint_fragment = 'jobs'

class Report():
    '''Denotes a single report on the server'''

    def __init__(self, report_id, reportFormat,
            connection):
        self.report_id=report_id
        self.reportFormat=reportFormat
        self.connection=connection

        self._endpoint_fragment = 'report'


    def download(self, filename=None):
        '''Downloads a generated report'''
        url_fragments = [self._endpoint_fragment, self.report_id]

        return self.connection.download_file(url_fragments, filename)
