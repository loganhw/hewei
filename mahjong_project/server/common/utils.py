# -*- coding:utf -*-

import threading


def create_thread(func, func_args=()):
    t = threading.Thread(target=func, args=func_args)
    t.setDaemon(True)
    t.start()
