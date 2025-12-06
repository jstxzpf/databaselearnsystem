"""
课程模型
"""
import os
import json
import glob
from datetime import datetime, timezone
from flask import current_app

class Course:
    """课程模型"""
    
    def __init__(self, name=None, description=None, filename=None, created_at=None):
        self.name = name
        self.description = description
        self.filename = filename
        self.created_at = created_at or datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<Course {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'filename': self.filename,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_all_courses():
        """获取所有课程"""
        courses = []
        
        # 添加默认的数据库课程
        if os.path.exists('kownlgebase.json'):
            courses.append(Course(
                name='数据库原理',
                description='数据库系统基础理论与应用',
                filename='kownlgebase.json',
                created_at=datetime.now(timezone.utc)
            ))
        
        # 扫描其他课程文件
        course_files = glob.glob('course_*.json')
        for file_path in course_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    course_name = data.get('科目', os.path.basename(file_path).replace('course_', '').replace('.json', ''))
                    courses.append(Course(
                        name=course_name,
                        description=f'{course_name}课程',
                        filename=file_path,
                        created_at=datetime.now(timezone.utc)
                    ))
            except Exception as e:
                print(f"加载课程文件 {file_path} 失败: {e}")
                continue
        
        return courses
    
    @staticmethod
    def get_course_by_name(name):
        """根据名称获取课程"""
        courses = Course.get_all_courses()
        for course in courses:
            if course.name == name:
                return course
        return None
    
    @staticmethod
    def create_course(name, description, knowledge_data):
        """创建新课程"""
        try:
            # 生成文件名
            safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            filename = f'course_{safe_name}.json'
            
            # 确保知识库数据格式正确
            if not isinstance(knowledge_data, dict) or '科目' not in knowledge_data:
                knowledge_data = {
                    '科目': name,
                    '章节': knowledge_data.get('章节', {}) if isinstance(knowledge_data, dict) else {}
                }
            
            # 保存到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
            
            return Course(
                name=name,
                description=description,
                filename=filename,
                created_at=datetime.now(timezone.utc)
            )
        except Exception as e:
            raise Exception(f"创建课程失败: {str(e)}")
    
    @staticmethod
    def delete_course(name):
        """删除课程"""
        try:
            # 不允许删除默认的数据库课程
            if name == '数据库原理':
                raise Exception("不能删除默认的数据库原理课程")
            
            course = Course.get_course_by_name(name)
            if not course:
                raise Exception("课程不存在")
            
            # 删除文件
            if course.filename and course.filename != 'kownlgebase.json':
                if os.path.exists(course.filename):
                    os.remove(course.filename)
                    return True
            
            return False
        except Exception as e:
            raise Exception(f"删除课程失败: {str(e)}")
    
    def load_knowledge_base(self):
        """加载课程的知识库"""
        try:
            if not self.filename or not os.path.exists(self.filename):
                return None
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载知识库失败: {e}")
            return None
    
    @staticmethod
    def get_default_course():
        """获取默认课程"""
        return Course(
            name='数据库原理',
            description='数据库系统基础理论与应用',
            filename='kownlgebase.json',
            created_at=datetime.now(timezone.utc)
        )
