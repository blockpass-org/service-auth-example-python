import os

class Config(object):
  PORT = os.getenv('PORT', '3000')
  GUNICORN_TOTAL_WORKERS = int(os.getenv('GUNICORN_TOTAL_WORKERS', '1'))
  LOGGER_HOST = os.getenv('LOGGER_HOST', 'localhost')
  LOGGER_PORT = os.getenv('LOGGER_PORT', False)
  GUNICORN_SYSLOG_ADDRESS = os.getenv('GUNICORN_SYSLOG_ADDRESS', 'localhost')
  BP_URL = os.getenv('BP_URL', 'https://sandbox-api.blockpass.org')
  BP_CLIENT_ID = os.getenv('BP_CLIENT_ID', 'developer_service')
  BP_SECRET_ID = os.getenv('BP_SECRET_ID', 'developer_service')
