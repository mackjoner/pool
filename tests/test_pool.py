import time
import threading
from nose.tools import eq_
import pool.pool as M

class TestManager:
    def test_the_returned_obj_should_not_interfered_between_threads(self):
        @M.ThreadSafeFactory
        class MemcacheClient(object):
            def get(self, key):
                self.to_return = key
                # time.sleep to make thread switch, like socket operations
                time.sleep(0.1)
                return self.to_return

        def run_in_thread(func, args=(), kwargs={}, return_holder=[]):
            def f():
                ret = func(*args, **kwargs)
                return_holder.append(ret)
            t = threading.Thread(target=f)
            t.start()
            return t

        mc = MemcacheClient()
        r1, r2 = [], []
        t1 = run_in_thread(mc.get, args=(1,), return_holder=r1)
        t2 = run_in_thread(mc.get, args=(2,), return_holder=r2)
        t1.join()
        t2.join()
        eq_(r1, [1])
        eq_(r2, [2])


    def test_the_returned_obj_should_use_the_same_connection_for_same_thread(self):
        @M.ThreadSafeFactory
        class MemcacheClient(object):
            def get(self, key):
                return id(self)

        mc = MemcacheClient()
        v1 = mc.get('key1')
        v2 = mc.get('key2')
        eq_(v1, v2)
