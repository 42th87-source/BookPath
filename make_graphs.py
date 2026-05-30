"""
PPT용 그래프 재생성 — 폰트 확대 + 어노테이션 강화
q6, q14, q15, summary_insight, q34
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import os

# 한글 폰트
for fname in fm.findSystemFonts():
    if 'malgun' in fname.lower():
        plt.rcParams['font.family'] = fm.FontProperties(fname=fname).get_name()
        break
plt.rcParams['axes.unicode_minus'] = False

OUT      = 'analysis/graphs'
DATA     = '2025 국민독서실태조사. 학생.xlsx'
os.makedirs(OUT, exist_ok=True)

# PPT 색상
BLUE    = '#2563EB'
BLUE_LT = '#DBEAFE'
DARK    = '#111827'
MUTED   = '#6B7280'
WHITE   = '#FFFFFF'
RED_C   = '#DC2626'
GREEN_C = '#059669'
PURPLE  = '#7C3AED'
GRAY_BG = '#F8FAFC'

# 데이터 로드
print("데이터 로드 중...")
df = pd.read_excel(DATA, sheet_name='Sheet1', header=None)
print(f"  로드 완료: {df.shape}")

schools_kr = ['전체', '초등학교', '중학교', '고등학교']


# ── 데이터 추출 헬퍼 ──────────────────────────────────────────────────────────
def get_rows(row_list, col_start, col_end):
    result = {}
    for label, row in zip(schools_kr, row_list):
        vals = []
        for c in range(col_start, col_end):
            v = df.iloc[row, c]
            vals.append(float(v) if str(v) != 'nan' else 0.0)
        result[label] = vals
    return result


# ── Q6 독서 도움 정도 ─────────────────────────────────────────────────────────
def make_q6():
    q6 = get_rows([559, 560, 561, 562], 3, 8)

    # 3개 범주로 합산 (겹침 방지)
    vals_3 = [
        q6['전체'][0],                          # 매우 도움이 된다
        q6['전체'][1],                          # 어느 정도 도움이 된다
        q6['전체'][2],                          # 보통이다
        q6['전체'][3] + q6['전체'][4],          # 도움이 되지 않는다 (합산)
    ]
    labels_3 = [
        f'매우 도움이 된다\n{vals_3[0]:.1f}%',
        f'어느 정도 도움이 된다\n{vals_3[1]:.1f}%',
        f'보통이다\n{vals_3[2]:.1f}%',
        f'도움이 되지 않는다\n{vals_3[3]:.1f}%',
    ]
    wcolors = ['#1D4ED8', '#3B82F6', '#93C5FD', '#FCA5A5']
    explode = (0.06, 0.03, 0, 0)

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    wedges, texts = ax.pie(
        vals_3,
        labels=None,           # 직접 라벨 없이 수동 배치
        colors=wcolors,
        explode=explode,
        startangle=90,
        wedgeprops=dict(width=0.62, edgecolor='white', linewidth=2),
    )

    # 각 조각에 레이블 수동 배치 (겹침 방지)
    label_dist = 1.28
    for i, (wedge, label, val) in enumerate(zip(wedges, labels_3, vals_3)):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = label_dist * np.cos(np.deg2rad(angle))
        y = label_dist * np.sin(np.deg2rad(angle))
        ha = 'left' if x > 0 else 'right'
        ax.annotate(
            label,
            xy=(0.75 * np.cos(np.deg2rad(angle)),
                0.75 * np.sin(np.deg2rad(angle))),
            xytext=(x, y),
            ha=ha, va='center',
            fontsize=14, color=wcolors[i], fontweight='bold',
            linespacing=1.4,
            arrowprops=dict(arrowstyle='-', color=wcolors[i], lw=1.2),
        )

    # 중앙 핵심 수치
    helpful = vals_3[0] + vals_3[1]
    ax.text(0, 0.08, f'{helpful:.1f}%',
            ha='center', va='center',
            fontsize=42, fontweight='bold', color='#1D4ED8')
    ax.text(0, -0.18, '독서가 도움이 된다',
            ha='center', va='center',
            fontsize=16, color='#1D4ED8')

    ax.set_title('독서가 도움이 된다고 생각하는가? (전체, N=2,486)\n2025 국민독서실태조사',
                 fontsize=17, fontweight='bold', pad=18, color=DARK)

    plt.tight_layout()
    path = f'{OUT}/q6_reading_helpfulness.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close()
    print(f'저장: {path}')


# ── Q14 도서 선호 분야 ────────────────────────────────────────────────────────
def make_q14():
    q14_short = ['소설·동화', '그림책', '취미·오락·여행',
                 '과학·기술·컴퓨터', '동시·시', '역사·지리',
                 '자기계발', '경제·경영', '철학·사상·종교',
                 '수필', '정치·사회·시사']
    q14 = get_rows([3590, 3591, 3592, 3593], 3, 3+len(q14_short))

    # 전체 기준 상위 8개
    sorted_idx = sorted(range(len(q14_short)),
                        key=lambda i: q14['전체'][i], reverse=True)[:8]
    top_labels = [q14_short[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(15, 7))
    fig.patch.set_facecolor(WHITE)

    bar_colors = ['#6B7280', '#F59E0B', '#10B981', '#2563EB']
    n_bars = len(schools_kr)
    x = np.arange(len(top_labels))
    bw = 0.18

    for i, (school, color) in enumerate(zip(schools_kr, bar_colors)):
        vals = [q14[school][j] for j in sorted_idx]
        offset = (i - n_bars/2 + 0.5) * bw
        bars = ax.bar(x + offset, vals, width=bw,
                      label=school, color=color, alpha=0.9)
        for bar, val in zip(bars, vals):
            if val >= 3:
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.4,
                        f'{val:.0f}',
                        ha='center', va='bottom',
                        fontsize=10, color=DARK, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(top_labels, fontsize=13)
    ax.set_ylabel('비율 (%)', fontsize=13)
    ax.set_ylim(0, 62)
    ax.set_title('Q14. 도서 선호 분야 — 학교급별 비교 (종이책, 1순위)\n2025 국민독서실태조사',
                 fontsize=16, fontweight='bold', pad=12)
    ax.legend(fontsize=12, framealpha=0.9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis='y', labelsize=12)

    # 편중 강조 어노테이션 (글자 크게)
    ax.axvspan(-0.45, 0.45, alpha=0.06, color=RED_C)
    ax.annotate('중·고등학생 50% 이상\n소설·동화에만 집중\n→ 다양한 분야 탐색 필요',
                xy=(0, 53), xytext=(1.2, 57),
                fontsize=13, color=RED_C, fontweight='bold',
                linespacing=1.5,
                arrowprops=dict(arrowstyle='->', color=RED_C, lw=2.0))

    plt.tight_layout()
    path = f'{OUT}/q14_book_genre_preference.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close()
    print(f'저장: {path}')


# ── Q15 도서 선택 방법 ────────────────────────────────────────────────────────
def make_q15():
    q15_short = ['서점·도서관\n직접 선택', 'SNS·인터넷\n소개',
                 '학교 추천', '주변 사람\n추천',
                 '유튜브·팟캐스트', '베스트셀러',
                 '드라마·영화\n원작', '기타', '신문·방송\n소개']
    q15 = get_rows([3968, 3969, 3970, 3971], 3, 3+len(q15_short))

    # 상위 6개
    sorted_idx = sorted(range(len(q15_short)),
                        key=lambda i: q15['전체'][i], reverse=True)[:6]
    top_labels = [q15_short[i] for i in sorted_idx]

    fig, ax = plt.subplots(figsize=(14, 6.5))
    fig.patch.set_facecolor(WHITE)

    palette = ['#1D4ED8', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE']
    y = np.arange(len(schools_kr))
    lefts = np.zeros(len(schools_kr))

    for i, (label, color) in enumerate(zip(top_labels, palette)):
        idx = sorted_idx[i]
        vals = [q15[s][idx] for s in schools_kr]
        bars = ax.barh(y, vals, left=lefts, color=color,
                       label=label.replace('\n', ' '), height=0.5)
        for j, (bar, val) in enumerate(zip(bars, vals)):
            if val > 4:
                ax.text(lefts[j] + val/2,
                        bar.get_y() + bar.get_height()/2,
                        f'{val:.0f}%',
                        ha='center', va='center',
                        fontsize=11,
                        color='white' if val > 9 else DARK,
                        fontweight='bold')
        lefts += np.array(vals)

    ax.set_yticks(y)
    ax.set_yticklabels(schools_kr, fontsize=14)
    ax.set_xlabel('비율 (%)', fontsize=13)
    ax.set_title('Q15. 도서 선택 시 이용 정보 — 학교급별\n2025 국민독서실태조사',
                 fontsize=16, fontweight='bold', pad=12)
    ax.legend(loc='lower right', fontsize=11, framealpha=0.9, ncol=2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', labelsize=12)

    # 하단 설명 텍스트
    직접_전체 = q15['전체'][0]
    ax.text(0.5, -0.18,
            f'서점·도서관 직접 선택 {직접_전체:.0f}% 1위 — 물리적 탐색이 주류, 온라인 우연 발견 경험 부재',
            transform=ax.transAxes, ha='center',
            fontsize=13, color=BLUE, fontweight='bold')

    plt.tight_layout()
    path = f'{OUT}/q15_book_selection_method.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=WHITE)
    plt.close()
    print(f'저장: {path}')


# ── summary_insight ───────────────────────────────────────────────────────────
def make_summary():
    q6  = get_rows([559, 560, 561, 562], 3, 8)
    q14 = get_rows([3590, 3591, 3592, 3593], 3, 14)
    q15 = get_rows([3968, 3969, 3970, 3971], 3, 12)
    q34 = get_rows([8198, 8199, 8200, 8201], 3, 9)

    helpful    = q6['전체'][0] + q6['전체'][1]
    novel_pct  = q14['전체'][0]
    direct_pct = q15['전체'][0]
    wish_pct   = q34['전체'][0]

    insights = [
        ('독서 효과 인식',    f'{helpful:.1f}%',   '학생이 독서가\n도움된다고 인식',
         '→ 가치는 알지만\n탐색 도구 부재',      BLUE),
        ('선호 분야 편중',    f'{novel_pct:.1f}%',  '소설·동화에만\n집중',
         '→ 다양한 분야\n탐색 필요',              RED_C),
        ('책 선택 방법 1위',  f'{direct_pct:.1f}%', '서점·도서관\n직접 선택',
         '→ 온라인 우연한\n발견 경험 부재',       GREEN_C),
        ('학교에 바라는 것 1위', f'{wish_pct:.1f}%','관심에 맞는\n책 소개 원함',
         '→ BookPath의\n핵심 기능!',              PURPLE),
    ]

    fig, axes = plt.subplots(1, 4, figsize=(18, 6.5))
    fig.patch.set_facecolor(GRAY_BG)

    for ax, (title, value, sub, detail, color) in zip(axes, insights):
        ax.set_facecolor(WHITE)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.04, 0.04), 0.92, 0.92, boxstyle='round,pad=0.02',
            facecolor=WHITE, edgecolor=color, linewidth=3))
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.04, 0.86), 0.92, 0.10, boxstyle='round,pad=0.01',
            facecolor=color, edgecolor='none'))
        ax.text(0.5, 0.915, title, ha='center', va='center',
                fontsize=14, fontweight='bold', color=WHITE)
        ax.text(0.5, 0.63, value, ha='center', va='center',
                fontsize=38, fontweight='bold', color=color)
        ax.text(0.5, 0.42, sub, ha='center', va='center',
                fontsize=13, color=DARK, linespacing=1.5)
        ax.plot([0.15, 0.85], [0.28, 0.28], color='#E5E7EB', lw=1.2)
        ax.text(0.5, 0.16, detail, ha='center', va='center',
                fontsize=12, color=color, fontstyle='italic', linespacing=1.5)

    plt.suptitle('BookPath 필요성 — 핵심 데이터 근거 (2025 국민독서실태조사)',
                 fontsize=17, fontweight='bold', y=1.01, color=DARK)
    plt.tight_layout(pad=1.2)
    path = f'{OUT}/summary_insight.png'
    plt.savefig(path, dpi=180, bbox_inches='tight', facecolor=GRAY_BG)
    plt.close()
    print(f'저장: {path}')


# ── Q34 학교에 바라는 점 ──────────────────────────────────────────────────────
def make_q34():
    q34_short = ['내 관심에 맞는\n책 소개', '도서관 편하게\n이용',
                 '교실 학급문고\n확충', '독서 시간\n확대',
                 '독서 행사\n다양화', '독서 방법\n지도']
    q34 = get_rows([8198, 8199, 8200, 8201], 3, 3+len(q34_short))

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(WHITE)

    bar_colors = ['#6B7280', '#F59E0B', '#10B981', '#2563EB']
    x = np.arange(len(q34_short))
    bw = 0.17

    for i, (school, color) in enumerate(zip(schools_kr, bar_colors)):
        vals = q34[school]
        offset = (i - 2 + 0.5) * bw
        bars = ax.bar(x + offset, vals, width=bw,
                      label=school, color=color, alpha=0.9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.4,
                    f'{val:.0f}',
                    ha='center', va='bottom',
                    fontsize=11, color=DARK, fontweight='bold')

    ax.axvspan(-0.45, 0.45, alpha=0.07, color=BLUE)
    ax.text(0, 40.5, '전교급 1위\n→ BookPath가 직접 해결!',
            ha='center', va='bottom',
            fontsize=14, color=BLUE, fontweight='bold', linespacing=1.4)

    ax.set_xticks(x)
    ax.set_xticklabels(q34_short, fontsize=13, linespacing=1.4)
    ax.set_ylabel('비율 (%)', fontsize=13)
    ax.set_ylim(0, 46)
    ax.set_title('학교 독서 환경에서 바라는 점 (1순위) — 학교급별\n2025 국민독서실태조사',
                 fontsize=16, fontweight='bold', pad=12)
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
    make_q6()
    make_q14()
    make_q15()
    make_summary()
    make_q34()
    print('\n전체 완료!')
