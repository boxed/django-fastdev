django-fastdev
==============

:code:`django-fastdev` is an app that makes it safer, faster and more fun to develop Django apps.

Features
--------


Error on non-existent template variables
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

There are more specialized error messages for when you try to access the contents of a :code:`dict`, and attributes of an object a few levels deep like :code:`foo.bar.baz` (where baz doesn't exist).

By default, :code:`django-fastdev` only checks templates that exist within your project directory. If you want it to check ALL templates, including stock django templates and templates from third party libraries, add :code:`FASTDEV_STRICT_TEMPLATE_CHECKING = True` to your project :code:`settings.py`.


NoReverseMatch errors
~~~~~~~~~~~~~~~~~~~~~

Have you ever gotten this error?

.. code::

    django.urls.exceptions.NoReverseMatch: Reverse for 'view-name' with arguments '('',)' not found. 1 pattern(s) tried:


It's because you have :code:`{% url 'view-name' does_not_exist %}`. Django sees
:code:`does_not_exist` and evaluates it to the empty string because it doesn't exist.
So that's why you get an error message that makes no sense. :code:`django-fastdev` will
make your code crash on the actual error: :code:`does_not_exist` doesn't exist.


Error if you have non-space text outside a block when extending
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common mistake for beginners that can be hard to spot is when they do:

..  code-block:: html

    <html>
        {% extends "something.html" %}
        stuff here
    </html>

Django silently throws away :code:`stuff here` and :code:`</html>`. :code:`django-fastdev` makes this an error.


Error on invalid block names when using :code:`{% extends "..." %}`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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


Django will silently throw away `hello!` because you wrote :code:`contents` instead
of :code:`content`. :code:`django-fastdev` will turn this into an error which lists the
invalid and valid block names in alphabetical order.

Better error messages for reverse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard error message for a bad :code:`reverse()/{% url %}` are rather sparse.
:code:`django-fastdev` improves them by listing valid patterns so you can easily see
the problem.


Better error messages for QuerySet.get()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The error message for :code:`QuerySet.get()` is improved to give you the query
parameters that resulted in the exception.


Validate clean_* methods
~~~~~~~~~~~~~~~~~~~~~~~~

A common mistake is to make a form clean method and make a spelling error. By
default Django just won't call the function. With :code:`django-fastdev` you will get
an error message telling you that your clean method doesn't match anything.

This is also very useful during refactoring. Renaming a field is a lot safer
as if you forget to rename the clean method :code:`django-fastdev` will tell you!


Faster startup
~~~~~~~~~~~~~~

The initial model checks can be quite slow on big projects. :code:`django-fastdev`
will move these checks to a separate thread, so the runserver startup time is
lowered, so you don't have to wait for the runserver restart as long.


Usage
------

First install: :code:`pip install django-fastdev`

In :code:`settings.py` add :code:`django_fastdev` to INSTALLED_APPS:

.. code:: python

    INSTALLED_APPS = [
        # ...
        'django_fastdev',
   ]


Enjoy a nicer Django experience!


License
-------

BSD
