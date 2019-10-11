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


# Get the root folder
root_folder = fossology.folder(folder_id=1)


# Upload a file to the root folder
upload = fossology.new_upload(target_folder=root_folder, fileInput='/tmp/sample.tar')

# Schedule a scan on this new upload
job = upload.schedule_agents(agents='''{
   "analysis": {
     "bucket": true,
     "copyright_email_author": true,
     "ecc": true,
     "keyword": true,
     "mime": true,
     "monk": true,
     "nomos": true,
     "package": true
   },
   "decider": {
     "nomos_monk": true,
     "bulk_reused": true,
     "new_scanner": true
   },
   "reuse": {
     "reuse_upload": 0,
     "reuse_group": 0,
     "reuse_main": true,
     "reuse_enhanced": true
   }
 }''')
 
 
# Generate a report
report = upload.request_report_generation(reportFormat='unifiedreport')

# Download the report
report.download()
```

# Documentation
TBD
  
  
# Installation
TBD
  
