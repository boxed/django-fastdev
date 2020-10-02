Changelog
---------

1.0.2
~~~~~

* Last release broke that {% if non_existant %} should work for checking existence of a variable.


1.0.1
~~~~~

* Fixed infinite recursion problem for things where str(x) tries to render a template (this is common in iommi)

1.0.0
~~~~~

* Initial release
