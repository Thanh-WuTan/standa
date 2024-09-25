from datetime import datetime, timezone

def get_current_timestamp():
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    return datetime.now(timezone.utc).strftime(TIME_FORMAT)

class Result: 
    def __init__(self, time_start=get_current_timestamp().replace("Z", ".000Z"), 
                       time_stop=get_current_timestamp().replace("Z", ".000Z"), 
                       stdout="", stderr=""):
        self.time_start = time_start 
        self.time_stop = time_stop
        self.stdout = stdout
        self.stderr = stderr
