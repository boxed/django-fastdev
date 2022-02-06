Changelog
---------

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
