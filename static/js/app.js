// 数据库学习系统 - 主要JavaScript文件

$(document).ready(function() {
    // 初始化应用
    initializeApp();

    // 加载用户信息
    loadUserInfo();

    // 加载课程信息
    loadCourseInfo();

    // 绑定全局事件
    bindGlobalEvents();
});

// 初始化应用
function initializeApp() {
    // 设置CSRF令牌（如果需要）
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                // 可以在这里添加CSRF令牌
            }
        }
    });
    
    // 设置全局AJAX错误处理
    $(document).ajaxError(function(event, xhr, settings, thrownError) {
        if (xhr.status === 0) {
            console.log('网络连接错误');
        } else if (xhr.status === 500) {
            console.log('服务器内部错误');
        } else if (xhr.status === 404) {
            console.log('请求的资源不存在');
        }
    });
    
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    console.log('应用初始化完成');
}

// 加载用户信息
function loadUserInfo() {
    $.get('/api/get-username')
        .done(function(data) {
            if (data.success) {
                updateUsernameDisplay(data.username);
            }
        })
        .fail(function() {
            console.log('获取用户信息失败');
        });
}

// 更新用户名显示
function updateUsernameDisplay(username) {
    $('#current-username').text(username);
    $('#usernameInput').val(username);
}

// 绑定全局事件
function bindGlobalEvents() {
    // 用户名输入框回车事件
    $('#usernameInput').keypress(function(e) {
        if (e.which == 13) {
            setUsername();
        }
    });
    
    // 页面可见性变化事件
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            // 页面变为可见时，可以刷新数据
            console.log('页面变为可见');
        }
    });
}

// 设置用户名
function setUsername() {
    const username = $('#usernameInput').val().trim();
    
    if (!username) {
        showToast('用户名不能为空', 'warning');
        return;
    }
    
    if (username.length > 50) {
        showToast('用户名长度不能超过50个字符', 'warning');
        return;
    }
    
    $.ajax({
        url: '/api/set-username',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ username: username })
    })
    .done(function(data) {
        if (data.success) {
            updateUsernameDisplay(data.username);
            $('#usernameModal').modal('hide');
            showToast('用户名设置成功', 'success');
        } else {
            showToast('设置失败: ' + data.error, 'danger');
        }
    })
    .fail(function() {
        showToast('网络错误，请稍后重试', 'danger');
    });
}

// 显示学习进度
function showProgress() {
    $('#progressModal').modal('show');
    
    // 重置内容
    $('#progress-content').html(`
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
        </div>
    `);
    
    // 加载进度数据
    $.get('/api/progress')
        .done(function(data) {
            if (data.success) {
                displayProgress(data.progress);
            } else {
                $('#progress-content').html(`
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>加载失败: ${data.error}
                    </div>
                `);
            }
        })
        .fail(function() {
            $('#progress-content').html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>网络错误，请稍后重试
                </div>
            `);
        });
}

// 显示进度信息
function displayProgress(progress) {
    let html = `
        <div class="row mb-4">
            <div class="col-md-4 text-center">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h3>${progress.chapters_studied}</h3>
                        <p class="mb-0">已学习章节</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 text-center">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h3>${progress.concepts_learned}</h3>
                        <p class="mb-0">已学习概念</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 text-center">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h3>${progress.recent_activity.length}</h3>
                        <p class="mb-0">最近活动</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    if (progress.recent_activity.length > 0) {
        html += `
            <h6>最近学习活动</h6>
            <div class="list-group">
        `;
        
        progress.recent_activity.forEach(activity => {
            const date = new Date(activity.created_at).toLocaleString();
            const typeIcon = activity.concept_type === 'concept' ? 'fas fa-lightbulb text-warning' : 'fas fa-book text-info';
            
            html += `
                <div class="list-group-item">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">
                            <i class="${typeIcon} me-2"></i>${activity.concept}
                        </h6>
                        <small class="text-muted">${date}</small>
                    </div>
                    <p class="mb-1">${activity.chapter}</p>
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += `
            <div class="text-muted text-center">
                <i class="fas fa-book fa-3x mb-3"></i>
                <p>还没有学习记录，快去开始学习吧！</p>
            </div>
        `;
    }
    
    $('#progress-content').html(html);
}

// 显示Toast消息
function showToast(message, type = 'info') {
    // 创建toast容器（如果不存在）
    if (!$('#toast-container').length) {
        $('body').append(`
            <div id="toast-container" class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;"></div>
        `);
    }
    
    const toastId = 'toast-' + Date.now();
    const iconClass = {
        'success': 'fas fa-check-circle text-success',
        'danger': 'fas fa-exclamation-circle text-danger',
        'warning': 'fas fa-exclamation-triangle text-warning',
        'info': 'fas fa-info-circle text-info'
    }[type] || 'fas fa-info-circle text-info';
    
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="${iconClass} me-2"></i>
                <strong class="me-auto">系统消息</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    $('#toast-container').append(toastHtml);
    
    // 显示toast
    const toastElement = new bootstrap.Toast(document.getElementById(toastId));
    toastElement.show();
    
    // 自动移除
    setTimeout(() => {
        $(`#${toastId}`).remove();
    }, 5000);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化日期时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('已复制到剪贴板', 'success');
        }).catch(() => {
            showToast('复制失败', 'danger');
        });
    } else {
        // 降级方案
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showToast('已复制到剪贴板', 'success');
        } catch (err) {
            showToast('复制失败', 'danger');
        }
        document.body.removeChild(textArea);
    }
}

