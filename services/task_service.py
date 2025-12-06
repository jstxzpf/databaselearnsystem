"""
任务服务 - 处理异步后台任务
"""
import uuid
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from flask import current_app

class TaskService:
    """任务服务类"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskService, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.tasks = {}  # 存储任务状态: {task_id: {status, result, error, progress, ...}}
        self._initialized = True
        
        # 启动清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_tasks, daemon=True)
        self.cleanup_thread.start()
    
    def submit_task(self, func, *args, **kwargs):
        """提交任务"""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            'id': task_id,
            'status': 'pending',
            'progress': 0,
            'created_at': time.time(),
            'result': None,
            'error': None,
            'message': '任务已提交'
        }
        
        def task_wrapper(tid, f, *a, **kw):
            try:
                self.update_task(tid, status='running', message='任务正在执行')
                
                # 注入进度回调
                if 'progress_callback' not in kw:
                    kw['progress_callback'] = lambda p: self.update_progress(tid, p)
                
                result = f(*a, **kw)
                self.update_task(tid, status='completed', result=result, progress=100, message='任务完成')
            except Exception as e:
                current_app.logger.error(f"任务 {tid} 执行失败: {e}")
                self.update_task(tid, status='failed', error=str(e), message=f'任务失败: {str(e)}')
        
        # 使用应用上下文，因为很多服务需要访问 current_app
        app = current_app._get_current_object()
        
        def context_wrapper(tid, f, *a, **kw):
            with app.app_context():
                task_wrapper(tid, f, *a, **kw)
                
        self.executor.submit(context_wrapper, task_id, func, *args, **kwargs)
        return task_id
    
    def get_task(self, task_id):
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id, **kwargs):
        """更新任务状态"""
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)
            self.tasks[task_id]['updated_at'] = time.time()
            
    def update_progress(self, task_id, progress_data):
        """更新进度"""
        if task_id in self.tasks:
            # 如果是简单的数字进度
            if isinstance(progress_data, (int, float)):
                self.tasks[task_id]['progress'] = progress_data
            # 如果是详细的进度对象
            elif isinstance(progress_data, dict):
                if 'percentage' in progress_data:
                    self.tasks[task_id]['progress'] = progress_data['percentage']
                self.tasks[task_id]['details'] = progress_data
                
                # 更新消息
                if 'chapter' in progress_data and 'concept' in progress_data:
                    self.tasks[task_id]['message'] = f"正在生成: {progress_data['chapter']} - {progress_data['concept']}"
    
    def _cleanup_tasks(self):
        """定期清理过期任务"""
        while True:
            try:
                time.sleep(3600)  # 每小时清理一次
                now = time.time()
                expired_tasks = []
                
                for tid, task in self.tasks.items():
                    # 清理24小时前的任务
                    if now - task['created_at'] > 86400:
                        expired_tasks.append(tid)
                        
                for tid in expired_tasks:
                    del self.tasks[tid]
                    
            except Exception as e:
                print(f"任务清理出错: {e}")
