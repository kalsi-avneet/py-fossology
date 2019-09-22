from posixpath import join
from uuid import uuid4


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


