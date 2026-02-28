# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [${version}]
### Added - for new features
### Changed - for changes in existing functionality
### Deprecated - for soon-to-be removed features
### Removed - for now removed features
### Fixed - for any bug fixes
### Security - in case of vulnerabilities
[${version}]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v${version}
-->

## [Unreleased]

### Added

- Added `is_anonymous`, `is_active`, and `is_superuser` as built-in user attribute permission checks, joining the existing `is_authenticated` and `is_staff`.

## [0.14.0]

### Added

- Added `append_slash` option to `NavItem` for per-item control over trailing slash behavior.
- `NavItem` and `NavGroup` can now render themselves via `render(request)`, enabling `{{ item }}` in templates — similar to how Django forms support `{{ form }}`. Each item can have its own `template_name` for per-item rendering customization.
- Added `NavItemContext`, a dict subclass returned by `Nav.get_context_data()`. It supports both dict-style access (`{{ item.title }}`) and self-rendering (`{{ item }}`), so existing templates work unchanged.
- Default templates `django_simple_nav/navitem.html` and `django_simple_nav/navgroup.html` ship with the package for use with the self-rendering feature. These are minimal, semantic HTML with `aria-current="page"` for active links.
- Support for Python 3.14.
- Support for Django 6.0.

### Removed

- Dropped support for Python 3.9.
- Removed `docs`, `tests`, and `types` optional dependency groups (e.g. `pip install django-simple-nav[tests]`). These are now internal development dependencies only.

## [0.13.0]

### Added

- Support for the `django.templates.backends.jinja2.Jinja2` template engine backend.
- Support for Django 5.2.

### Removed

- Dropped support for Django 5.0.

### New Contributors

