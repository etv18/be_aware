import os
import importlib

models_directory = os.path.dirname(__file__)

for filename in os.listdir(models_directory):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = f'app.models.{filename[:-3]}'
        importlib.import_module(module_name)