import re
import pandas as pd
from typing import Dict, List, Any

class StoryParser:
    def __init__(self):
        self.expected_headers = {
            "故事名称", "故事集数", "每集故事时长", "目标受众", "故事类型及基调",
            "背景设定或世界观构建", "故事概述", "故事细节", "角色简述"
        }

    def clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        return text.strip() if text else ""

    def extract_header_content(self, line: str) -> tuple[str, str]:
        """从行中提取标题和内容"""
        parts = re.split(r'[:：]', line, maxsplit=1)
        if len(parts) > 1:
            header = self.clean_text(parts[0].lstrip("-"))
            content = self.clean_text(parts[1])
            return header, content
        return "", line

    def process_episode_content(self, content: str) -> List[Dict[str, str]]:
        """处理分集内容"""
        result = []
        parts = re.split(r'==第(\d+)集==', content)
        
        for i in range(1, len(parts) - 1, 2):
            ep_num = parts[i].strip()
            ep_details = self.clean_text(parts[i + 1])
            
            # 检查是否包含角色简述
            role_split = re.split(r'角色\s*简述\s*[：:]', ep_details, maxsplit=1)
            
            result.append({
                "字段": f"第{ep_num}集",
                "内容": self.clean_text(role_split[0])
            })
            
            if len(role_split) > 1:
                result.append({
                    "字段": "角色简述",
                    "内容": self.clean_text(role_split[1])
                })
                
        return result

    def parse(self, filepath: str) -> pd.DataFrame:
        """解析故事概述文件"""
        try:
            with open(filepath, encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        # 初始化数据结构
        data = []
        current_key = None
        value_lines = []

        # 逐行处理内容
        for line in content.splitlines():
            line = self.clean_text(line)
            if not line:
                if value_lines:  # 只在已有内容时添加空行
                    value_lines.append("")
                continue

            header, content = self.extract_header_content(line)
            
            if header in self.expected_headers:
                # 保存当前字段的内容
                if current_key is not None:
                    data.append({
                        "字段": current_key,
                        "内容": "\n".join(value_lines).strip()
                    })
                # 开始新字段
                current_key = header
                value_lines = [content] if content else []
            else:
                if current_key is not None:
                    value_lines.append(line)

        # 处理最后一个字段
        if current_key is not None and value_lines:
            data.append({
                "字段": current_key,
                "内容": "\n".join(value_lines).strip()
            })

        # 处理特殊字段
        processed_data = []
        for item in data:
            if item["字段"] == "故事细节":
                processed_data.extend(self.process_episode_content(item["内容"]))
            else:
                processed_data.append(item)

        # 创建DataFrame并进行数据清理
        df = pd.DataFrame(processed_data)
        df = df.drop_duplicates()
        df = df.fillna("")  # 填充空值
        
        return df

def parse_story_overview(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = StoryParser()
    return parser.parse(filepath)