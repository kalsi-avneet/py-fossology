# py-fossology
Python wrapper around FOSSology's REST API.

Works with FOSSology version 3.5.0

# Example usage
```python

from fossology import Fossology

fossology = Fossology(server='http://localhost:8085/repo/',
                      auth={'username' : 'fossy',
                            'password' : 'fossy',
                            'token_scope' : 'write',
                            'token_expire' : '2019-09-07'
                            })


# create a new folder
fossology.new_folder(parent_folder_id=1, folder_name='sample')

# List all folders
for folder in fossology.get_all_folders():
    print(folder.folder_name)

# Upload a file
fossology.new_upload(folder_id=1, fileInput='/tmp/sample.tar')
```

# Documentation
TBD
  
  
# Installation
TBD
  
