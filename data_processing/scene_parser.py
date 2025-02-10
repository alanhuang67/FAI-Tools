import re
import pandas as pd
from typing import Dict, List, Optional

class SceneParser:
    def __init__(self):
        self.section_fields = {
            "场景整体规划": {
                "场景编号": "场景编号",
                "时间": "时间",
                "地点": "地点",
                "人物": "人物",
                "场景描述": "场景描述",
                "核心事件": "核心事件",
                "情感基调": "情感基调",
                "预计时长": "时长(秒)"
            },
            "视觉设计": {
                "空间特征": "空间特征",
                "光影设计": "光影设计",
                "色彩方案": "色彩方案",
                "环境细节": "环境细节"
            },
            "氛围营造": {
                "整体氛围": "整体氛围",
                "情感渲染": "情感渲染",
                "特殊要求": "特殊要求"
            },
            "主题深化": {
                "象征设计": "象征设计",
                "隐喻层次": "隐喻层次",
                "现代议题": "现代议题",
                "人文关怀": "人文关怀"
            },
            "转场设计": {
                "前场景衔接": "前场景衔接",
                "后场景衔接": "后场景衔接"
            }
        }

    def clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def extract_time_duration(self, text: str) -> int:
        """从时长文本中提取秒数"""
        match = re.search(r'(\d+)秒?', text)
        return int(match.group(1)) if match else 0

    def parse_section(self, section_text: str, section_fields: Dict[str, str]) -> Dict[str, str]:
        """解析单个部分（如场景整体规划、视觉设计等）的内容"""
        result = {}
        lines = section_text.split('\n')
        
        for line in lines:
            line = self.clean_text(line)
            if not line or not line.startswith('-'):
                continue
                
            parts = re.split(r'[：:]', line.lstrip('- '), maxsplit=1)
            if len(parts) != 2:
                continue
                
            field_name = parts[0].strip()
            field_content = parts[1].strip()
            
            if field_name in section_fields:
                mapped_name = section_fields[field_name]
                result[mapped_name] = field_content
        
        return result

    def parse_scene_block(self, block: str) -> Dict[str, str]:
        """解析单个场景块的内容"""
        result = {}
        sections = re.split(r'==(.+?)==', block)
        
        for i in range(1, len(sections), 2):
            section_name = sections[i].strip()
            section_content = sections[i + 1].strip() if i + 1 < len(sections) else ""
            
            if section_name in self.section_fields:
                section_data = self.parse_section(
                    section_content, 
                    self.section_fields[section_name]
                )
                result.update(section_data)
        
        return result

    def parse(self, filepath: str) -> pd.DataFrame:
        """解析场景设计文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        content = re.sub(r'\r\n?', '\n', content)
        episode_blocks = re.split(r'<第(\d+)集开始>', content)[1:]
        scenes_data = []
        
        for i in range(0, len(episode_blocks), 2):
            current_episode = episode_blocks[i]
            episode_content = episode_blocks[i + 1] if i + 1 < len(episode_blocks) else ""
            
            scene_blocks = re.split(r'<<场景(\d+)开始>>', episode_content)
            
            for j in range(1, len(scene_blocks), 2):
                scene_num = scene_blocks[j]
                scene_content = scene_blocks[j + 1]
                
                scene_data = self.parse_scene_block(scene_content)
                scene_data["集数"] = current_episode
                scene_data["场景"] = f"{current_episode}.{scene_num}"
                
                if "时长(秒)" in scene_data:
                    scene_data["时长(秒)"] = self.extract_time_duration(scene_data["时长(秒)"])
                
                scenes_data.append(scene_data)

        df = pd.DataFrame(scenes_data)
        
        all_fields = ["集数", "场景"]
        for section_fields in self.section_fields.values():
            all_fields.extend(section_fields.values())
            
        for field in all_fields:
            if field not in df.columns:
                df[field] = ""
                
        df = df[all_fields]
        df = df.fillna("")
        df = df.drop_duplicates(subset=["集数", "场景"], keep="first")
        
        return df

def parse_scene_design(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = SceneParser()
    return parser.parse(filepath)