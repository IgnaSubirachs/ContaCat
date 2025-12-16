from fastapi.templating import Jinja2Templates
import os

# Determine path to frontend/templates
# This file is deep in app/interface/api/templates.py
# Root is ../../../
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 3 levels to reach 'app' root, then one more to reach project root, then down to frontend
# Actually:
# c:\ERP\app\interface\api\templates.py (current)
# c:\ERP\app\interface\api (..)
# c:\ERP\app\interface (../..)
# c:\ERP\app (../../..)
# c:\ERP (../../../..)
# c:\ERP\frontend\templates
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
templates_dir = os.path.join(project_root, "frontend/templates")

templates = Jinja2Templates(directory=templates_dir, auto_reload=True)
