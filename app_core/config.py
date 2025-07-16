import configparser, os
CONFIG_FILE = 'config.ini'

def load_api_key():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        return config.get('google','api_key',fallback='')
    return ''

def save_api_key(api_key: str):
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    if 'google' not in config:
        config['google'] = {}
    config['google']['api_key'] = api_key
    with open(CONFIG_FILE,'w') as f:
        config.write(f)
