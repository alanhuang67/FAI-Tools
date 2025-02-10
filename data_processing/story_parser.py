import re
import pandas as pd
from typing import Dict, List, Any, Optional

class StoryParser:
    def __init__(self):
        self.expected_headers = {
            "故事名称", "故事集数", "每集故事时长", "目标受众", "故事类型及基调",
            "背景设定或世界观构建", "故事概述", "故事细节", "角色简述"
        }
        self.required_fields = {"故事名称", "故事集数", "故事概述"}

    def clean_text(self, text: str) -> str:
        """清理和标准化文本"""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def extract_header_content(self, line: str) -> tuple[str, str]:
        """从行中提取标题和内容"""
        parts = re.split(r'[:：]', line, maxsplit=1)
        if len(parts) > 1:
            header = self.clean_text(parts[0].lstrip("-"))
            content = self.clean_text(parts[1])
            return header, content
        return "", line

    def validate_episode_numbers(self, episodes: List[str]) -> bool:
        """验证集数的连续性"""
        try:
            numbers = [int(re.search(r'\d+', ep).group()) 
                      for ep in episodes if re.search(r'\d+', ep)]
            if not numbers:
                return False
            expected = list(range(1, len(numbers) + 1))
            return numbers == expected
        except Exception:
            return False

    def validate_content(self, df: pd.DataFrame) -> bool:
        """验证关键内容是否存在且非空"""
        if df.empty:
            return False
        
        # 检查必需字段是否存在
        fields_present = set(df["字段"].values)
        if not self.required_fields.issubset(fields_present):
            return False

        # 检查必需字段是否有内容
        for field in self.required_fields:
            content = df[df["字段"] == field]["内容"].iloc[0]
            if not content or content.isspace():
                return False

        return True

    def extract_episode_count(self, df: pd.DataFrame) -> Optional[int]:
        """从故事集数字段提取集数"""
        try:
            episode_row = df[df["字段"] == "故事集数"]
            if episode_row.empty:
                return None
            content = episode_row.iloc[0]["内容"]
            match = re.search(r'(\d+)集', content)
            return int(match.group(1)) if match else None
        except Exception:
            return None

    def process_episode_content(self, content: str, expected_episodes: Optional[int] = None) -> List[Dict[str, str]]:
        """处理分集内容"""
        result = []
        if not content:
            return result

        parts = re.split(r'==第(\d+)集==', content)
        if len(parts) < 3:  # 至少需要有一集内容
            return result
        
        for i in range(1, len(parts) - 1, 2):
            ep_num = parts[i].strip()
            ep_details = self.clean_text(parts[i + 1])
            
            if not ep_details:  # 跳过空的集数内容
                continue
                
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

        # 验证集数
        if expected_episodes is not None:
            episode_count = len([item for item in result if item["字段"].startswith("第")])
            if episode_count != expected_episodes:
                raise ValueError(f"预期集数 {expected_episodes} 与实际集数 {episode_count} 不匹配")

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

        # 创建初始 DataFrame
        df = pd.DataFrame(data)
        
        # 提取预期集数
        expected_episodes = self.extract_episode_count(df)

        # 处理特殊字段
        processed_data = []
        for item in data:
            if item["字段"] == "故事细节":
                processed_data.extend(
                    self.process_episode_content(
                        item["内容"], 
                        expected_episodes
                    )
                )
            else:
                processed_data.append(item)

        # 创建最终 DataFrame
        final_df = pd.DataFrame(processed_data)
        
        # 验证数据完整性
        if not self.validate_content(final_df):
            raise ValueError("故事内容不完整或关键字段缺失")

        # 数据清理
        final_df = final_df.drop_duplicates()
        final_df = final_df.fillna("")
        
        return final_df

def parse_story_overview(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = StoryParser()
    return parser.parse(filepath)