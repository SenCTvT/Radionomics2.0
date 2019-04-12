import os

BASE_URL = 'http://localhost:5600'
if 'HOST' in os.environ: 
    BASE_URL = os.environ['HOST']


UPLOAD_DIR = '/var/www/temp_uploads/'
if os.name == 'nt':
    UPLOAD_DIR = "C:\\temp\\"
