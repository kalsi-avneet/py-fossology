from posixpath import join
from requests import Request, Session
from uuid import uuid4
import cgi


from fossology.exceptions import FossologyError, FossologyResourceNotReadyError


def _join_url(base_url, *fragments):
    '''Returns a URL constructed from the base_url and fragments '''
    #TODO: Rewrite this to remove limitations of posixpath.join

    # make sure that all passed args are strings
    base_url=str(base_url)
    fragments = [str(i) for i in fragments]

    return join(base_url, *fragments)

def _generate_unique_name():
    '''Generates a unique ID'''

    return str(uuid4())


class Connection():
    def __init__(self, server):
        self.server = server

        self.session = Session()
        self.headers = self.session.headers

    def upload_file(self, url_fragments, file, *args, **kwargs):

        url = _join_url(self.server, *url_fragments)

        with open(file, 'rb') as fi:
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

    def download_file(self, url_fragments, filename=None,
            *args, **kwargs):
        '''Downloads a file

        Returns a filename if successful, else throws an error
          - FossologyResourceNotReadyError if resource is not ready
          - FossologyError for any other error
        '''
        url = _join_url(self.server, *url_fragments)
        response = self.session.get(url, stream=True,
                *args, **kwargs)

        chunks = response.iter_content()
        response_code = response.status_code
        if response_code == 200:
            # Try to extract the filename
            _,params = cgi.parse_header(
                    response.headers.get('Content-Disposition'))
            filename = filename or params.get('filename','download')

            # Write the downloaded data to the file
            with open(filename, 'wb') as f:
                for chunk in chunks:
                    f.write(chunk)
            return filename

        elif response_code == 503:
            response_data = response.json()
            raise FossologyResourceNotReadyError(response_code,
                    response_data['message'],
                    response_data['type'],
                    response.headers.get('Retry-After'))
        else:
            raise FossologyError(response_code, None, None)


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
        url = _join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='DELETE', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def get(self, url_fragments, *args, **kwargs):
        '''Wrapper around a sessions GET request
        '''
        url = _join_url(self.server, *url_fragments)

        prepared_request = self.session.prepare_request(
                Request(method='GET', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def patch(self, url_fragments, *args, **kwargs):
        url = _join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='PATCH', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def post(self, url_fragments, *args, **kwargs):
        '''Wrapper around a sessions POST request
        '''
        url = _join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='POST', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def put(self, url_fragments, *args, **kwargs):
        url = _join_url(self.server, *url_fragments)
        prepared_request = self.session.prepare_request(
                Request(method='PUT', url=url, *args, **kwargs))
        return(self._send_request(prepared_request))


    def close_connection(self):
        self.session.close()
