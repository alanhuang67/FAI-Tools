import re
import pandas as pd
from typing import Dict, List, Optional

class ScriptParser:
    def __init__(self):
        self.field_mapping = {
            "集号": "集号",
            "标题": "标题",
            "内容": "内容"
        }

    def extract_episode_content(self, content: str) -> List[Dict[str, str]]:
        """提取每集内容"""
        results = []
        
        # 分割每集内容
        episodes = re.split(r'第(\d+)集[:：]', content)[1:]  # 跳过第一个空匹配
        
        # 成对处理集号和内容
        for i in range(0, len(episodes), 2):
            if i + 1 < len(episodes):
                episode_num = episodes[i]
                episode_content = episodes[i + 1].strip()
                
                # 提取标题和内容
                title_content = episode_content.split('\n', 1)
                title = title_content[0].strip()
                content = title_content[1].strip() if len(title_content) > 1 else ""
                
                results.append({
                    "集号": f"第{episode_num}集",
                    "标题": title,
                    "内容": content
                })
        
        return results

    def parse(self, filepath: str) -> pd.DataFrame:
        """解析剧本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        # 处理内容
        episodes_data = self.extract_episode_content(content)
        
        # 创建DataFrame
        df = pd.DataFrame(episodes_data)
        
        # 确保所有列都存在
        for col in self.field_mapping.values():
            if col not in df.columns:
                df[col] = ""

        # 按预定义顺序排列列
        df = df[list(self.field_mapping.values())]
        
        # 清理数据
        df = df.fillna("")
        df = df.drop_duplicates()
        
        return df

def parse_script(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = ScriptParser()
    return parser.parse(filepath)