class Config:
    SECRET_KEY = 'ted-talks-annotation'
    MONGODB_SETTINGS = {
        'host': '127.0.0.1',
        'db': 'ted_talks',
        'port': 27017,
        # 'username': 'YOUR_DB_USERNAME',
        # 'password': 'YOUR_DB_PASSWORD',
    }
