__author__ = 'mandriy'
# -*- coding: utf-8 -*-

import os
import utils
import server

if os.getenv('LAB2_TASKS'):
    server.init_server(utils.get_files(os.getenv('LAB2_TASKS')))
    server.run_server(host='0.0.0.0')

