"""
AI服务 - 与Ollama API交互
"""
import requests
import json
import time
from flask import current_app

class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.api_url = current_app.config['OLLAMA_API_URL']
        self.model_name = current_app.config['OLLAMA_MODEL']
        self.timeout = 60  # 60秒超时
        self.max_retries = 3
    
    def _make_request(self, prompt, max_tokens=2000):
        """发送请求到Ollama API"""
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": 0.7
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                current_app.logger.info(f"发送AI请求 (尝试 {attempt + 1}/{self.max_retries})")
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'message' in result and 'content' in result['message']:
                        content = result['message']['content']
                        # 清理可能导致问题的字符
                        content = self._clean_ai_content(content)
                        # 额外的安全检查：确保没有可能导致Python执行错误的内容
                        content = self._final_safety_check(content)
                        return content
                    else:
                        current_app.logger.error(f"AI响应格式错误: {result}")
                        return "抱歉，AI服务响应格式错误。"
                else:
                    current_app.logger.error(f"AI API错误: {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                current_app.logger.warning(f"AI请求超时 (尝试 {attempt + 1})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
            except requests.exceptions.ConnectionError:
                current_app.logger.error("无法连接到Ollama服务")
                return "无法连接到AI服务，请确保Ollama服务正在运行。"
            except Exception as e:
                current_app.logger.error(f"AI请求异常: {str(e)}")
                
        return "抱歉，AI服务暂时不可用，请稍后重试。"

    def _clean_ai_content(self, content):
        """清理AI返回的内容，移除可能导致问题的字符"""
        if not content:
            return content

        try:
            # 移除零宽字符和控制字符
            content = content.replace('\u200b', '')  # 零宽空格
            content = content.replace('\u200c', '')  # 零宽非连接符
            content = content.replace('\u200d', '')  # 零宽连接符
            content = content.replace('\ufeff', '')  # 字节顺序标记

            # 统一引号
            content = content.replace('"', '"').replace('"', '"')
            content = content.replace(''', "'").replace(''', "'")

            # 移除可能的HTML标签（如果AI错误返回了HTML）
            import re
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

            # 特别处理可能导致Python执行错误的内容
            # 移除可能被误解为Python代码的内容，但避开代码块
            # 使用简单的替换策略，避免复杂的正则回溯
            dangerous_keywords = ['eval', 'exec', 'compile', '__import__']
            for keyword in dangerous_keywords:
                # 简单的替换，不尝试解析上下文，安全第一
                if f"{keyword}(" in content:
                    content = content.replace(f"{keyword}(", f"{keyword}_SAFE(")

            # 清理Mermaid图表中可能有问题的中文节点名
            # 将中文节点名替换为安全的英文标识符
            def clean_mermaid_nodes(match):
                mermaid_content = match.group(1)

                # 确保节点标签用引号包围（如果包含中文或特殊字符）
                import re

                # 处理方括号节点 [中文内容] -> ["中文内容"]
                # 排除已经被引号包围的
                mermaid_content = re.sub(r'\[(?!"|[\d\w\s]+\])([^]]*[\u4e00-\u9fff][^]]*)\]', r'["\1"]', mermaid_content)

                # 处理花括号节点 {中文内容} -> {"中文内容"}
                mermaid_content = re.sub(r'\{(?!"|[\d\w\s]+\})([^}]*[\u4e00-\u9fff][^}]*)\}', r'{"\1"}', mermaid_content)

                # 处理圆括号节点 (中文内容) -> ("中文内容")
                mermaid_content = re.sub(r'\((?!"|[\d\w\s]+\))([^)]*[\u4e00-\u9fff][^)]*)\)', r'("\1")', mermaid_content)

                return f'```mermaid\n{mermaid_content}\n```'

            content = re.sub(r'```mermaid\n(.*?)\n```', clean_mermaid_nodes, content, flags=re.DOTALL)

            return content.strip()

        except Exception as e:
            current_app.logger.warning(f"清理AI内容时出错: {str(e)}")
            return content

    def _final_safety_check(self, content):
        """最终安全检查，确保没有可能导致Python执行错误的内容"""
        if not content:
            return content

        try:
            import re

            # 只检查明显的安全问题，不再过度清理Mermaid图表
            # 移除可能的Python代码执行
            content = re.sub(r'eval\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)
            content = re.sub(r'exec\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)
            content = re.sub(r'Function\s*\([^)]*\)', '[已过滤]', content, flags=re.IGNORECASE)

            # 移除可能的脚本标签
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

            return content

        except Exception as e:
            current_app.logger.warning(f"最终安全检查时出错: {str(e)}")
            return content

    def generate_explanation(self, chapter, concept, concept_type, course_name="数据库原理"):
        """生成概念讲解"""
        # 智能判断是否需要包含表格和流程图
        needs_table, needs_flowchart = self._analyze_content_needs(concept, concept_type)

        if concept_type == 'concept':
            prompt = self._build_concept_prompt(chapter, concept, needs_table, needs_flowchart, course_name)
        else:  # content
            prompt = self._build_content_prompt(chapter, concept, needs_table, needs_flowchart, course_name)

        return self._make_request(prompt, max_tokens=4000)

    def _analyze_content_needs(self, concept, concept_type):
        """智能分析内容是否需要表格和流程图"""
        # 定义需要表格的关键词
        table_keywords = ['对比', '比较', '特点', '类型', '分类', '范式', '约束', '权限', '级别', '区别']
        # 定义需要流程图的关键词
        flowchart_keywords = ['流程', '步骤', '算法', '处理', '转换', '操作', '检验', '设计', '原理']

        # 定义不需要流程图的简单概念
        simple_concept_keywords = ['定义', '概念', '基本', '简介']

        needs_table = any(keyword in concept for keyword in table_keywords)
        needs_flowchart = any(keyword in concept for keyword in flowchart_keywords)

        # 检查是否是简单概念
        is_simple_concept = any(keyword in concept for keyword in simple_concept_keywords)

        # 对于某些特定概念，调整格式需求
        if concept_type == 'concept':
            # 概念类型通常需要表格来展示特点，除非是非常简单的概念
            if not is_simple_concept:
                needs_table = True

            # 只有系统、模型、架构类概念才需要流程图
            system_keywords = ['系统', '模型', '架构', '管理系统', 'DBMS']
            basic_concepts = ['数据库', '数据', '信息', '字段', '记录']  # 基础概念不需要流程图

            if any(word in concept for word in system_keywords):
                needs_flowchart = True
            elif any(word == concept for word in basic_concepts):  # 精确匹配基础概念
                needs_flowchart = False
        else:  # content
            # 知识点类型根据内容决定
            if any(word in concept for word in ['设计', '转换', '算法', '检验', '流程', '步骤']):
                needs_flowchart = True
            if any(word in concept for word in ['对比', '分类', '类型', '区别']):
                needs_table = True

        return needs_table, needs_flowchart

    def _build_concept_prompt(self, chapter, concept, needs_table, needs_flowchart, course_name="数据库原理"):
        """构建概念讲解提示词"""
        base_sections = [
            "## 1. 概念定义\n给出准确、简洁的定义",
            "## 2. 概念解释\n使用通俗易懂的语言解释这个概念，让初学者也能理解其核心含义和重要性",
            "## 3. 详细解释\n深入解释概念的含义和重要性"
        ]

        if needs_table:
            base_sections.append("""## 4. 核心特点
使用表格形式列出主要特点：
| 特点 | 说明 | 重要性 |
|------|------|--------|
| 特点1 | 详细说明 | 重要程度 |
| 特点2 | 详细说明 | 重要程度 |""")

        if needs_flowchart:
            base_sections.append("""## 5. 工作原理/流程
使用Mermaid流程图语法描述相关流程：
```mermaid
graph TD
    A["开始"] --> B["处理步骤"]
    B --> C{"判断条件"}
    C -->|是| D["执行操作"]
    C -->|否| E["其他处理"]
    D --> F["结束"]
    E --> F
```
注意：节点标签如果包含中文，请用双引号包围。""")

        base_sections.extend([
            "## 6. 实际应用\n- 应用场景1：具体说明\n- 应用场景2：具体说明",
            "## 7. 学习要点\n- 重点1：详细说明\n- 重点2：详细说明"
        ])

        sections_text = "\n\n".join(base_sections)

        # 根据课程类型调整语气风格
        course_style = self._get_course_style(course_name)

        return f"""作为{course_name}课程的专业教师，请详细解释以下概念：

章节：{chapter}
概念：{concept}

{course_style}

请按以下格式回答：

{sections_text}

请用中文回答，确保内容准确、详细且易于理解。
注意：在Mermaid流程图中，如果节点标签包含中文，请用双引号包围，例如：A["中文标签"]。
"""

    def _build_content_prompt(self, chapter, concept, needs_table, needs_flowchart, course_name="数据库原理"):
        """构建知识点讲解提示词"""
        base_sections = [
            "## 1. 知识点概述\n简要说明这个知识点的重要性和在整个课程中的地位",
            "## 2. 概念解释\n使用通俗易懂的语言解释相关的核心概念，确保初学者能够理解",
            "## 3. 详细原理\n深入解释相关原理和方法"
        ]

        if needs_table:
            base_sections.append("""## 4. 关键要素对比
使用表格形式对比相关要素：
| 要素 | 特征 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| 要素1 | 特征描述 | 优点说明 | 缺点说明 | 场景说明 |
| 要素2 | 特征描述 | 优点说明 | 缺点说明 | 场景说明 |""")

        if needs_flowchart:
            base_sections.append("""## 5. 操作流程
使用Mermaid流程图描述操作或处理流程：
```mermaid
graph TD
    A["开始操作"] --> B["数据处理"]
    B --> C{"验证结果"}
    C -->|通过| D["保存数据"]
    C -->|失败| E["错误处理"]
    D --> F["操作完成"]
    E --> F
```
注意：节点标签如果包含中文，请用双引号包围。""")

        base_sections.extend([
            "## 6. 实例演示\n提供具体的例子或代码示例，包含：\n- 示例背景\n- 具体实现\n- 结果分析",
            "## 7. 学习建议\n- 重点掌握：关键概念和方法\n- 实践练习：具体练习建议\n- 扩展阅读：相关资料推荐"
        ])

        sections_text = "\n\n".join(base_sections)

        # 根据课程类型调整语气风格
        course_style = self._get_course_style(course_name)

        return f"""作为{course_name}课程的专业教师，请详细讲解以下知识点：

章节：{chapter}
知识点：{concept}

{course_style}

请按以下格式回答：

{sections_text}

请用中文回答，确保内容准确、详细且易于理解。
注意：在Mermaid流程图中，如果节点标签包含中文，请用双引号包围，例如：A["中文标签"]。
"""

    def _get_course_style(self, course_name):
        """根据课程类型获取相应的语气风格"""
        course_styles = {
            "数据库原理": "请采用严谨、逻辑性强的学术风格，注重理论基础和实际应用的结合。",
            "编程": "请采用实用、循序渐进的教学风格，多提供代码示例和实践指导。",
            "算法": "请采用逻辑清晰、步骤明确的解释风格，注重思维过程的展示。",
            "数据结构": "请采用图解丰富、概念清晰的教学风格，多使用可视化说明。",
            "计算机网络": "请采用层次分明、协议导向的解释风格，注重实际网络场景。",
            "操作系统": "请采用系统性、机制导向的教学风格，注重原理和实现的结合。",
            "软件工程": "请采用实践导向、工程化的教学风格，注重方法论和最佳实践。",
            "人工智能": "请采用前沿性、应用导向的教学风格，结合最新发展和实际案例。",
            "机器学习": "请采用数学严谨、实验导向的教学风格，注重理论推导和实践验证。",
            "数学": "请采用严谨、证明导向的学术风格，注重逻辑推理和定理应用。",
            "物理": "请采用现象导向、实验结合的教学风格，注重物理直觉和数学描述。",
            "化学": "请采用反应机理、实验导向的教学风格，注重化学原理和实际应用。",
            "生物": "请采用生命现象、系统性的教学风格，注重结构功能关系。"
        }

        # 默认风格
        default_style = "请采用通俗易懂、循序渐进的教学风格，确保内容既准确又易于理解。"

        # 模糊匹配课程名称
        for key, style in course_styles.items():
            if key in course_name or course_name in key:
                return style

        return default_style

    def generate_questions(self, question_type, chapters, count=1, course_name="数据库原理"):
        """生成考试题目"""
        chapters_str = "、".join(chapters)
        
        # 根据课程类型调整语气风格
        course_style = self._get_course_style(course_name)

        prompt = f"""
作为{course_name}课程的专业教师，请为以下章节生成{question_type}：

考试章节：{chapters_str}
题目数量：{count}题

{course_style}

请严格按照以下要求：
1. 题目必须来自指定章节的内容
2. 难度适中，符合本科生水平
3. 题目表述清晰、准确
4. 如果是选择题，请提供4个选项（A、B、C、D）并标明正确答案
5. 如果是简答题或设计题，请给出参考答案要点

请用中文出题，格式规范。
"""
        
        return self._make_request(prompt, max_tokens=3000)
    
    def review_answers(self, questions_and_answers, knowledge_context="", course_name="数据库原理"):
        """批改试卷答案"""
        # 根据课程类型调整语气风格
        course_style = self._get_course_style(course_name)

        prompt = f"""
作为{course_name}课程的专业教师，请批改以下试卷：

{questions_and_answers}

知识背景：
{knowledge_context}

{course_style}

请按以下格式给出批改结果：
1. 逐题批改：对每道题给出分数和评语
2. 总体评价：分析答题情况的优缺点
3. 薄弱环节：指出需要加强的知识点
4. 学习建议：提供具体的改进建议

请用中文回答，评价要客观、建设性。
"""

        return self._make_request(prompt, max_tokens=3000)
    
    def get_learning_advice(self, weak_points, chapter_context="", course_name="数据库原理"):
        """生成学习建议"""
        # 根据课程类型调整语气风格
        course_style = self._get_course_style(course_name)

        prompt = f"""
作为{course_name}课程的专业教师，请为学生提供学习建议：

薄弱知识点：{weak_points}
相关章节：{chapter_context}

{course_style}

请提供：
1. 重点复习内容
2. 学习方法建议
3. 练习题推荐
4. 学习顺序安排

请用中文回答，建议要具体、可操作。
"""

        return self._make_request(prompt)

    def batch_generate_explanations(self, chapter_concepts, progress_callback=None, course_name="数据库原理"):
        """批量生成讲解"""
        results = {}
        total = len(chapter_concepts)

        for i, (chapter, concept, concept_type) in enumerate(chapter_concepts):
            try:
                current_app.logger.info(f"批量生成 {i+1}/{total}: {chapter} - {concept}")

                # 生成讲解
                explanation = self.generate_explanation(chapter, concept, concept_type, course_name)

                if explanation and not explanation.startswith("抱歉") and not explanation.startswith("无法连接"):
                    results[f"{chapter}_{concept}"] = {
                        'success': True,
                        'explanation': explanation,
                        'chapter': chapter,
                        'concept': concept,
                        'concept_type': concept_type
                    }
                else:
                    results[f"{chapter}_{concept}"] = {
                        'success': False,
                        'error': explanation or "AI服务暂时不可用",
                        'chapter': chapter,
                        'concept': concept,
                        'concept_type': concept_type
                    }

                # 调用进度回调
                if progress_callback:
                    progress_callback(i + 1, total, chapter, concept)

                # 添加延迟避免API限制
                if i < total - 1:  # 最后一个不需要延迟
                    time.sleep(1)

            except Exception as e:
                current_app.logger.error(f"批量生成失败 {chapter} - {concept}: {str(e)}")
                results[f"{chapter}_{concept}"] = {
                    'success': False,
                    'error': f"生成失败: {str(e)}",
                    'chapter': chapter,
                    'concept': concept,
                    'concept_type': concept_type
                }

                if progress_callback:
                    progress_callback(i + 1, total, chapter, concept, error=str(e))

        return results
