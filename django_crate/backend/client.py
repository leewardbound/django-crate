# -*- coding: utf-8 -*-
from django.db.backends.base.client import BaseDatabaseClient
from crate.crash.command import main as crash_main
import sys

class DatabaseClient(BaseDatabaseClient):
    executable_name = 'crash'

    def runshell(self):
        sys.argv = [sys.argv[0], "--hosts"]
        for server in self.connection.settings_dict['SERVERS']:
            sys.argv.extend(("--hosts", server))
        crash_main()
