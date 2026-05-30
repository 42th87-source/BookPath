import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# 한글 폰트 설정
for fname in fm.findSystemFonts():
    if 'malgun' in fname.lower() or 'nanumgothic' in fname.lower():
        plt.rcParams['font.family'] = fm.FontProperties(fname=fname).get_name()
        break

fig, ax = plt.subplots(figsize=(16, 7))
ax.set_xlim(0, 16)
ax.set_ylim(0, 7)
ax.axis('off')
fig.patch.set_facecolor('white')

# 색상
INDIGO  = '#4f46e5'
PURPLE  = '#7c3aed'
GREEN   = '#10b981'
GRAY    = '#f1f5f9'
DARK    = '#1e293b'
MUTED   = '#64748b'
WHITE   = 'white'

steps = [
    {
        'icon': 'API',
        'title': '사서 추천 도서\nOpen API',
        'desc': '한국문화정보원',
        'stat': '7,085건 수집',
        'color': INDIGO,
    },
    {
        'icon': 'Filter',
        'title': '비도서\n필터링',
        'desc': '공지·행사 제거',
        'stat': '→ 5,050권',
        'color': PURPLE,
    },
    {
        'icon': 'AI ①',
        'title': 'AI 1단계\n태깅',
        'desc': 'KDC·진로·키워드',
        'stat': '약 2시간',
        'color': '#7c3aed',
    },
    {
        'icon': 'AI ②',
        'title': 'AI 2단계\nthemes',
        'desc': 'cross-KDC 연결키',
        'stat': '약 30분',
        'color': '#059669',
    },
    {
        'icon': 'Web',
        'title': 'BookPath\n웹 서비스',
        'desc': 'GitHub Pages',
        'stat': '5,050권 서비스',
        'color': INDIGO,
    },
]

box_w = 2.2
box_h = 2.8
gap   = 0.6
start_x = 0.5
y_top = 4.8

for i, step in enumerate(steps):
    x = start_x + i * (box_w + gap)

    # 박스
    rect = mpatches.FancyBboxPatch(
        (x, y_top - box_h), box_w, box_h,
        boxstyle="round,pad=0.1",
        facecolor=step['color'], edgecolor='white', linewidth=2,
        zorder=3
    )
    ax.add_patch(rect)

    # 아이콘
    ax.text(x + box_w/2, y_top - 0.45, step['icon'],
            ha='center', va='center', fontsize=22, zorder=4)

    # 제목
    ax.text(x + box_w/2, y_top - 1.35, step['title'],
            ha='center', va='center', fontsize=10.5, fontweight='bold',
            color=WHITE, zorder=4, linespacing=1.4)

    # 설명
    ax.text(x + box_w/2, y_top - 2.15, step['desc'],
            ha='center', va='center', fontsize=8.5,
            color='#c4b5fd' if step['color'] != GREEN else '#6ee7b7',
            zorder=4)

    # 수치 (박스 아래)
    stat_bg = mpatches.FancyBboxPatch(
        (x + 0.1, y_top - box_h - 0.7), box_w - 0.2, 0.55,
        boxstyle="round,pad=0.05",
        facecolor=GRAY, edgecolor=step['color'], linewidth=1.5, zorder=3
    )
    ax.add_patch(stat_bg)
    ax.text(x + box_w/2, y_top - box_h - 0.42, step['stat'],
            ha='center', va='center', fontsize=9, fontweight='bold',
            color=step['color'], zorder=4)

    # 화살표
    if i < len(steps) - 1:
        arrow_x = x + box_w + 0.05
        arrow_y = y_top - box_h/2
        ax.annotate('',
            xy=(arrow_x + gap - 0.1, arrow_y),
            xytext=(arrow_x, arrow_y),
            arrowprops=dict(arrowstyle='->', color=MUTED,
                           lw=2.5, mutation_scale=20),
            zorder=5
        )

# 하단 박스: KDC 대신 AI 이유
reason_y = 1.8
rect2 = mpatches.FancyBboxPatch(
    (0.3, 0.15), 15.4, reason_y,
    boxstyle="round,pad=0.1",
    facecolor=GRAY, edgecolor='#e2e8f0', linewidth=1.5, zorder=2
)
ax.add_patch(rect2)

ax.text(8, 1.75, 'KDC 세부코드 대신 AI를 사용한 이유',
        ha='center', va='center', fontsize=11, fontweight='bold',
        color=DARK, zorder=3)

reasons = [
    ('X', 'KDC API', '사용한 사서 추천 도서 API에서 KDC 세부코드 미제공'),
    ('X', '규칙 기반', '문맥 이해 불가 — 학생 친화 태그·진로 연결 생성 불가'),
    ('O', 'Gemini AI', '내용 이해 기반 → 진로 연결 + 학생 친화 태그 + themes 동시 생성'),
]

cols_x = [1.2, 1.8, 3.0]
for j, (icon, label, desc) in enumerate(reasons):
    y_r = 1.22 - j * 0.38
    color = '#ef4444' if icon == '❌' else '#10b981'
    ax.text(cols_x[0], y_r, icon, ha='center', va='center',
            fontsize=11, zorder=3)
    ax.text(cols_x[1], y_r, label, ha='left', va='center',
            fontsize=9.5, fontweight='bold', color=color, zorder=3)
    ax.text(cols_x[2], y_r, desc, ha='left', va='center',
            fontsize=9, color=DARK, zorder=3)

plt.tight_layout(pad=0.2)
out = 'analysis/graphs/data_flow_chart.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print(f'저장 완료: {out}')
