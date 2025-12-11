# 导入项目需要的工具（不用改）
from flask import Flask, render_template, session, redirect, url_for, request
import random
from datetime import datetime  # 用于计时功能

# 初始化Flask应用（不用改）
app = Flask(__name__)
# 加密session的密钥（随便写一段字符串，比如生日、手机号，必须有这行）
app.secret_key = 'math100_game_2025'


def generate_question():
    """生成100以内的加减法题目（确保结果非负，不用改）"""
    # 随机选加法（+）或减法（-）
    op = random.choice(['+', '-'])
    if op == '+':
        # 加法：确保两数之和≤100（避免超过100）
        a = random.randint(0, 100)
        b = random.randint(0, 100 - a)
        correct_answer = a + b
    else:
        # 减法：确保被减数≥减数（结果不会是负数）
        a = random.randint(0, 100)
        b = random.randint(0, a)
        correct_answer = a - b
    # 返回题目信息（文本和正确答案）
    return {
        'text': f"{a} {op} {b} = ?",  # 题目显示文本（如“23 + 15 = ?”）
        'correct': correct_answer     # 正确答案（供判断对错用）
    }


@app.route('/')
def index():
    """首页：显示开始游戏按钮和题目数量选择"""
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def start_game():
    """开始游戏：初始化答题数据和计时（新增题目数量设置）"""
    session.clear()  # 清空之前的答题记录
    # 获取用户选择的题目数量，默认25题
    question_count = int(request.form.get('question_count', 25))
    session['total_questions'] = question_count  # 存储总题数
    session['current_question'] = 1  # 当前是第1题
    session['score'] = 0  # 初始分数0分
    session['wrong_questions'] = []  # 记录错误题目
    session['current_question_data'] = generate_question()  # 生成第一题
    session['start_time'] = datetime.now().timestamp()  # 记录开始时间（计时用）
    return redirect(url_for('show_question'))  # 跳转到答题页


@app.route('/question')
def show_question():
    """显示当前题目（修改为动态总题数）"""
    # 若已答完所有题，跳转到结果页
    if session.get('current_question', 0) > session.get('total_questions', 25):
        return redirect(url_for('show_result'))
    # 显示当前题目
    question_data = session.get('current_question_data')
    return render_template('question.html',
                          question=question_data,
                          current=session['current_question'],
                          total=session['total_questions'])  # 传递总题数到前端


@app.route('/submit', methods=['POST'])
def submit_answer():
    """处理用户提交的答案，判断对错并更新数据（修改为动态总题数）"""
    # 获取用户输入的答案
    user_answer = request.form.get('answer', '').strip()
    try:
        user_answer = int(user_answer)  # 把输入转成数字（非数字视为错误）
    except ValueError:
        user_answer = None  # 非数字答案标记为None
    
    # 获取当前题目的数据
    question_data = session['current_question_data']
    current_question_num = session['current_question']
    total_questions = session['total_questions']  # 获取总题数
    
    # 判断对错，生成反馈信息
    is_correct = user_answer == question_data['correct']
    feedback_msg = "答对啦！" if is_correct else "答错啦！"
    feedback_color = "green" if is_correct else "red"  # 答对绿色，答错红色
    
    # 更新分数和错误题目记录
    if is_correct:
        session['score'] += 1  # 答对加1分
    else:
        # 答错：记录错误题目（题目文本、用户答案、正确答案）
        session['wrong_questions'].append({
            'text': question_data['text'],
            'user_answer': user_answer if user_answer is not None else '无效输入',
            'correct_answer': question_data['correct']
        })
    
    # 准备下一题
    session['current_question'] = current_question_num + 1
    if current_question_num < total_questions:  # 使用动态总题数判断
        # 生成下一题，跳转到答题页并显示反馈
        session['current_question_data'] = generate_question()
        return render_template('question.html',
                              question=session['current_question_data'],
                              current=session['current_question'],
                              total=total_questions,  # 传递总题数到前端
                              feedback_msg=feedback_msg,
                              feedback_color=feedback_color)
    else:
        # 答完所有题，跳转到结果页
        return redirect(url_for('show_result'))


@app.route('/result')
def show_result():
    """显示最终得分、用时和错误题目（修改为动态总题数）"""
    # 计算总用时（从开始到结束的秒数）
    end_time = datetime.now().timestamp()
    start_time = session.get('start_time', end_time)  # 防止异常情况
    total_seconds = int(end_time - start_time)
    # 转换为“分:秒”格式（补零，如1分5秒显示为01:05）
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    time_used = f"{minutes:02d}:{seconds:02d}"
    
    # 显示结果页（使用动态总题数）
    return render_template('result.html',
                          score=session['score'],  # 总得分
                          total=session['total_questions'],  # 动态总题数
                          wrong=session['wrong_questions'],  # 错误题目
                          time_used=time_used)  # 总用时


# 启动项目（修改后）
if __name__ == '__main__':
    # 本地运行，访问地址：http://127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)

# 新增：供Vercel生产环境使用的WSGI入口
# Vercel的Python运行时会自动识别名为`application`的WSGI应用
application = app
