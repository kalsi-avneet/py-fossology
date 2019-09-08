import json
from requests import Session


from fossology.common import _util
from fossology.exceptions import FossologyError,\
        FossologyInvalidCredentialsError

class Connection():
    def __init__(self):
        self.session = Session()
        self.headers = self.session.headers

    def post(self, args, **kwargs):
        return self.session.post(args, **kwargs)

    def get(self, args, **kwargs):
        return self.session.get(args, **kwargs)

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


