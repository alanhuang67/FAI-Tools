import re
import pandas as pd
from typing import Dict, List, Optional

class ShotParser:
    def __init__(self):
        self.expected_columns = [
            "集号",
            "场景编号", 
            "分镜编号",
            "景别",
            "镜头时长(秒)",
            "对白/旁白",
            "画面详细描述"
        ]

        self.field_mapping = {
            "集数": "集号",
            "场景编号": "场景编号",
            "分镜编号": "分镜编号",
            "景别": "景别",
            "分镜时长": "镜头时长(秒)",
            "对白或旁白": "对白/旁白",
            "分镜详细描述": "画面详细描述"
        }

    def clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        if not text:
            return ""
        return text.strip()

    def extract_time_duration(self, text: str) -> str:
        """从时长文本中提取秒数"""
        match = re.search(r'(\d+)秒?', text)
        return str(match.group(1)) if match else "0"

    def parse_shot_block(self, block: str) -> Dict[str, str]:
        """解析单个分镜块"""
        shot_data = {col: "" for col in self.expected_columns}
        current_field = None
        current_content = []
        
        lines = block.split('\n')
        i = 0
        while i < len(lines):
            line = self.clean_text(lines[i])
            if not line or line.startswith('====='):
                i += 1
                continue

            # 处理字段标记
            if line.startswith('='):
                # 如果之前在收集内容，先保存
                if current_field and current_content:
                    if current_field == "分镜详细描述":
                        shot_data["画面详细描述"] = '\n'.join(current_content)
                    elif current_field == "对白或旁白":
                        shot_data["对白/旁白"] = '\n'.join(current_content)
                    current_content = []

                # 处理新字段
                line = line[1:]  # 移除开头的=
                parts = re.split(r'[:：]', line, maxsplit=1)
                field_name = parts[0].strip()
                
                if field_name in self.field_mapping:
                    current_field = field_name
                    mapped_name = self.field_mapping[field_name]
                    
                    # 如果字段有值，直接保存
                    if len(parts) > 1 and parts[1].strip():
                        if mapped_name == "镜头时长(秒)":
                            shot_data[mapped_name] = self.extract_time_duration(parts[1])
                        else:
                            shot_data[mapped_name] = parts[1].strip()
                    i += 1
                    
                    # 如果是需要收集多行内容的字段，开始收集后续行
                    while i < len(lines):
                        next_line = self.clean_text(lines[i])
                        if not next_line or next_line.startswith('='):
                            break
                        current_content.append(next_line)
                        i += 1
                    continue
            i += 1

        # 保存最后一个字段的内容
        if current_field and current_content:
            if current_field == "分镜详细描述":
                shot_data["画面详细描述"] = '\n'.join(current_content)
            elif current_field == "对白或旁白":
                shot_data["对白/旁白"] = '\n'.join(current_content)

        return shot_data

    def parse(self, filepath: str) -> pd.DataFrame:
        """解析分镜脚本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        shot_blocks = re.split(r'=====分镜(?:开始|结束)=====', content)
        shot_blocks = [block.strip() for block in shot_blocks if block.strip()]
        
        shots_data = []
        for block in shot_blocks:
            shot_data = self.parse_shot_block(block)
            if any(shot_data.values()):
                shots_data.append(shot_data)

        df = pd.DataFrame(shots_data)
        
        for col in self.expected_columns:
            if col not in df.columns:
                df[col] = ""
        
        df = df[self.expected_columns]
        df = df.fillna("")
        df = df.drop_duplicates()
        
        return df

def parse_shot_script(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = ShotParser()
    return parser.parse(filepath)