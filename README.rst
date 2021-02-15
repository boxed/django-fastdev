django-fastdev
==============

Django-fastdev is an app that makes it faster and more fun to develop Django apps.

Features
--------

Faster runserver
~~~~~~~~~~~~~~~~

Django-fastdev turns off the model validation of the runserver. This makes the runserver *much* faster to start/restart, and you aren't editing your models 90% of the time anyway, and when you do and have a problem, the error messages from Django are fairly understandable anyway.


Saner templates
~~~~~~~~~~~~~~~

Django templates by default hide errors, and when it does show an error it's often not very helpful. This app will change this so that if you do:

.. code:: html

    {{ does_not_exist }}

instead of rendering that as an empty string, this app will give you an error message:

.. code::

    does_not_exist does not exist in context. Available top level variables:

        DEFAULT_MESSAGE_LEVELS
        False
        None
        True
        bar
        csrf_token
        foo
        messages
        perms
        request
        user

There are more specialized error messages for when you try to access the contents of a `dict`, and attributes of an object a few levels deep like `foo.bar.baz` (where baz doesn't exist).


Usage
------

First install: `pip install django-fastdev`

In `settings.py` add `django_fastdev` to INSTALLED_APPS:

.. code:: python

    INSTALLED_APPS = [
        # ...
        'django_fastdev',
   ]


Enjoy a nicer Django experience!


License
-------

BSD
