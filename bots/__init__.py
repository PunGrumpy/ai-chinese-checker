import importlib
from glob import glob

for module in glob("bots/*py"):
    if not module.endswith("__init__.py") and not module.endswith(
        "custom_bot_template.py"
    ):
        importlib.import_module(
            module.replace("/", ".").replace("\\", ".").removesuffix(".py")
        )
