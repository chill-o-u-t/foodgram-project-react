import re

SYMBOLS_TAG = re.compile(r'^[-a-zA-Z0-9_]+$')

SYMBOLS_USERNAME = re.compile(r'[\w.@+-@./+-]+')
