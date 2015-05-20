__author__ = 'mandriy'

from multiprocessing import Process
import server
import utils


def open_web_driver(web_driver_to_open):
    class WebDriverContextManager(web_driver_to_open):

        def __init__(self):
            web_driver_to_open.__init__(self)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            self.close()

    return WebDriverContextManager()


class PersonsLookerLifecycle:

    def __init__(self, init_data, server_root):
        def run_server(data, root):
            utils.set_server_root(root)
            server.init_server(data)
            server.run_server()
        self.__server_thread__ = Process(target=run_server, args=(init_data, server_root))
        self.__server_thread__.start()

    def __enter__(self):
        return self.__server_thread__.pid

    def __exit__(self, *_):
        self.__server_thread__.terminate()