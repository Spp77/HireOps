# config/settings/__init__.py
# Auto-selects settings module based on ENV variable.
# Set ENV=production in your server environment.

import os

_env = os.environ.get("ENV", "development").lower()

if _env == "production":
    from .production import *          # noqa: F401, F403
elif _env == "test":
    from .test import *                # noqa: F401, F403
else:
    from .development import *         # noqa: F401, F403
