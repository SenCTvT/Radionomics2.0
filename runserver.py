from FlaskApp import app
import sys
import logging
import site

logging.basicConfig(stream=sys.stderr)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5600)