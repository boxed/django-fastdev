Changelog
---------

1.11.0
~~~~~~

* Fixed a bug with the invalid block checker

* Adds a new monkey patch for `Model.__repr__` to fix infinite recursion in error messages for `DoesNotExist` and `MultipleObjectsReturned` (the first is a fastdev bug and the second is a Django bug)


1.10.0
~~~~~~

* Reintroduced invalid block check with fixes


1.9.0
~~~~~

* Fix for strict if on 500 pages in prod
* Improve the reliability of venv gitignore checking
* Modify errors to be printed to stderr instead of stdout
* Check if virtualenv ENV is set


1.8.0
~~~~~

* Adds error handling on bad usages of dotted paths in blocktrans.

1.7.6
~~~~~

* Raise exceptions from `Template('....')` type literals with unknown source file

1.7.5
~~~~~

* Last release was incorrectly performed so missed the fix in 1.7.3

1.7.4
~~~~~

* Strict `{% if %}` put the 500 debug page into an infinite loop


1.7.3
~~~~~

* Changed: only HTML templates within your main project directory are checked; HTML templates outside of your main project directory revert to standard django behavior


1.7.2
~~~~~

* Fixed: include template tags in source distribution


1.7.1
~~~~~

* Fix for bug in gitignore validation


1.7.0
~~~~~

* New template tag: '{% ifexists foo %}{% elifexists bar %}{% else %}{% endifexists %}` to use instead of `{% if %}` to check if a variable exists in the context.

* Warn if you use `{% if %}` to check for existance of a variable (really warn if it triggers false if the lookup fails)

* New setting: `FASTDEV_STRICT_IF`. Set this to `True` to make `{% if %}` crash on non-existant variables. This setting will very likely break some of the Django admin, because it relies on this behavior!


* Check that the venv and pycache stuff is in .gitignore


1.6.0
~~~~~

* Non-existant variable accessed inside an `{% if %}` didn't crash.

* Warning on invalid fk field name. So for example using `car_id = ForeignKey(Car)` will now warn and explain what you should do.


1.5.0
~~~~~

* .gitignore validation

* Removed accidental debug print left in the code.


1.4.2
~~~~~

* Removed invalid block check. It didn't work properly.


1.4.1
~~~~~

* Fixed error message when trying to access `Context` object

1.4.0
~~~~~

* Invalid block checks corrected. The old check gave errors for valid stuff in some situations.

* New feature: QuerySet.get() improved error message.

1.3.0
~~~~~

* Validate `clean_*` methods

1.2.1
~~~~~

* Fixed errors on non-space outside blocks feature

1.2.0
~~~~~

* Errors if you have non-space outside blocks, and error if you have invalid block names when extending (fixes #5)

* Make runserver run the checks but on a separate thread to make the server start faster

1.1.0
~~~~~

* New feature: much better error messages on bad `reverse()`/`{% url %}`!


1.0.7
~~~~~

* Fixed crash on first load


1.0.6
~~~~~

* Fixed a case where fastdev stepped on its own toes. Thanks Sam Tilley for the help!


1.0.5
~~~~~

* `{% firstof %}` should fail silently


1.0.4
~~~~~

* Fixed broken install


1.0.3
~~~~~

* Lower requirements. Thanks cb109.


1.0.2
~~~~~

* Last release broke that {% if non_existant %} should work for checking existence of a variable.


1.0.1
~~~~~

* Fixed infinite recursion problem for things where str(x) tries to render a template (this is common in iommi)

1.0.0
~~~~~

* Initial release
