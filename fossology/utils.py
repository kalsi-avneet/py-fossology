from posixpath import join
from uuid import uuid4


def _join_url(base_url, *fragments):
    '''Returns a URL constructed from the base_url and fragments '''

    return join(base_url, *fragments)

def _generate_unique_name():
    '''Generates a unique ID'''

    return str(uuid4())


