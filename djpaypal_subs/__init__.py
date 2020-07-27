import pkg_resources
# from . import checks  # noqa: Register the checks

__version__ = pkg_resources.require("djpaypal_subs")[0].version
default_app_config = 'djpaypal_subs.apps.DjPaypalSubsConfig'