// 检查网络连接
function checkNetworkConnection() {
    return navigator.onLine;
}

// 网络状态变化监听
window.addEventListener('online', function() {
    showToast('网络连接已恢复', 'success');
});

window.addEventListener('offline', function() {
    showToast('网络连接已断开', 'warning');
});

// 加载课程信息
function loadCourseInfo() {
    // 加载当前课程
    $.get('/api/courses/current')
        .done(function(data) {
            if (data.success) {
                updateCurrentCourseDisplay(data.current_course);
            }
        })
        .fail(function() {
            console.log('获取当前课程失败');
        });

    // 加载课程列表
    loadCourseList();
}

// 加载课程列表
function loadCourseList() {
    $.get('/api/courses')
        .done(function(data) {
            if (data.success) {
                updateCourseDropdown(data.courses);
            }
        })
        .fail(function() {
            console.log('获取课程列表失败');
        });
}

// 更新当前课程显示
function updateCurrentCourseDisplay(courseName) {
    $('#current-course-name').text(courseName);

    // 更新页面标题
    const currentTitle = document.title;
    if (currentTitle.includes(' - ')) {
        const parts = currentTitle.split(' - ');
        document.title = parts[0] + ' - ' + courseName + '学习系统';
    }
}

// 更新课程下拉菜单
function updateCourseDropdown(courses) {
    const dropdown = $('#course-dropdown-menu');
    const currentCourse = $('#current-course-name').text();

    // 清空现有课程项
    dropdown.find('.course-item').remove();

    // 添加课程项
    courses.forEach(course => {
        const isActive = course.name === currentCourse;
        const courseItem = `
            <li class="course-item">
                <a class="dropdown-item ${isActive ? 'active' : ''}" href="#"
                   onclick="switchCourse('${course.name}')">
                    <i class="fas fa-book me-2"></i>${course.name}
                    ${isActive ? '<i class="fas fa-check ms-auto"></i>' : ''}
                </a>
            </li>
        `;
        dropdown.find('.dropdown-divider').before(courseItem);
    });
}

// 切换课程
function switchCourse(courseName) {
    if (courseName === $('#current-course-name').text()) {
        return; // 已经是当前课程
    }

    $.ajax({
        url: '/api/courses/current',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ course_name: courseName })
    })
    .done(function(data) {
        if (data.success) {
            updateCurrentCourseDisplay(courseName);
            showToast('课程切换成功', 'success');

            // 如果在学习页面，刷新内容
            if (window.location.pathname.includes('/learning')) {
                setTimeout(() => {
                    location.reload();
                }, 1000);
            }
        } else {
            showToast('切换失败: ' + data.error, 'danger');
        }
    })
    .fail(function() {
        showToast('网络错误，请稍后重试', 'danger');
    });
}

// 导出全局函数
window.setUsername = setUsername;
window.showProgress = showProgress;
window.showToast = showToast;
window.formatFileSize = formatFileSize;
window.formatDateTime = formatDateTime;
window.copyToClipboard = copyToClipboard;
window.loadCourseList = loadCourseList;
window.switchCourse = switchCourse;
