import datetime
import calendar
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

# -----------------------
# 1) USER CONFIGURATION
# -----------------------
ACADEMIC_START   = datetime.date(2025, 8, 14)
LAST_DAY         = datetime.date(2026, 6, 5)
C_DAY            = ACADEMIC_START

RECESS_DATES = [
    *(datetime.date(2025, 11, d) for d in range(24, 29)),  # Thanksgiving week
    *(datetime.date(2025, 12, d) for d in range(22, 32)),  # Winter break start
    *(datetime.date(2026,  1, d) for d in range(1,  3)),   # Winter break end
    *(datetime.date(2026,  3, d) for d in range(23, 28)),  # Spring break
]

LEGAL_HOLIDAYS = [
    datetime.date(2025,  9,  1),
    datetime.date(2025, 11, 11),
    datetime.date(2026,  1, 19),
    datetime.date(2026,  2, 16),
    datetime.date(2026,  5, 25),
    datetime.date(2026,  6, 19),
]

TEACHER_PLANNING = [
    datetime.date(2025,  8, 11),
    datetime.date(2025,  8, 12),
    datetime.date(2025,  8, 13),
    datetime.date(2025,  9, 23),
    datetime.date(2025, 10,  2),
    datetime.date(2025, 11,  3),
    datetime.date(2026,  1, 16),
    datetime.date(2026,  3, 20),
    datetime.date(2026,  4,  3),
    datetime.date(2026,  6,  5),
]

GRADING_DATES = [
    datetime.date(2025,  8, 14),
    datetime.date(2025, 10, 17),
    datetime.date(2025, 10, 20),
    datetime.date(2026,  1, 15),
    datetime.date(2026,  1, 20),
    datetime.date(2026,  4,  2),
    datetime.date(2026,  4,  6),
    datetime.date(2026,  6,  4),
]

# -----------------------
# 2) SETUP
# -----------------------
calendar.setfirstweekday(calendar.SUNDAY)

def is_instruction_day(d):
    return d >= ACADEMIC_START and d.weekday() < 5 and d not in RECESS_DATES and d <= LAST_DAY

# -----------------------
# 3) ASSIGN DAY TYPES
# -----------------------
day_type = {}
counter = 0

# Start from earliest planning day so June 5 is included
start_date = min(ACADEMIC_START, *TEACHER_PLANNING)

d = start_date
while d <= LAST_DAY:
    if d in TEACHER_PLANNING:
        day_type[d] = 'Planning'
    elif d == C_DAY:
        day_type[d] = 'C'
    elif d in LEGAL_HOLIDAYS:
        day_type[d] = 'Legal'
    elif is_instruction_day(d):
        day_type[d] = 'A' if (counter % 2) == 0 else 'B'
        counter += 1
    d += datetime.timedelta(days=1)

# -----------------------
# 4) FILL NON-INSTRUCTION
# -----------------------
d = start_date
while d <= LAST_DAY:
    if d not in day_type:
        if d in RECESS_DATES:
            day_type[d] = 'Recess'
        elif d.weekday() >= 5:
            day_type[d] = 'Weekend'
        else:
            day_type[d] = 'Holiday'
    d += datetime.timedelta(days=1)

# -----------------------
# 5) COLOR MAP
# -----------------------
COLOR_MAP = {
    'A':        '#e74c3c',   # red
    'B':        '#f1c40f',   # gold
    'C':        '#2ecc71',   # green
    'Legal':    '#9b59b6',   # purple
    'Planning': '#add8e6',   # light blue
    'Recess':   '#cccccc',   # gray
    'Weekend':  '#ffffff',   # white
    'Holiday':  '#ffffff',   # white
}

# -----------------------
# 6) BUILD MONTH LIST
# -----------------------
months = []
y, m = ACADEMIC_START.year, ACADEMIC_START.month
while (y, m) <= (LAST_DAY.year, LAST_DAY.month):
    months.append((y, m))
    m += 1
    if m > 12:
        m, y = 1, y + 1

total = len(months)
ncols = 4
nrows = (total + ncols - 1) // ncols

# -----------------------
# 7) DRAW CALENDARS
# -----------------------
fig = plt.figure(figsize=(ncols * 4, nrows * 4))
overlays = []

