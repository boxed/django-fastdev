__version__ = '1.0.3'


default_app_config = 'django_fastdev.django_app.FastDevConfig'


from django.core.management.commands.runserver import Command
Command.check = lambda *_, **__: print('Skipped model validations')
Command.check_migrations = lambda *_, **__: print('Skipped migrations checks')
