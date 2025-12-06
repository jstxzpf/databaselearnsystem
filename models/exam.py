"""
考试模型
"""
import json
import uuid
from datetime import datetime, timezone
from flask import current_app

class ExamModel:
    """考试模型管理类"""
    
    def __init__(self):
        self.config_data = None
        self.load_test_config()
    
    def load_test_config(self):
        """加载考试配置"""
        try:
            # 尝试从应用配置获取文件路径，如果失败则使用默认路径
            try:
                file_path = current_app.config['TEST_MODEL_FILE']
            except RuntimeError:
                # 应用上下文不可用时使用默认路径
                file_path = 'testmodel.json'

            with open(file_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)

            # 安全地记录日志
            try:
                current_app.logger.info("考试配置加载成功")
            except RuntimeError:
                print("考试配置加载成功")

        except FileNotFoundError:
            try:
                current_app.logger.error(f"考试配置文件未找到: {file_path}")
            except (RuntimeError, NameError):
                print(f"考试配置文件未找到: testmodel.json")
            self.config_data = {"考试信息": {"题型列表": []}}
        except json.JSONDecodeError as e:
            try:
                current_app.logger.error(f"考试配置JSON解析错误: {e}")
            except RuntimeError:
                print(f"考试配置JSON解析错误: {e}")
            self.config_data = {"考试信息": {"题型列表": []}}
    
    def get_exam_info(self):
        """获取考试基本信息"""
        return self.config_data.get("考试信息", {})
    
    def get_question_types(self):
        """获取题型列表"""
        exam_info = self.get_exam_info()
        return exam_info.get("题型列表", [])
    
    def get_question_type_by_name(self, type_name):
        """根据名称获取题型配置"""
        question_types = self.get_question_types()
        for q_type in question_types:
            if q_type.get("题型名称") == type_name:
                return q_type
        return None
    
    def generate_exam_paper(self, selected_chapters, selected_types=None):
        """生成试卷"""
        if selected_types is None:
            selected_types = [qt["题型名称"] for qt in self.get_question_types()]
        
        exam_paper = {
            'id': str(uuid.uuid4()),
            'created_at': datetime.now(timezone.utc).isoformat(),
            'chapters': selected_chapters,
            'question_types': selected_types,
            'questions': []
        }
        
        # 为每种题型生成题目配置
        for type_name in selected_types:
            q_type = self.get_question_type_by_name(type_name)
            if q_type:
                question_section = {
                    'type_name': type_name,
                    'count': q_type.get('题量', 1),
                    'total_score': q_type.get('总分', 10),
                    'focus': q_type.get('考查重点', ''),
                    'scope': q_type.get('内容范围', ''),
                    'requirements': q_type.get('答题要求', ''),
                    'questions': []
                }
                exam_paper['questions'].append(question_section)
        
        return exam_paper
    
    def format_exam_paper(self, exam_paper, generated_questions=None):
        """格式化试卷为文本"""
        lines = []
        lines.append("通用学习系统考试试卷")
        lines.append("=" * 50)
        lines.append(f"考试时间: {datetime.now().strftime('%Y年%m月%d日')}")
        lines.append(f"考试章节: {', '.join(exam_paper['chapters'])}")
        lines.append("")
        
        total_score = 0
        question_num = 1
        
        all_answers = []  # 收集所有答案
        
        for i, section in enumerate(exam_paper['questions']):
            lines.append(f"{section['type_name']} (共{section['count']}题，{section['total_score']}分)")
            lines.append(f"考查重点: {section['focus']}")
            if section.get('requirements'):
                lines.append(f"答题要求: {section['requirements']}")
            lines.append("")
            
            section_answers = []
            
            # 如果有生成的题目，使用生成的题目
            if generated_questions and i < len(generated_questions):
                questions = generated_questions[i]
                for q in questions:
                    if isinstance(q, dict):
                        # 结构化题目
                        lines.append(f"{question_num}. {q.get('content', '')}")
                        
                        # 选项
                        if q.get('options'):
                            for opt in q['options']:
                                lines.append(f"    {opt}")
                        
                        lines.append("")
                        
                        # 收集答案
                        ans = q.get('answer', '无答案')
                        analysis = q.get('analysis', '')
                        section_answers.append(f"{question_num}. {ans}\n   解析: {analysis}")
                        
                    else:
                        # 旧文本格式
                        lines.append(f"{question_num}. {q}")
                        lines.append("")
                        section_answers.append(f"{question_num}. (见题目描述)")
                        
                    question_num += 1
            else:
                # 否则显示占位符
                for j in range(section['count']):
                    lines.append(f"{question_num}. [待生成题目]")
                    lines.append("")
                    question_num += 1
            
            all_answers.append((section['type_name'], section_answers))
            
            total_score += section['total_score']
            lines.append("")
        
        lines.append(f"总分: {total_score}分")
        lines.append("=" * 50)
        lines.append("")
        lines.append("参考答案")
        lines.append("-" * 30)
        
        for section_name, answers in all_answers:
            if answers:
                lines.append(f"【{section_name}】")
                for ans in answers:
                    lines.append(ans)
                lines.append("")
        
        return "\n".join(lines)
