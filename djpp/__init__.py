import pkg_resources
# from . import checks  # noqa: Register the checks

__version__ = pkg_resources.require("djpp")[0].version
default_app_config = 'djpp.apps.DjppConfig'
