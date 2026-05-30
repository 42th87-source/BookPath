import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# 한글 폰트
for fname in fm.findSystemFonts():
    if 'malgun' in fname.lower():
        plt.rcParams['font.family'] = fm.FontProperties(fname=fname).get_name()
        break

# PPT 디자인 색상
WHITE   = '#ffffff'
DARK    = '#111827'
BLUE    = '#2563eb'
BLUE_LT = '#eff6ff'
BLUE_MD = '#bfdbfe'
MUTED   = '#6b7280'
GRAY_BG = '#f9fafb'
GRAY_BD = '#e5e7eb'
RED_C   = '#ef4444'
GREEN_C = '#16a34a'
NUM_C   = '#3b82f6'

def txt(ax, s, x, y, size=12, bold=False, color=DARK, ha='center', va='center'):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size,
            fontweight='bold' if bold else 'normal',
            color=color, zorder=4)

def rbox(ax, x, y, w, h, fc=BLUE_LT, ec=BLUE_MD, lw=1.2, r=0.06):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3))

# ── 캔버스 ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(17, 6.2))
ax.set_xlim(0, 17)
ax.set_ylim(0, 6.2)
ax.axis('off')
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# ── 흐름 단계 ─────────────────────────────────────────────────────────────────
steps = [
    ('01', '데이터 수집',       '사서 추천 도서\nOpen API\n7,085건',    False),
    ('02', '비도서 필터링',     '공지·행사 제거\n→ 5,050권',            False),
    ('03', 'AI 1단계 태깅',     'KDC·진로태그\n키워드 생성\n약 2시간',  False),
    ('04', 'AI 2단계 Themes',   'cross-KDC\n연결 키워드\n약 30분',      False),
    ('05', '웹 서비스 제공',    'BookPath\n5,050권 서비스',              True),
]

sw = 2.72
gw = 0.25
total = len(steps) * sw + (len(steps) - 1) * gw
sx = (17 - total) / 2
yb = 2.7
bh = 3.0

for i, (num, title, desc, last) in enumerate(steps):
    x  = sx + i * (sw + gw)
    fc = BLUE    if last else BLUE_LT
    ec = BLUE    if last else BLUE_MD
    tc = WHITE   if last else DARK
    nc = WHITE   if last else NUM_C
    dc = '#bfdbfe' if last else MUTED
    lw = 0       if last else 1.2

    rbox(ax, x, yb, sw, bh, fc=fc, ec=ec, lw=lw)

    txt(ax, num,   x+sw/2, yb+bh-0.38, size=10, bold=True,  color=nc)
    txt(ax, title, x+sw/2, yb+bh-1.0,  size=13, bold=True,  color=tc)
    txt(ax, desc,  x+sw/2, yb+bh-2.15, size=9.5,            color=dc)

    if i < len(steps) - 1:
        ax.text(x+sw+gw/2, yb+bh/2, '>',
                ha='center', va='center', fontsize=18,
                color=BLUE_MD, fontweight='bold', zorder=4)

# ── KDC 대신 AI 이유 ──────────────────────────────────────────────────────────
rbox(ax, 0.55, 0.2, 15.9, 2.15, fc=GRAY_BG, ec=GRAY_BD, lw=1, r=0.05)

txt(ax, 'KDC 세부코드 대신 AI를 사용한 이유',
    8.5, 2.1, size=11, bold=True, color=DARK)

reasons = [
    (RED_C,   'X   KDC API',   '활용한 사서 추천 도서 API에서 KDC 세부코드 미제공'),
    (RED_C,   'X   규칙 기반', '문맥 이해 불가 — 학생 친화 태그·진로 연결 생성 불가'),
    (GREEN_C, 'O   Gemini AI', '내용 이해 기반 → 진로 연결 + 학생 친화 태그 + Themes 동시 생성'),
]
for j, (col, label, desc) in enumerate(reasons):
    yr = 1.65 - j * 0.52
    txt(ax, label, 2.1, yr, size=10, bold=True, color=col, ha='left')
    txt(ax, desc,  5.6, yr, size=10,             color=DARK, ha='left')

plt.tight_layout(pad=0.05)
out = 'analysis/graphs/data_flow_chart.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor=WHITE, edgecolor='none')
plt.close()
print(f'저장 완료: {out}')
