django-fastdev
==============

Django-fastdev is an app that makes it faster and more fun to develop Django apps.

Features
--------

Faster runserver
~~~~~~~~~~~~~~~~

Django-fastdev turns off the model validation of the runserver. This makes the runserver *much* faster to start/restart, and you aren't editing your models 90% of the time anyway, and when you do and have a problem, the error messages from Django are fairly understandable anyway.


Error on non-existant template variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Error if you have non-space text outside a block when extending
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common mistake for beginners that can be hard to spot is when they do:

..  code-block:: html

    <html>
        {% extends "something.html" %}
        stuff here
    </html>

Django silently throws away `stuff here` and `</html>`. `Django-fastdev` makes this an error.


Error on invalid block names when using `{% extends "..." %}`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have a base template:

..  code-block:: html

    <html>
        <body>
            {% block content %}{% endblock %}
        </body>
    </html>

and then write a template like this:

..  code-block:: html

    {% extends "base.html" %}

    {% block contents %}
        hello!
    {% endblock %}


Django will silently throw away `hello!` because you wrote `contents` instead
of `content`. `Django-fastdev` will turn this into an error which lists the
invalid and valid block names in alphabetical order.

Better error messages for reverse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard error message for a bad `reverse()`/`{% url %}` are rather sparse.
`Django-fastdev` improves them by listing valid patterns so you can easily see
the problem.


Faster startup
~~~~~~~~~~~~~~

The initial model checks can be quite slow on big projects. `Django-fastdev`
will move these checks to a separate thread, so the runserver startup time is
lowered, so you don't have to wait for the runserver restart as long.


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
