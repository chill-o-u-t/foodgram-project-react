import re

SYMBOLS_TAG = re.compile(r'^[-a-zA-Z0-9_]+$')
SYMBOLS_COLOR = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
SYMBOLS_USERNAME = re.compile(r'[\w.@+-@./+-]+')