- HiPhish [@hiphish](https://github.com/hiphish) ([#170](https://github.com/joshuadavidthomas/django-simple-nav/pull/170))

## [0.12.0]

### Changed

- Bumped `django-twc-package` template to v2024.29.
- Switched project and dependency management over to use `uv` across the board (`pyproject.toml`, `Justfile` recipes, GHA workflows).

### Removed

- Dropped support for Python 3.8.

## [0.11.0]

### Fixed

- Checking whether a `NavItem` or `NavGroup` is active now takes into account the URL scheme and domain name for both the nav item and request.

## [0.10.0]

### Added

- Support for Python 3.13.

### Changed

- Bumped `django-twc-package` template to v2024.23.
- Removed `westerveltco/setup-ci-action` from GitHub Actions workflows.

## [0.9.0]

### Changed

- Updated `NavItem.get_active` to allow for using URLs that contain query strings.

## [0.8.0]

### Changed

- Updated `NavItem.url` and `NavItem.get_url` to allow for using a callable. This allows `NavItem.url` to support `django.urls.reverse` or `django.urls.reverse_lazy` primarily, but it can be any callable as long as it returns a string.

## [0.7.0]

### Added

- `NavItem` and `NavGroup` now both have a `get_context_data` that returns the context needed for template rendering.
- `NavItem` and `NavGroup` now both have a `get_url` method for returning the URL for the item.
- `NavItem` and `NavGroup` now both have a `get_active` method for returning whether the item is active or not, meaning it's the URL currently being requested.
- `NavItem` and `NavGroup` now both have a `check_permissions` method for checking whether the item should be rendered for a given request.
- `NavItem` and `NavGroup` now support using a callable in the list of `permissions`. This callable should take an `HttpRequest` and return a `bool` indicating whether the item should be rendered for a given request.
- The `Nav` class now has a `get_template` method that returns the template to render. This method takes an optional `template_name` argument, and if not provided is taken from the `get_template_name` method. If overridden, you can return a string as a way to embed a template directly in the `Nav` definition.
- `NavItem` now has a `get_items` method. This is to aid a future refactor.

### Changed

- Internals of library have been refactored to slightly simplify it, including `Nav`, `NavGroup`, `NavItem` and the `django_simple_nav` templatetag.
- `Nav.get_items` now returns a list of `NavGroup` or `NavItem`, instead of a list of `RenderedNavItem`.
- Check for the existence of a user attached to the `request` object passed in to `django_simple_nav.permissions.check_item_permissions` has been moved to allow for an early return if there is no user. There are instances where the `django.contrib.auth` app can be installed, but no user is attached to the request object. This change will allow this function to correctly be used in those instances.
- Now using v2024.20 of `django-twc-package`.
- `NavGroup` is now marked as active if the request path matches it's URL (if set) **or** and of its items' URLs.

### Removed

- The `extra_context` attribute of `NavItem` and `NavGroup` now only renders the contents of the dictionary to the template context. Previously it did that as well as provided `extra_context` to the context. If this sounds confusing, that's because it kinda is. 😅 This basically just means instead of two places to get the extra context (`extra_context` and the keys provided within the `extra_context` attribute), there is now just one (the keys provided within the `extra_context` attribute).
- `RenderedNavItem` has been removed and it's functionality refactored into both `NavItem` and `NavGroup`. This should not affect the public API of this library, but I thought it should be noted.
- `django_simple_nav.permissions` module has been removed and it's functionality refactored into `NavItem`.
- Dropped support for Django 3.2.

### Fixed

- `active` boolean for a `NavItem` should now accurately match the request URL, taking into account any potential nesting and a project's `APPEND_SLASH` setting.
- The permissions check for `NavGroup` has been fixed to apply to the child items as well. Previously, it only checked the top-level permissions on the `NavGroup` instance itself. If the items within the `NavGroup` have permissions defined, they will now be checked and filtered out. If the check ends up filtering all of the items out and the `NavGroup` has no url set, then it will not be rendered.

## [0.6.0]

### Added

- Added two new methods to `Nav`: `get_items` and `get_template_name`. These should allow for further flexibility and customization of rendering the `Nav`.

### Changed

- Now using v2024.16 of `django-twc-package`.

### Fixed

- Active nav item matching is now correctly using the `url` property on `RenderedNavItem`.

## [0.5.1]

### Added

- Added the requisite `py.typed` file to the package, so that it plays nicely when type-checking in projects using `django-simple-nav`.

## [0.5.0]

### Added

- An number of examples have been added to a new `example` directory. These examples are intended to demonstrate various ways how to use `django-simple-nav` in a Django project and include basic usage and usage with some popular CSS frameworks.

### Changed

- `check_item_permission` now takes a `request` argument instead of a `user` argument.

### Fixed

- `check_item_permission` now explicitly checks if `django.contrib.auth` is installed before attempting to check if a user has a permission. If it is not, it will return `True` by default and log a warning.
- The `request` object is now passed to `render_to_string` when rendering the navigation template, so that the `request` object is available in the template context. This allows for nesting the `django_simple_nav` template tag within another `django_simple_nav` template tag, and having the `request` object available in the nested template.

## [0.4.0]

### Added

- The `Nav` class now has two new methods: `get_context_data` and `render`. These methods are used to render the navigation to a template. These new methods give greater flexibility for customizing the rendering of the navigation, as they can be overridden when defining a new `Nav`.
  - `Nav.get_context_data` method takes a Django `HttpRequest` object and returns a dictionary of context data that can be used to render the navigation to a template.
  - `Nav.render` method takes a Django `HttpRequest` object and an optional template name and renders the navigation to a template, returning the rendered template as a string.

### Removed

- `Nav.render_from_request` method has been removed. This was only used within the template tag to render a `Nav` template from an `HttpRequest` object. It has been removed in favor of the new `Nav.get_context_data` and `Nav.render` methods.

## [0.3.0]

### Added

- `NavGroup` and `NavItem` now has a new `extra_context` attribute. This allows for passing additional context to the template when rendering the navigation, either via the extra attribute (`item.foo`) or the `extra_context` attribute itself (`item.extra_context.foo`).

### Changed

- Now using v2024.13 of `django-twc-package`.

### Fixed

- `RenderedNavItem.items` property now correctly returns a list of `RenderedNavItem` objects, rather than a list of `NavItem` objects. This fixes a bug where the properties that should be available (e.g. `active`, `url`, etc.) were not available when iterating over the `RenderedNavItem.items` list if the item was a `NavGroup` object with child items.

## [0.2.0]

### Added

- The `django_simple_nav` template tag can now take an instance of a `Nav` class, in addition to a `Nav` dotted path string. This should give greater flexibility for rendering a `Nav`, as it can now be overridden on a per-view/template basis.

### Changed

- Now using [`django-twc-package`](https://github.com/westerveltco/django-twc-package) template for repository and package structure.

## [0.1.0]

Initial release! 🎉

### Added

- A group of navigation classes -- `Nav`, `NavGroup`, and `NavItem` -- that can be used together to build a simple navigation structure.
  - `Nav` is the main container for a navigation structure.
  - `NavGroup` is a container for a group of `NavItem` objects.
  - `NavItem` is a single navigation item.
- A `django_simple_nav` template tag that renders a `Nav` object to a template. The template tag takes a string represented the dotted path to a `Nav` object and renders it to the template.
- Navigation item urls can be either a URL string (e.g. `https://example.com/about/` or `/about/`) or a Django URL name (e.g. `about-view`). When rendering out to the template, the template tag will resolve the URL name to the actual URL.
- Navigation items also can take a list of permissions to control the visibility of the item. The permissions can be user attributes (e.g. `is_staff`, `is_superuser`, etc.) or a specific permission (e.g. `auth.add_user`).
- Navigation items are marked as `active` if the current request path matches the item's URL. This is can be useful for highlighting the current page in the navigation.
- A `Nav` object's template can either be set as a class attribute (`template_name`) or passed in as a keyword argument when rendering the template tag. This allows for easy customization of the navigation structure on a per-template or per-view basis.
- Initial documentation.
- Initial tests.
- Initial CI/CD (GitHub Actions).

### New Contributors

- Josh Thomas <josh@joshthomas.dev> (maintainer)
- Jeff Triplett [@jefftriplett](https://github.com/jefftriplett)

[unreleased]: https://github.com/joshuadavidthomas/django-simple-nav/compare/v0.14.0...HEAD
[0.1.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.1.0
[0.2.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.2.0
[0.3.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.3.0
[0.4.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.4.0
[0.5.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.5.0
[0.5.1]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.5.1
[0.6.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.6.0
[0.7.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.7.0
[0.8.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.8.0
[0.9.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.9.0
[0.10.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.10.0
[0.11.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.11.0
[0.12.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.12.0
[0.13.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.13.0
[0.14.0]: https://github.com/joshuadavidthomas/django-simple-nav/releases/tag/v0.14.0
