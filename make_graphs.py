"""
PPT용 그래프 재생성 — 폰트 확대 + 설명 강화
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
import os

# 한글 폰트
for fname in fm.findSystemFonts():
    if 'malgun' in fname.lower():
        plt.rcParams['font.family'] = fm.FontProperties(fname=fname).get_name()
        break
plt.rcParams['axes.unicode_minus'] = False

OUT = 'analysis/graphs'
os.makedirs(OUT, exist_ok=True)

# PPT 색상
BLUE     = '#2563EB'
BLUE_LT  = '#DBEAFE'
DARK     = '#111827'
MUTED    = '#6B7280'
WHITE    = '#FFFFFF'
RED_C    = '#DC2626'
GREEN_C  = '#059669'
PURPLE   = '#7C3AED'
GRAY_BG  = '#F8FAFC'

# ── 그래프 1: summary_insight ─────────────────────────────────────────────────
def make_summary():
    insights = [
        {
            'title': '독서 효과 인식',
            'value': '77.9%',
            'sub':   '학생이 독서가\n도움된다고 인식',
            'detail':'→ 가치는 알지만\n탐색 방법이 부족',
            'color': BLUE,
        },
        {
            'title': '선호 분야 편중',
            'value': '45.5%',
            'sub':   '소설·동화에만\n집중',
            'detail':'→ 과학·역사 등\n다양한 분야 탐색 필요',
            'color': RED_C,
        },
        {
            'title': '책 선택 방법 1위',
            'value': '41.6%',
            'sub':   '서점·도서관\n직접 선택',
            'detail':'→ 온라인 우연한\n발견 경험 부재',
            'color': GREEN_C,
        },
        {
            'title': '학교에 바라는 것 1위',
            'value': '31.0%',
            'sub':   '관심에 맞는\n책 소개 원함',
            'detail':'→ BookPath의\n핵심 기능!',
            'color': PURPLE,
        },
    ]

    fig, axes = plt.subplots(1, 4, figsize=(18, 6.5))
    fig.patch.set_facecolor(GRAY_BG)

    for ax, ins in zip(axes, insights):
        ax.set_facecolor(WHITE)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # 테두리 박스
        rect = mpatches.FancyBboxPatch(
            (0.04, 0.04), 0.92, 0.92,
            boxstyle='round,pad=0.02',
            facecolor=WHITE, edgecolor=ins['color'], linewidth=3)
        ax.add_patch(rect)

        # 상단 컬러 바
        top = mpatches.FancyBboxPatch(
            (0.04, 0.86), 0.92, 0.1,
            boxstyle='round,pad=0.01',
            facecolor=ins['color'], edgecolor='none')
        ax.add_patch(top)

        ax.text(0.5, 0.915, ins['title'],
                ha='center', va='center',
                fontsize=14, fontweight='bold', color=WHITE)

        ax.text(0.5, 0.63, ins['value'],
                ha='center', va='center',
                fontsize=38, fontweight='bold', color=ins['color'])

        ax.text(0.5, 0.42, ins['sub'],
                ha='center', va='center',
                fontsize=13, color=DARK, linespacing=1.5)

        # 구분선
        ax.plot([0.15, 0.85], [0.28, 0.28], color='#E5E7EB', lw=1.2)

        ax.text(0.5, 0.16, ins['detail'],
                ha='center', va='center',
                fontsize=12, color=ins['color'],
                fontstyle='italic', linespacing=1.5)

    plt.suptitle(
        'BookPath 필요성 — 핵심 데이터 근거 (2025 국민독서실태조사)',
        fontsize=17, fontweight='bold', y=1.01, color=DARK)

    plt.tight_layout(pad=1.2)
    path = f'{OUT}/summary_insight.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=GRAY_BG)
    plt.close()
    print(f'저장: {path}')


# ── 그래프 2: q34 학교에 바라는 점 ───────────────────────────────────────────
def make_q34():
    q34_short = [
        '내 관심에 맞는\n책 소개',
        '도서관 편하게\n이용',
        '교실 학급문고\n확충',
        '독서 시간\n확대',
        '독서 행사\n다양화',
        '독서 방법\n지도',
    ]
    q34_data = {
        '전체':   [31, 25, 17, 15, 8, 3],
        '초등학교': [27, 28, 18, 12, 10, 4],
        '중학교':  [34, 24, 17, 15, 8, 3],
        '고등학교': [32, 24, 16, 20, 6, 3],
    }
    schools     = ['전체', '초등학교', '중학교', '고등학교']
    bar_colors  = ['#6B7280', '#F59E0B', '#10B981', '#2563EB']

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(WHITE)

    n_groups = len(q34_short)
    n_bars   = len(schools)
    x        = np.arange(n_groups)
    bw       = 0.17

    for i, (school, color) in enumerate(zip(schools, bar_colors)):
        vals   = q34_data[school]
        offset = (i - n_bars / 2 + 0.5) * bw
        bars   = ax.bar(x + offset, vals, width=bw,
                        label=school, color=color, alpha=0.9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.4,
                    f'{val}',
                    ha='center', va='bottom',
                    fontsize=11, color=DARK, fontweight='bold')

    # 1위 강조 영역
    ax.axvspan(-0.45, 0.45, alpha=0.07, color=BLUE)
    ax.text(0, 39.5,
            '전교급 1위\n→ BookPath가 직접 해결!',
            ha='center', va='bottom',
            fontsize=13, color=BLUE, fontweight='bold', linespacing=1.4)

    ax.set_xticks(x)
    ax.set_xticklabels(q34_short, fontsize=13, linespacing=1.4)
    ax.set_ylabel('비율 (%)', fontsize=13)
    ax.set_ylim(0, 44)
    ax.set_title(
        '학교 독서 환경에서 바라는 점 (1순위) — 학교급별\n'
        '2025 국민독서실태조사',
        fontsize=16, fontweight='bold', pad=14, color=DARK)
    ax.legend(fontsize=12, framealpha=0.9, loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', labelsize=12)

    plt.tight_layout()
    path = f'{OUT}/q34_school_reading_wishes.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close()
    print(f'저장: {path}')


if __name__ == '__main__':
    make_summary()
    make_q34()
    print('\n완료!')
