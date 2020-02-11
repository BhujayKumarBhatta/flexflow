import json


class FlexFlowException(Exception):
    status = "UNKNOWN_STATUS"
    message = "Unknown status"

    def __init__(self, status=None, message=None):
        if status:  self.status = status
        if message: self.message = message
        self.ret_val = {"status": self.status, "message": self.message }
        super(FlexFlowException, self).__init__(self.status, self.message)

    def __str__(self):
        return json.dumps(self.ret_val)


    def __repr__(self):
        return self.ret_val