import re
import pandas as pd
from typing import Dict, List, Optional

class ShotParser:
    def __init__(self):
        # 优化字段映射，确保与期望输出完全匹配
        self.column_mapping = {
            "集号": "集号",
            "场景编号": "场景编号",
            "分镜编号": "分镜编号",
            "画面详细描述": "画面详细描述",
            "镜头运动": "镜头运动",
            "镜头时长": "镜头时长",
            "机位": "机位",
            "景别": "景别",
            "音效": "音效",
            "光影/色调/氛围": "光影/色调/氛围",
            "角色动作表情": "角色动作表情",
            "对白/旁白": "对白/旁白"
        }

        # 定义输出列的顺序
        self.column_order = [
            "集号", "场景编号", "分镜编号", "画面详细描述", 
            "镜头运动", "镜头时长", "机位", "景别", "音效",
            "光影/色调/氛围", "角色动作表情", "对白/旁白"
        ]

    def clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def format_field_content(self, field: str, content: str) -> str:
        """格式化字段内容"""
        content = self.clean_text(content)
        if not content:
            return ""
        
        # 处理特殊字段的格式化
        if field == "镜头时长":
            match = re.search(r'(\d+)秒?', content)
            return match.group(1) if match else ""
            
        return content

    def parse_field_content(self, content: str) -> Dict[str, str]:
        """解析分镜内容的各个字段"""
        fields = {}
        current_field = None
        current_content = []

        for line in content.split('\n'):
            line = self.clean_text(line)
            if not line:
                continue

            # 处理字段标记行
            if line.startswith('-'):
                # 保存前一个字段的内容
                if current_field:
                    field_name = self.normalize_field_name(current_field)
                    if field_name:
                        fields[field_name] = self.format_field_content(
                            field_name, '\n'.join(current_content)
                        )

                # 提取新字段
                parts = re.split(r'[：:]', line.lstrip('- '), maxsplit=1)
                if len(parts) > 1:
                    current_field = parts[0].strip()
                    current_content = [parts[1].strip()]
                else:
                    current_field = parts[0].strip()
                    current_content = []
            elif current_field:
                current_content.append(line)

        # 保存最后一个字段的内容
        if current_field:
            field_name = self.normalize_field_name(current_field)
            if field_name:
                fields[field_name] = self.format_field_content(
                    field_name, '\n'.join(current_content)
                )

        return fields

    def normalize_field_name(self, field: str) -> Optional[str]:
        """标准化字段名称"""
        field = self.clean_text(field)
        # 直接匹配
        if field in self.column_mapping:
            return self.column_mapping[field]
        # 模糊匹配
        for standard_name in self.column_mapping:
            if field.replace(' ', '') in standard_name.replace(' ', ''):
                return self.column_mapping[standard_name]
        return None

    def parse_shot_block(self, content: str, episode: str, scene: str, shot: str) -> Dict:
        """解析单个分镜块"""
        # 基础信息
        shot_data = {
            "集号": episode,
            "场景编号": scene,
            "分镜编号": shot
        }

        # 解析字段内容
        field_data = self.parse_field_content(content)
        shot_data.update(field_data)

        return shot_data

    def parse_file(self, filepath: str) -> pd.DataFrame:
        """解析分镜脚本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        shots_data = []
        current_episode = None
        current_scene = None

        # 分割内容块
        blocks = re.split(r'(<=第\d+集=>|<==场景[\d\.]+===>|<===分镜[\d\.]+===>)', content)
        
        for i in range(1, len(blocks), 2):
            block_header = blocks[i]
            block_content = blocks[i + 1] if i + 1 < len(blocks) else ""

            # 处理集号
            ep_match = re.match(r'<=第(\d+)集=>', block_header)
            if ep_match:
                current_episode = ep_match.group(1)
                continue

            # 处理场景编号
            scene_match = re.match(r'<==场景([\d\.]+)==>', block_header)
            if scene_match:
                current_scene = scene_match.group(1)
                continue

            # 处理分镜
            shot_match = re.match(r'<===分镜([\d\.]+)===>',  block_header)
            if shot_match and block_content:
                shot_num = shot_match.group(1)
                shot_data = self.parse_shot_block(
                    block_content, current_episode, current_scene, shot_num
                )
                shots_data.append(shot_data)

        # 创建DataFrame
        df = pd.DataFrame(shots_data)
        
        # 确保所有列都存在
        for col in self.column_order:
            if col not in df.columns:
                df[col] = ""

        # 按预定义顺序排列列
        df = df[self.column_order]
        
        # 清理数据
        df = df.fillna("")
        df = df.drop_duplicates()
        
        return df

def parse_shot_script(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = ShotParser()
    return parser.parse_file(filepath)