for idx, (yr, mo) in enumerate(months):
    ax = fig.add_subplot(nrows, ncols, idx + 1)
    short_year = f"'{yr % 100:02d}"
    ax.set_title(f"{calendar.month_name[mo]} {short_year}", fontsize=18, x=0.5)
    ax.axis('off')

    mat = calendar.monthcalendar(yr, mo)
    txt_rows, col_rows = [], []
    for week in mat:
        rtxt, rcol = [], []
        for day in week:
            if day == 0:
                rtxt.append('')
                rcol.append('#ffffff')
            else:
                dt = datetime.date(yr, mo, day)
                rtxt.append(str(day))
                # ensure legal holidays beyond LAST_DAY still colored
                if dt in LEGAL_HOLIDAYS:
                    rcol.append(COLOR_MAP['Legal'])
                else:
                    rcol.append(COLOR_MAP.get(day_type.get(dt), '#ffffff'))
        txt_rows.append(rtxt)
        col_rows.append(rcol)

    tbl = ax.table(
        cellText    = txt_rows,
        cellColours = col_rows,
        cellLoc     = 'center',
        colLabels   = ['Su','M','T','W','Th','F','Sa'],
        bbox        = [0, 0, 1, 0.95],
    )
    tbl.scale(1.5, 2.5)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(16)
    ax.set_ylim(len(mat) * 2.5, 0)

    overlays.append((tbl, mat, yr, mo))

# -----------------------
# 8) LEGEND & LAYOUT
# -----------------------
legend_items = [
    Patch(color=COLOR_MAP['C'],        label='C Day'),
    Patch(color=COLOR_MAP['Planning'], label='Teacher Planning Day'),
    Patch(color=COLOR_MAP['A'],        label='A Day'),
    Patch(color=COLOR_MAP['B'],        label='B Day'),
    Patch(color=COLOR_MAP['Legal'],    label='Legal Holiday'),
    Patch(color=COLOR_MAP['Recess'],   label='Recess'),
    Patch(facecolor='none', edgecolor='black', linewidth=3,
          label='Start/End of Grading Period'),
]

fig.subplots_adjust(
    top=0.96,
    bottom=0.18,
    left=0.02,
    right=0.98,
    hspace=0.3,
    wspace=0.3,
)

fig.legend(
    handles        = legend_items,
    loc            = 'lower center',
    bbox_to_anchor = (0.5, 0.02),
    ncol           = 4,
    fontsize       = 16,
    frameon        = False,
)

# -----------------------
# 9) OVERLAY SYMBOLS
# -----------------------
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

for tbl, mat, yr, mo in overlays:
    for r, week in enumerate(mat, start=1):
        for c, day in enumerate(week):
            if not day:
                continue
            dt = datetime.date(yr, mo, day)
            bbox = tbl[r, c].get_window_extent(renderer)
            inv = fig.transFigure.inverted()
            x0, y0 = inv.transform((bbox.x0, bbox.y0))
            x1, y1 = inv.transform((bbox.x1, bbox.y1))
            cx, cy = (x0 + x1)/2, (y0 + y1)/2

            if dt in LEGAL_HOLIDAYS:
                fig.text(cx, cy, '✕',
                         ha='center', va='center',
                         fontsize=20, fontweight='bold',
                         transform=fig.transFigure)
            if dt in TEACHER_PLANNING:
                fig.text(cx, cy, '◯',
                         ha='center', va='center',
                         fontsize=20, fontweight='bold',
                         transform=fig.transFigure)
            if dt in GRADING_DATES:
                rect = Rectangle((x0, y0), x1 - x0, y1 - y0,
                                 fill=False, edgecolor='black',
                                 linewidth=4,
                                 transform=fig.transFigure)
                fig.add_artist(rect)

# -----------------------
# 10) SAVE OUTPUT
# -----------------------
outfile = f"academic_calendar_{ACADEMIC_START.year}_{LAST_DAY.year}"
plt.savefig(outfile + ".png", dpi=200)
plt.savefig(outfile + ".pdf")
plt.close()
print(f"Saved {outfile}.png and {outfile}.pdf")
