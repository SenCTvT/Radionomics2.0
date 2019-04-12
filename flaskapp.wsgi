#!/usr/bin/python
import sys
import logging
import site


logging.basicConfig(stream=sys.stderr)
sys.stdout = open('/var/www/temp_uploads/output.log', 'w')
sys.path.insert(0,"/var/www/Radionomics/")

from FlaskApp import app as application
application.secret_key = 'kd5NZKisDCPcz5w5vBdUdkFcTtM7OqUs'
