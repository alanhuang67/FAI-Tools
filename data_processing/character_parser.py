import re
import pandas as pd
from typing import Dict, List, Optional

class CharacterParser:
    def __init__(self):
        self.field_mapping = {
            "基础信息": "基础信息",
            "故事功能 & 主题关联": "故事功能 & 主题关联",
            "三大维度（内在属性）": "三大维度（内在属性）",
            "目标—冲突—转折": "目标—冲突—转折",
            "角色弧光（成长/变化）": "角色弧光（成长/变化）",
            "外貌 & 视觉符号": "外貌 & 视觉符号",
            "社会/当代议题映射（新生代扩展）": "社会/当代议题映射（新生代扩展）",
            "角色与他人/世界的关系": "角色与他人/世界的关系",
            "观众角度 & 可辨识度": "观众角度 & 可辨识度"
        }

    def format_content(self, content: str) -> str:
        """格式化内容，添加适当的标记和缩进"""
        if not content:
            return ""
            
        formatted_lines = []
        current_point = 0
        
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # 处理带有标签的行
            if re.match(r'-[^:：]+[：:]', line):
                # 提取标签和内容
                parts = re.split(r'[：:]', line.lstrip('- '), maxsplit=1)
                if len(parts) > 1:
                    formatted_lines.append(f"• {parts[0].strip()}：{parts[1].strip()}")
                else:
                    formatted_lines.append(f"• {parts[0].strip()}")
            
            # 处理已格式化的内容（带[标签]的）
            elif line.startswith('[') and ']' in line:
                formatted_lines.append(f"• {line}")
            
            # 处理普通内容行
            else:
                current_point += 1
                formatted_lines.append(f"({current_point}) {line}")
                
        return '\n'.join(formatted_lines)

    def extract_field_content(self, block: str) -> Dict[str, str]:
        """从文本块中提取字段内容"""
        results = {}
        current_field = None
        current_content = []
        
        lines = block.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配字段标题
            field_match = re.match(r'^\d+\.\s*(.+)$', line)
            if field_match:
                if current_field and current_content:
                    results[current_field] = '\n'.join(current_content).strip()
                field_name = field_match.group(1).strip()
                current_field = field_name
                current_content = []
                continue
                
            if current_field:
                current_content.append(line)
                
        # 保存最后一个字段的内容
        if current_field and current_content:
            results[current_field] = '\n'.join(current_content).strip()
            
        return results

    def parse(self, filepath: str) -> pd.DataFrame:
        """解析角色信息文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"无法读取文件 {filepath}: {str(e)}")

        # 分割角色块
        character_blocks = re.split(r'==角色编号\d+==', content)
        character_numbers = re.findall(r'==角色编号(\d+)==', content)
        
        data = []
        for i, block in enumerate(character_blocks[1:], 1):
            if not block.strip():
                continue
                
            character_data = self.extract_field_content(block)
            
            # 添加角色编号
            character_number = character_numbers[i-1] if i <= len(character_numbers) else str(i)
            row_data = {"角色编号": f"角色{character_number}"}
            
            # 处理每个字段并格式化内容
            for field, content in character_data.items():
                if field in self.field_mapping:
                    row_data[self.field_mapping[field]] = self.format_content(content)
                    
            data.append(row_data)

        # 创建DataFrame并设置列顺序
        df = pd.DataFrame(data)
        columns = ["角色编号"] + list(self.field_mapping.values())
        for col in columns:
            if col not in df.columns:
                df[col] = ""
                
        df = df[columns]
        df = df.fillna("")
        df = df.drop_duplicates()
        
        return df

def parse_character_info(filepath: str) -> pd.DataFrame:
    """主解析函数"""
    parser = CharacterParser()
    return parser.parse(filepath)