# -*- coding = utf-8 -*-
# @Author : VV1P1n
# @time : 2024/4/21 : 10:21

class NotLoggedIn(Exception):
    def __init__(self, code=0, msg=None):
        self.code = code
        self.msg = msg

    def __str__(self):
        return f"ERROR CODE: {self.code} PS: {self.msg}"

