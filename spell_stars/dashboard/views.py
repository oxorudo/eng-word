from accounts.models import Student
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .utils import plot_learning_mode_hours, plot_test_scores, plot_learning_results
from accounts.models import ParentStudentRelation, Parent
from plotly.subplots import make_subplots


@login_required
def dashboard_view(request, student_id=None):
    if request.user.role == 'student':
        # 학생: 본인 데이터 확인
        student = get_object_or_404(Student, user=request.user)
        template_name = 'dashboard/dashboard.html'
        context = {
            "graphs": create_dashboard_graphs(student),
        }
    elif request.user.role == 'parent':
        # 부모: 자녀 데이터 확인
        if not student_id:
            raise PermissionDenied("학생 ID가 제공되지 않았습니다.")
        
        # 부모는 Parent 모델로 연결된 User를 통해 확인
        parent = get_object_or_404(Parent, user=request.user)  # user가 Parent 객체로 연결
        relation = get_object_or_404(ParentStudentRelation, student_id=student_id, parent=parent)
        student = relation.student  # 해당 학생 정보를 가져옴
        template_name = 'dashboard/student_dashboard.html'
        
        # 자녀의 이름을 context에 포함
        context = {
            "student_name": student.user.name,
            "graphs": create_dashboard_graphs(student),
        }
    else:
        raise PermissionDenied("접근 권한이 없습니다.")

    return render(request, template_name, context)


def create_dashboard_graphs(student):
    """그래프를 생성하는 함수"""
    # 각 그래프를 먼저 생성
    fig1 = plot_learning_mode_hours(student)
    fig2 = plot_test_scores(student)
    fig3 = plot_learning_results(student)
    
    # 각 그래프에 대한 레이아웃 업데이트 (각 그래프의 개별 설정)
    layout1 = dict(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold'),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.7)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=14)
        ),
    )

    layout2 = dict(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold'),
        xaxis=dict(tickformat='%Y-%m-%d')
    )

    layout3 = dict(
        font=dict(family="Arial, sans-serif", size=18, color="black"),
        title_x=0.5,
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#ffffff",
        title_font=dict(size=20, color='black', family='Arial, sans-serif', weight='bold'),
        xaxis=dict(tickformat='%Y-%m-%d')
    )
    
    fig1.update_layout(layout1)
    fig2.update_layout(layout2)
    fig3.update_layout(layout3)

    # 서브플롯을 결합 (서브플롯의 레이아웃을 설정)
    final_fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=("학습 모드별 학습 시간", "시험 점수 변화", "예문 학습 결과"),
        specs=[[{'type': 'domain'}], [{'type': 'xy'}], [{'type': 'xy'}]]  # 도넛 차트와 XY 그래프의 혼합 설정
    )

    # 각각의 trace를 서브플롯에 추가
    for trace in fig1['data']:
        final_fig.add_trace(trace, row=1, col=1)
    for trace in fig2['data']:
        final_fig.add_trace(trace, row=2, col=1)
    for trace in fig3['data']:
        final_fig.add_trace(trace, row=3, col=1)

    # 서브플롯 전체에 대한 레이아웃 설정
    final_fig.update_layout(
        height=2000,
        width=1000,
        title_text="대시보드",
        title_x=0.5,
        plot_bgcolor="#f9f9f9",  # 서브플롯 전체의 배경색 설정
        paper_bgcolor="#ffffff",  # 종이 배경색 설정
        showlegend=True  # 범례를 표시
    )

    # 각 서브플롯의 레이아웃 설정
    final_fig.layout.update(layout1)
    final_fig.layout.update(layout2)
    final_fig.layout.update(layout3)

    # 최종적으로 HTML로 변환하여 반환
    return final_fig.to_html(full_html=False)
