import time


class timer:
    def __init__(self):
        self.cur_time = time.time()

    def elapsed(self, txt):
        print("{}: {}".format(txt, time.time()-self.cur_time))
        self.cur_time = time.time()
