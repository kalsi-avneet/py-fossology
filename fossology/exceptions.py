class FossologyError(Exception):
    '''General exception raised for most Fossology REST api errors

    Attributes:
        err_code -- Error code returned by Fossology
        err_msg -- Message returned by Fossology
        err_type -- Type of error returned by Fossology
    '''

    def __init__(self, err_code, err_msg, err_type):
        self.err_code = err_code
        self.err_msg = err_msg
        self.err_type = err_type

    def __str__(self):
        return self.err_msg

class FossologyInvalidCredentialsError(FossologyError):
    '''Raised when authenticating with invalid username or password
    '''
    def __init__(self):
        super().__init__(err_code = 404,
                err_msg = 'Username or password incorrect.',
                err_type = 'ERROR')

    def __str__(self):
        return self.err_msg

class FossologyResourceNotReadyError(FossologyError):
    '''Raised when authenticating with invalid username or password
    '''
    def __init__(self, err_code, err_msg, err_type, retry_after):
        super().__init__(err_code = err_code,
                err_msg = err_msg,
                err_type = err_type)
        self.retry_after = retry_after

    def __str__(self):
        return self.err_msg

# class FossologyTokenConflictError(FossologyError):
#     '''Raised when requesting a new token with an existing name'''
#     def __init__(self):
#         super().__init__(err_code = 409,
#                 err_msg = 'Already have a token with same name.',
#                 err_type = 'ERROR')

#     def __str__(self):
#         return self.err_msg
