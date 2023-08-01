import win32api,win32con
from threading import Thread

class msg(Thread):
    def __init__(self, title, msg):
        Thread.__init__(self)
        self.title = title
        self.msg = msg
    def run(self):
        win32api.MessageBox(0, self.msg, self.title) #,win32con.MBOK)

if __name__ == "__main__":
    msg(title="测试",msg="这是一个MSGBox测试代码。").start()
