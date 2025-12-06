"""
路由定义 - 数据库学习系统
"""
from flask import Blueprint, render_template, request, jsonify, session, send_file
from services import LearningService, ExamService, ReviewService, SettingsService, CourseService
from services.task_service import TaskService
from datetime import datetime
import os

# 创建蓝图
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# 服务将在需要时初始化
learning_service = None
exam_service = None
review_service = None
settings_service = None
course_service = None
task_service = None

def get_learning_service():
    global learning_service
    if learning_service is None:
        learning_service = LearningService()
    return learning_service

def get_exam_service():
    global exam_service
    if exam_service is None:
        exam_service = ExamService()
    return exam_service

def get_review_service():
    global review_service
    if review_service is None:
        review_service = ReviewService()
    return review_service

def get_settings_service():
    global settings_service
    if settings_service is None:
        settings_service = SettingsService()
    return settings_service

def get_course_service():
    global course_service
    if course_service is None:
        course_service = CourseService()
    return course_service

def get_task_service():
    global task_service
    if task_service is None:
        task_service = TaskService()
    return task_service

# ==================== 主页面路由 ====================

@main_bp.route('/')
def index():
    """主页"""
    return render_template('index.html')

@main_bp.route('/learning')
def learning_page():
    """学习页面"""
    try:
        learning_service = get_learning_service()
        knowledge_base = learning_service.get_current_knowledge_base()
        chapters = knowledge_base.get_chapters()
        return render_template('learning.html', chapters=chapters)
    except Exception as e:
        return render_template('learning.html', chapters=[])

@main_bp.route('/exam')
def exam_page():
    """考试页面"""
    try:
        learning_service = get_learning_service()
        knowledge_base = learning_service.get_current_knowledge_base()
        chapters = knowledge_base.get_chapters()
        exam_service = get_exam_service()
        exam_model = exam_service.exam_model
        question_types = exam_model.get_question_types()
        return render_template('exam.html', chapters=chapters, question_types=question_types)
    except Exception as e:
        return render_template('exam.html', chapters=[], question_types=[])

@main_bp.route('/review')
def review_page():
    """审批页面"""
    return render_template('review.html')

@main_bp.route('/settings')
def settings_page():
    """设置页面"""
    try:
        settings_service = get_settings_service()
        course_service = get_course_service()

        # 获取当前设置
        current_settings = settings_service.load_settings()

        # 获取可用模型
        available_models = settings_service.get_available_models()

        # 获取所有课程
        all_courses = course_service.get_all_courses()

        return render_template('settings.html',
                             settings=current_settings,
                             available_models=available_models,
                             courses=all_courses)
    except Exception as e:
        return render_template('settings.html',
                             settings={},
                             available_models=[],
                             courses=[])

# ==================== 学习相关API ====================

