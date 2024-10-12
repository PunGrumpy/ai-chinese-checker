import os
import importlib
from glob import glob
from lib.utils import resource_path

bot_folder = resource_path("bots")
for module in glob(os.path.join(bot_folder, "*py")):
    if not module.endswith("__init__.py") and not module.endswith(
        "custom_bot_template.py"
    ):
        module_name = os.path.basename(module)[:-3]  # Remove .py extension
        importlib.import_module(f"bots.{module_name}")
