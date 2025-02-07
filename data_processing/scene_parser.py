import re
import pandas as pd
from typing import Dict, List, Optional

class SceneParser:
    def __init__(self):
        self.FIELD_MAPPING = {
            "名称": "名称",
            "时长": "时长(秒)",
            "时间&地点": "时间&地点",
            "场景功能": "场景功能",
            "角色动机": "角色动机",
            "冲突&转折": "冲突&转折",
            "氛围与视觉": "氛围与视觉",
            "后续衔接": "后续衔接",
            "剧情过程": "剧情过程",
            "对白要点": "对白要点",
            "情绪节点": "情绪节点",
            "动作/分镜提示": "动作/分镜提示"
        }

    def extract_content_between_fields(self, text: str, field_names: List[str]) -> Dict[str, str]:
        """在已知字段之间提取内容"""
        result = {}
        field_pattern = '|'.join(map(re.escape, field_names))
        
        # 将文本按字段名分割
        parts = re.split(f'-\\s*({field_pattern})[：:](.*?)(?=-\\s*(?:{field_pattern})[：:]|$)', text, flags=re.DOTALL)
        
        current_field = None
        current_content = []
        
        for part in parts:
            if not part.strip():
                continue
            
            # 检查是否是字段名
            if part.strip() in field_names:
                if current_field:
                    result[current_field] = '\n'.join(current_content).strip()
                current_field = part.strip()
                current_content = []
            else:
                current_content.append(part.strip())
        
        # 处理最后一个字段
        if current_field:
            result[current_field] = '\n'.join(current_content).strip()
            
        return result

    def process_scene_block(self, block: str) -> Dict:
        """处理单个场景块"""
        # 移除场景概览和剧情设计标记
        block = re.sub(r'===场景概览===|===剧情设计===', '', block)
        
        # 提取所有字段内容
        field_names = list(self.FIELD_MAPPING.keys())
        contents = self.extract_content_between_fields(block, field_names)
        
        # 转换字段名
        return {self.FIELD_MAPPING[k]: v for k, v in contents.items() if k in self.FIELD_MAPPING}

    def parse_file(self, filepath: str) -> pd.DataFrame:
        """解析文件并返回DataFrame"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 清理文本
        content = re.sub(r'\r\n?', '\n', content)
        
        # 提取场景块
        scene_blocks = re.split(r'==场景\d+\.\d+(?:开始|结束)==', content)
        scene_numbers = re.findall(r'==场景(\d+\.\d+)(?:开始|结束)==', content)
        
        # 提取集数
        episode_matches = re.finditer(r'<第(\d+)集开始>', content)
        episode_positions = [(m.group(1), m.start()) for m in episode_matches]
        
        scenes_data = []
        current_episode = "1"
        
        # 处理每个场景块
        for block, scene_num in zip(scene_blocks[1:], scene_numbers):
            # 更新当前集数
            for ep_num, pos in episode_positions:
                if pos < content.find(f"==场景{scene_num}"):
                    current_episode = ep_num
            
            # 处理场景数据
            scene_data = self.process_scene_block(block)
            scene_data["集数"] = current_episode
            scene_data["场景"] = scene_num
            
            # 仅添加非空场景
            if any(scene_data.values()):
                scenes_data.append(scene_data)
        
        # 创建DataFrame
        df = pd.DataFrame(scenes_data)
        
        # 确保所有列都存在并按正确顺序排列
        columns = ["集数", "场景"] + list(self.FIELD_MAPPING.values())
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
        
        # 处理时长列
        df["时长(秒)"] = df["时长(秒)"].apply(lambda x: int(re.search(r'(\d+)', str(x)).group(1)) if isinstance(x, str) and re.search(r'(\d+)', str(x)) else 0)
        
        # 清理并移除重复行
        df = df.drop_duplicates(subset=["集数", "场景"], keep="first")
        
        return df

def parse_scene_design(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = SceneParser()
    return parser.parse_file(filepath)