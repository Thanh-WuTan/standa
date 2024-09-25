from datetime import datetime, timezone

class Result:
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    def __init__(self, 
    time_start=get_current_timestamp().replace("Z", ".000Z"), 
    time_stop=get_current_timestamp().replace("Z", ".000Z"), 
    stdout, stderr):
        self.time_start = time_start 
        self.time_stop = time_stop
        self.stdout = stdout
        self.stderr = stderr


def get_current_timestamp(date_format=TIME_FORMAT):
    return datetime.now(timezone.utc).strftime(date_format)