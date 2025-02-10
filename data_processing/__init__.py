# __init__.py

# 该模块导入子模块的解析功能，方便在 main.py 中统一调用
from .character_parser import parse_character_info
from .story_parser import parse_story_overview
from .scene_parser import parse_scene_design
from .shot_parser import parse_shot_script