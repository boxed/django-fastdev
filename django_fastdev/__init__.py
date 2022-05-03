__version__ = '1.7.1'

from threading import Thread
from time import sleep

default_app_config = 'django_fastdev.apps.FastDevConfig'


from django.core.management.commands.runserver import Command

orig_check = Command.check
orig_check_migrations = Command.check_migrations


def off_thread_check(self, *args, **kwargs):
    def inner():
        sleep(0.1)  # give the main thread some time to run
        orig_check(self, *args, **kwargs)
    t = Thread(target=inner)
    t.start()


def off_thread_check_migrations(self, *args, **kwargs):
    def inner():
        sleep(0.1)  # give the main thread some time to run
        orig_check_migrations(self, *args, **kwargs)
    t = Thread(target=inner)
    t.start()


Command.check = off_thread_check
Command.check_migrations = off_thread_check_migrations
