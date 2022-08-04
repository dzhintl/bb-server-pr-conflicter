import base64
from configparser import SafeConfigParser


class Credential:
    
    KEY_HMAC_KEY = 'HMAC_KEY'
    KEY_HMAC_SHA = 'HMAC_SHA'
    KEY_USERNAME = 'USERNAME'
    KEY_PASSWORD = 'PASSWORD'


    hmac_key = ''
    hmac_sha = 'SHA256'
    username = ''
    password = ''

    def __init__(self, config_file, section) -> None:
        config_parser = SafeConfigParser()
        config_parser.read(config_file)

        if config_parser.has_option(section, self.KEY_HMAC_KEY):
            self.hmac_key = config_parser.get(section, self.KEY_HMAC_KEY)

        if config_parser.has_option(section, self.KEY_HMAC_SHA):
            self.hmac_sha = config_parser.get(section, self.KEY_HMAC_SHA)

        if config_parser.has_option(section, self.KEY_USERNAME):
            self.username = config_parser.get(section, self.KEY_USERNAME)
        
        if config_parser.has_option(section, self.KEY_PASSWORD):
            self.password = config_parser.get(section, self.KEY_PASSWORD)
        

    def get_password(self) -> str:
        return base64.b64decode(self.password).decode('utf-8')

    def get_username(self) -> str:
        return base64.b64decode(self.username).decode('utf-8')

    def get_hmac_key(self) -> bytes:
        return base64.b64decode(self.hmac_key)

    def get_hmac_sha(self) -> str:
        return self.hmac_sha
