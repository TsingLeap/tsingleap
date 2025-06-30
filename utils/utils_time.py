import datetime

EMAIL_VERIFICATION_EXPIRE_TIME = 10 * 60  # 10 minutes
EMAIL_VERIFICATION_SEND_INTERVAL = 60  # 1 minute

def get_timestamp():
    return (datetime.datetime.now()).timestamp()
