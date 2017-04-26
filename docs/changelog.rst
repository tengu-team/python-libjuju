Change Log
----------

0.4.0
^^^^^
Wed Apr 19 2017

* Feature/api version support (#109)
* Expanding controller.py with basic user functions, get_models and
  destroy (#89)
* Added Monitor class to Connection. (#105)
* Support placement lists (#103)
* Include resources from store when deploying (#102)
* Allow underscore to dash translation when accessing model
  attributes (#101)
* Added controller to ssh fix. (#100)
* Regen schema to pick up missing APIs
* Improve error handling
* Fix issue where we do not check to make sure that we are receiving the
  correct response.
* Retry calls to charmstore and increase timeout to 5s
* Make connect_model and deploy a bit more friendly
* Fix model name not including user
* Implement Model.get_status
* Add integration tests.

0.3.0
^^^^^
Mon Feb 27 2017

* Fix docstrings for placement directives.
* Implement Model.add_machine()
* Bug fix - "to" parameter to Model.deploy() was broken
* Add docs and examples for adding machines and containers and deploying
  charms to them.
* Make Machine.destroy() block the current coroutine, returning only after
  the machine is actually removed from the remote model. This is more
  consistent with the way the other apis work (e.g. Model.deploy(),
  Application.add_unit(), etc).
* Raise NotImplementedError in all unimplemented method stubs instead of
  silently passing.

0.2.0
^^^^^
Thu Feb 16 2017

* Add default ssh key to newly created model.
* Add loop helpers and simplify examples/deploy.py
* Add support for deploying local charms, and bundles containing local charm paths.
* Add ability to get cloud name for controller.
* Bug fix - fix wrong api used in Model.destroy_unit()
* Add error detection in bundle deploy.

0.1.2
^^^^^
Thu Dec 22 2016

* Bug fix - Include docs in package

0.1.1
^^^^^
Thu Dec 22 2016

* Bug fix - Include VERSION file in package

0.1.0
^^^^^
Wed Dec 21 2016

* Initial Release