@api_bp.route('/chapters')
def get_chapters():
    """获取所有章节"""
    try:
        learning_service = get_learning_service()
        knowledge_base = learning_service.get_current_knowledge_base()
        chapters = knowledge_base.get_chapters()
        return jsonify({
            'success': True,
            'chapters': chapters,
            'subject': knowledge_base.get_subject()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/chapters/<chapter_name>/content')
def get_chapter_content(chapter_name):
    """获取章节内容"""
    try:
        learning_service = get_learning_service()
        content = learning_service.get_chapter_content(chapter_name)
        if content:
            return jsonify({'success': True, 'content': content})
        else:
            return jsonify({'success': False, 'error': '章节不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/explain', methods=['POST'])
def explain_concept():
    """获取AI讲解"""
    try:
        data = request.get_json()
        username = session.get('username', 'anonymous')
        chapter = data.get('chapter')
        concept = data.get('concept')
        concept_type = data.get('type', 'concept')

        if not chapter or not concept:
            return jsonify({'success': False, 'error': '参数不完整'}), 400

        learning_service = get_learning_service()
        result = learning_service.explain_concept(username, chapter, concept, concept_type)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batch-explain-chapter', methods=['POST'])
def batch_explain_chapter():
    """批量生成章节讲解 (异步)"""
    try:
        data = request.get_json()
        username = session.get('username', 'anonymous')
        chapter = data.get('chapter')

        if not chapter:
            return jsonify({'success': False, 'error': '章节参数不能为空'}), 400

        learning_service = get_learning_service()
        task_service = get_task_service()

        # 提交异步任务
        task_id = task_service.submit_task(
            learning_service.batch_explain_chapter,
            username, 
            chapter
        )
        
        return jsonify({
            'success': True, 
            'task_id': task_id,
            'message': '批量生成任务已提交'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/batch-explain-all', methods=['POST'])
def batch_explain_all():
    """批量生成全部讲解 (异步)"""
    try:
        username = session.get('username', 'anonymous')
        learning_service = get_learning_service()
        task_service = get_task_service()

        # 提交异步任务
        task_id = task_service.submit_task(
            learning_service.batch_explain_all,
            username
        )
        
        return jsonify({
            'success': True, 
            'task_id': task_id,
            'message': '批量生成全部任务已提交'
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/tasks/<task_id>/status')
def get_task_status(task_id):
    """获取任务状态"""
    try:
        task_service = get_task_service()
        task = task_service.get_task(task_id)
        
        if task:
            return jsonify({'success': True, 'task': task})
        else:
            return jsonify({'success': False, 'error': '任务不存在'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/regenerate-explain', methods=['POST'])
def regenerate_explain():
    """重新生成讲解"""
    try:
        data = request.get_json()
        username = session.get('username', 'anonymous')
        chapter = data.get('chapter')
        concept = data.get('concept')
        concept_type = data.get('type', 'concept')

        if not chapter or not concept:
            return jsonify({'success': False, 'error': '参数不完整'}), 400

        learning_service = get_learning_service()
        result = learning_service.regenerate_explanation(username, chapter, concept, concept_type)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/search')
def search_knowledge():
    """搜索知识点"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify({'success': False, 'error': '搜索关键词不能为空'}), 400
        
        learning_service = get_learning_service()
        results = learning_service.search_knowledge(keyword)
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/progress')
def get_progress():
    """获取学习进度"""
    try:
        username = session.get('username', 'anonymous')
        learning_service = get_learning_service()
        progress = learning_service.track_progress(username)
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 考试相关API ====================

@api_bp.route('/generate-exam', methods=['POST'])
def generate_exam():
    """生成考试"""
    try:
        data = request.get_json()
        username = session.get('username', 'anonymous')
        chapters = data.get('chapters', [])
        question_types = data.get('question_types', [])
        use_ai = data.get('use_ai', True)
        
        if not chapters:
            return jsonify({'success': False, 'error': '请选择至少一个章节'}), 400
        
        # 创建考试
        exam_service = get_exam_service()
        result = exam_service.create_exam(username, chapters, question_types)
        if not result['success']:
            return jsonify(result), 500

        exam_id = result['exam_id']

        # 生成题目
        generate_result = exam_service.generate_questions(exam_id, use_ai)
        if not generate_result['success']:
            return jsonify(generate_result), 500
        
        return jsonify({
            'success': True,
            'exam_id': exam_id,
            'formatted_paper': generate_result['formatted_paper'],
            'exam_paper': generate_result['exam_paper']
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/download-exam/<exam_id>')
def download_exam(exam_id):
    """下载试卷"""
    try:
        # 获取考试数据
        exam_service = get_exam_service()
        exam_data = exam_service.get_exam_by_id(exam_id)
        if not exam_data:
            return jsonify({'success': False, 'error': '考试不存在'}), 404

        # 重新生成试卷内容
        generate_result = exam_service.generate_questions(exam_id, use_ai=False)
        if not generate_result['success']:
            return jsonify(generate_result), 500

        # 保存文件
        save_result = exam_service.save_exam_file(exam_id, generate_result['formatted_paper'])
        if not save_result['success']:
            return jsonify(save_result), 500
        
        # 返回文件
        return send_file(
            save_result['file_path'],
            as_attachment=True,
            download_name=save_result['filename'],
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/exam-history')
def get_exam_history():
    """获取考试历史"""
    try:
        username = session.get('username', 'anonymous')
        exam_service = get_exam_service()
        history = exam_service.get_exam_history(username)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 审批相关API ====================

@api_bp.route('/upload-exam', methods=['POST'])
def upload_exam():
    """上传试卷文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'}), 400

        file = request.files['file']
        username = session.get('username', 'anonymous')

        review_service = get_review_service()
        result = review_service.upload_exam_file(username, file)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/parse-exam/<int:record_id>')
def parse_exam(record_id):
    """解析试卷文件"""
    try:
        review_service = get_review_service()
        result = review_service.parse_exam_file(record_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/review-exam', methods=['POST'])
def review_exam():
    """审批试卷"""
    try:
        data = request.get_json()
        record_id = data.get('record_id')

        if not record_id:
            return jsonify({'success': False, 'error': '记录ID不能为空'}), 400

        review_service = get_review_service()
        result = review_service.review_exam(record_id)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/review-history')
def get_review_history():
    """获取审批历史"""
    try:
        username = session.get('username', 'anonymous')
        review_service = get_review_service()
        history = review_service.get_review_history(username)
        return jsonify({'success': True, 'history': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 用户相关API ====================

@api_bp.route('/set-username', methods=['POST'])
def set_username():
    """设置用户名"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()

        if not username:
            return jsonify({'success': False, 'error': '用户名不能为空'}), 400

        session['username'] = username
        return jsonify({'success': True, 'username': username})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/get-username')
def get_username():
    """获取当前用户名"""
    username = session.get('username', 'anonymous')
    return jsonify({'success': True, 'username': username})

# ==================== 设置相关API ====================

@api_bp.route('/settings/ollama/models')
def get_ollama_models():
    """获取可用的Ollama模型"""
    try:
        settings_service = get_settings_service()
        models = settings_service.get_available_models()
        return jsonify({'success': True, 'models': models})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/settings/ollama/test', methods=['POST'])
def test_ollama_connection():
    """测试Ollama连接"""
    try:
        data = request.get_json()
        api_url = data.get('api_url')
        model_name = data.get('model_name')

        if not api_url or not model_name:
            return jsonify({'success': False, 'error': '参数不完整'}), 400

        settings_service = get_settings_service()
        result = settings_service.test_ollama_connection(api_url, model_name)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/settings/ollama/save', methods=['POST'])
def save_ollama_settings():
    """保存Ollama设置"""
    try:
        data = request.get_json()
        api_url = data.get('api_url')
        model_name = data.get('model_name')

        if not api_url or not model_name:
            return jsonify({'success': False, 'error': '参数不完整'}), 400

        settings_service = get_settings_service()
        result = settings_service.update_ollama_settings(api_url, model_name)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 课程管理API ====================

@api_bp.route('/courses')
def get_all_courses():
    """获取所有课程"""
    try:
        course_service = get_course_service()
        courses = course_service.get_all_courses()
        courses_data = [course.to_dict() for course in courses]
        return jsonify({'success': True, 'courses': courses_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/courses/create', methods=['POST'])
def create_course():
    """创建新课程"""
    try:
        data = request.get_json()
        course_name = data.get('name', '').strip()
        description = data.get('description', '').strip()

        if not course_name:
            return jsonify({'success': False, 'error': '课程名称不能为空'}), 400

        course_service = get_course_service()
        result = course_service.create_course_with_ai(course_name, description)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/courses/<course_name>/delete', methods=['DELETE'])
def delete_course(course_name):
    """删除课程"""
    try:
        course_service = get_course_service()
        result = course_service.delete_course(course_name)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/health')
def health_check():
    """健康检查端点 - 用于Docker健康检查"""
    try:
        # 检查基本服务状态
        from flask import current_app
        from sqlalchemy import text

        # 检查数据库连接
        from extensions import db
        with db.engine.connect() as connection:
            connection.execute(text('SELECT 1'))

        # 检查必要文件
        required_files = [
            current_app.config.get('KNOWLEDGE_BASE_FILE', 'kownlgebase.json'),
            current_app.config.get('TEST_MODEL_FILE', 'testmodel.json')
        ]

        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)

        # 检查数据目录
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)

        status = {
            'status': 'healthy',
            'database': 'connected',
            'files': {
                'missing': missing_files,
                'status': 'ok' if not missing_files else 'warning'
            },
            'timestamp': str(datetime.now())
        }

        return jsonify(status), 200

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': str(datetime.now())
        }), 503

@api_bp.route('/courses/current')
def get_current_course():
    """获取当前课程"""
    try:
        settings_service = get_settings_service()
        current_course = settings_service.get_current_course()
        return jsonify({'success': True, 'current_course': current_course})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/courses/current', methods=['POST'])
def set_current_course():
    """设置当前课程"""
    try:
        data = request.get_json()
        course_name = data.get('course_name')

        if not course_name:
            return jsonify({'success': False, 'error': '课程名称不能为空'}), 400

        settings_service = get_settings_service()
        result = settings_service.set_current_course(course_name)

        # 更新session
        session['current_course'] = course_name

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
