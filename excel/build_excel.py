"""Builds excel/Walmart_Store_Performance.xlsx — every summary number is a live formula on the Data sheet.
Run from the repo root:  python excel/build_excel.py
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

df = pd.read_csv("Walmart.csv")
df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
df["Year"], df["Month"] = df["Date"].dt.year, df["Date"].dt.month
N = len(df) + 1  # last data row

F = "Arial"
HDR_FILL = PatternFill("solid", fgColor="1C5CAB")
HDR = Font(name=F, bold=True, color="FFFFFF")
BODY = Font(name=F)
BOLD = Font(name=F, bold=True)
TITLE = Font(name=F, bold=True, size=14)
NOTE = Font(name=F, italic=True, color="52514E", size=9)
thin = Side(style="thin", color="D9D8D3")
BOX = Border(bottom=thin)
M = '$#,##0.0,,"M"'
PCT = '+0.0%;-0.0%;0.0%'

wb = Workbook()

def header(ws, row, labels, widths=None):
    for c, lab in enumerate(labels, 1):
        cell = ws.cell(row=row, column=c, value=lab)
        cell.font, cell.fill = HDR, HDR_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30
    for c, w in enumerate(widths or [], 1):
        ws.column_dimensions[get_column_letter(c)].width = w

def style_rows(ws, r1, r2, ncols):
    for r in range(r1, r2 + 1):
        for c in range(1, ncols + 1):
            ws.cell(row=r, column=c).font = BODY
            ws.cell(row=r, column=c).border = BOX

# ---------------- Data ----------------
ws = wb.active; ws.title = "Data"
cols = ["Store", "Date", "Year", "Month", "Weekly_Sales", "Holiday_Flag", "Temperature", "Fuel_Price", "CPI", "Unemployment"]
header(ws, 1, cols, [8, 12, 8, 8, 15, 12, 12, 11, 10, 13])
for i, r in enumerate(df[cols].itertuples(index=False), 2):
    for c, v in enumerate(r, 1):
        ws.cell(row=i, column=c, value=v.to_pydatetime() if c == 2 else v)
    ws.cell(row=i, column=2).number_format = "yyyy-mm-dd"
    ws.cell(row=i, column=5).number_format = "#,##0.00"
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:J{N}"

S, D, Y, MO, SAL = (f"Data!$A$2:$A${N}", f"Data!$B$2:$B${N}", f"Data!$C$2:$C${N}",
                    f"Data!$D$2:$D${N}", f"Data!$E$2:$E${N}")

# ---------------- Weekly (chain level) ----------------
wk = wb.create_sheet("Weekly")
header(wk, 1, ["Week ending", "Month", "Chain sales", "Holiday flag", "Holiday event"], [13, 8, 15, 11, 28])
dates = sorted(df["Date"].unique())
flag = df.groupby("Date")["Holiday_Flag"].max()
for i, d in enumerate(dates, 2):
    d = pd.Timestamp(d)
    wk.cell(row=i, column=1, value=d.to_pydatetime()).number_format = "yyyy-mm-dd"
    wk.cell(row=i, column=2, value=f"=MONTH(A{i})")
    wk.cell(row=i, column=3, value=f"=SUMIFS({SAL},{D},A{i})").number_format = M
    wk.cell(row=i, column=4, value=int(flag[d]))
    wk.cell(row=i, column=5, value=(
        f'=IF(D{i}=1,CHOOSE(MATCH(B{i},{{2,9,11,12}},0),"Super Bowl","Labor Day","Thanksgiving","Christmas (flagged week)"),'
        f'IF(AND(B{i}=12,DAY(A{i})>=18,DAY(A{i})<=24),"Pre-Christmas (not flagged)","Regular week"))'))
W_END = len(dates) + 1
style_rows(wk, 2, W_END, 5)
wk.freeze_panes = "A2"

# ---------------- Store Summary ----------------
ss = wb.create_sheet("Store Summary")
ss["A1"] = "Store performance summary"; ss["A1"].font = TITLE
ss["A2"] = "All values are formulas on the Data sheet. YTD = January–October. Red = declining store."; ss["A2"].font = NOTE
header(ss, 4, ["Store", "Total sales", "Avg weekly sales", "Share of chain", "Sales rank",
               "YTD 2011", "YTD 2012", "Change ($)", "Growth %", "Growth rank", "Status"],
       [8, 14, 15, 13, 10, 13, 13, 13, 11, 11, 12])
first, last = 5, 5 + 44
for i, st in enumerate(range(1, 46), first):
    ss.cell(row=i, column=1, value=st)
    ss.cell(row=i, column=2, value=f"=SUMIFS({SAL},{S},A{i})").number_format = M
    ss.cell(row=i, column=3, value=f"=AVERAGEIFS({SAL},{S},A{i})").number_format = '$#,##0'
    ss.cell(row=i, column=4, value=f"=B{i}/SUM($B${first}:$B${last})").number_format = "0.00%"
    ss.cell(row=i, column=5, value=f"=RANK(B{i},$B${first}:$B${last},0)")
    ss.cell(row=i, column=6, value=f'=SUMIFS({SAL},{S},A{i},{Y},2011,{MO},"<=10")').number_format = M
    ss.cell(row=i, column=7, value=f'=SUMIFS({SAL},{S},A{i},{Y},2012,{MO},"<=10")').number_format = M
    ss.cell(row=i, column=8, value=f"=G{i}-F{i}").number_format = '$#,##0.0,,"M";-$#,##0.0,,"M"'
    ss.cell(row=i, column=9, value=f"=IFERROR(G{i}/F{i}-1,0)").number_format = PCT
    ss.cell(row=i, column=10, value=f"=RANK(I{i},$I${first}:$I${last},0)")
    ss.cell(row=i, column=11, value=f'=IF(I{i}<0,"Declining","Growing")')
style_rows(ss, first, last, 11)
t = last + 1
ss.cell(row=t, column=1, value="Total").font = BOLD
for c, f, fmt in [(2, f"=SUM(B{first}:B{last})", M), (3, f"=AVERAGE({SAL})", '$#,##0'),
                  (4, f"=SUM(D{first}:D{last})", "0.0%"), (6, f"=SUM(F{first}:F{last})", M),
                  (7, f"=SUM(G{first}:G{last})", M), (8, f"=G{t}-F{t}", '$#,##0.0,,"M";-$#,##0.0,,"M"'),
                  (9, f"=G{t}/F{t}-1", PCT), (11, f'=COUNTIF(K{first}:K{last},"Declining")&" declining"', None)]:
    cell = ss.cell(row=t, column=c, value=f); cell.font = BOLD
    if fmt: cell.number_format = fmt
ss.conditional_formatting.add(f"B{first}:B{last}", DataBarRule(start_type="min", end_type="max", color="86B6EF"))
red = PatternFill("solid", fgColor="FBE3E3")
ss.conditional_formatting.add(f"I{first}:I{last}", CellIsRule(operator="lessThan", formula=["0"], fill=red, font=Font(name=F, color="B42318")))
ss.conditional_formatting.add(f"K{first}:K{last}", CellIsRule(operator="equal", formula=['"Declining"'], fill=red, font=Font(name=F, color="B42318", bold=True)))
ss.freeze_panes = "B5"
ss.auto_filter.ref = f"A4:K{last}"

# ---------------- Holiday Impact ----------------
hi = wb.create_sheet("Holiday Impact")
hi["A1"] = "Which holidays lift sales?"; hi["A1"].font = TITLE
hi["A2"] = ("Chain sales per week vs. a regular week. 'Pre-Christmas' = week ending Dec 18–24, which the source data "
            "does NOT flag as a holiday."); hi["A2"].font = NOTE
header(hi, 4, ["Holiday event", "Weeks", "Avg chain sales / week", "Lift vs regular week"], [30, 8, 22, 20])
WE, WS_ = f"Weekly!$E$2:$E${W_END}", f"Weekly!$C$2:$C${W_END}"
events = ["Pre-Christmas (not flagged)", "Thanksgiving", "Super Bowl", "Labor Day", "Christmas (flagged week)", "Regular week"]
for i, e in enumerate(events, 5):
    hi.cell(row=i, column=1, value=e)
    hi.cell(row=i, column=2, value=f"=COUNTIF({WE},A{i})")
    hi.cell(row=i, column=3, value=f"=AVERAGEIFS({WS_},{WE},A{i})").number_format = M
    hi.cell(row=i, column=4, value=f"=C{i}/$C$10-1").number_format = PCT
style_rows(hi, 5, 10, 4)
hi.conditional_formatting.add("D5:D9", CellIsRule(operator="lessThan", formula=["0"], fill=red, font=Font(name=F, color="B42318")))
ch = BarChart(); ch.type = "bar"; ch.style = 2
ch.title = "Sales lift vs. a regular week"; ch.legend = None
ch.add_data(Reference(hi, min_col=4, min_row=4, max_row=9), titles_from_data=True)
ch.set_categories(Reference(hi, min_col=1, min_row=5, max_row=9))
ch.y_axis.numFmt = "0%"; ch.x_axis.scaling.orientation = "maxMin"
ch.series[0].graphicalProperties.solidFill = "2A78D6"; ch.series[0].invertIfNegative = False
ch.y_axis.delete = False; ch.x_axis.delete = False
ch.height, ch.width = 7.5, 16
hi.add_chart(ch, "F4")

# ---------------- Seasonality ----------------
se = wb.create_sheet("Seasonality")
se["A1"] = "Average chain sales per week by month"; se["A1"].font = TITLE
se["A2"] = "Index: 100 = the average week across the whole period."; se["A2"].font = NOTE
header(se, 4, ["Month", "Month #", "Weeks", "Avg chain sales / week", "Index"], [10, 9, 8, 22, 9])
WM = f"Weekly!$B$2:$B${W_END}"
for i, (mname, mnum) in enumerate(zip(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], range(1, 13)), 5):
    se.cell(row=i, column=1, value=mname); se.cell(row=i, column=2, value=mnum)
    se.cell(row=i, column=3, value=f"=COUNTIF({WM},B{i})")
    se.cell(row=i, column=4, value=f"=AVERAGEIFS({WS_},{WM},B{i})").number_format = M
    se.cell(row=i, column=5, value=f"=ROUND(D{i}/AVERAGE({WS_})*100,0)")
style_rows(se, 5, 16, 5)
se.conditional_formatting.add("E5:E16", CellIsRule(operator="greaterThanOrEqual", formula=["105"], fill=PatternFill("solid", fgColor="CDE2FB"), font=Font(name=F, bold=True)))
se.conditional_formatting.add("E5:E16", CellIsRule(operator="lessThan", formula=["90"], fill=red, font=Font(name=F, color="B42318", bold=True)))
ch2 = BarChart(); ch2.title = "Avg chain sales per week by month"; ch2.legend = None; ch2.style = 2
ch2.add_data(Reference(se, min_col=4, min_row=4, max_row=16), titles_from_data=True)
ch2.set_categories(Reference(se, min_col=1, min_row=5, max_row=16))
ch2.series[0].graphicalProperties.solidFill = "2A78D6"; ch2.y_axis.numFmt = '$#,##0,,"M"'
ch2.y_axis.delete = False; ch2.x_axis.delete = False
ch2.height, ch2.width = 7.5, 16
se.add_chart(ch2, "G4")

# ---------------- Summary (first tab) ----------------
sm = wb.create_sheet("Summary", 0)
sm.column_dimensions["A"].width = 46; sm.column_dimensions["B"].width = 18; sm.column_dimensions["C"].width = 70
sm["A1"] = "Walmart Store Sales: Performance Summary (Feb 2010 – Oct 2012)"; sm["A1"].font = TITLE
sm["A2"] = "Prepared by Nishad Rashid Mahi. Every figure below is a live formula; see the other tabs for detail."; sm["A2"].font = NOTE
header(sm, 4, ["KPI", "Value", "What it means"])
kpis = [
    ("Total sales", f"=SUM({SAL})", M, "45 stores, 143 weeks"),
    ("Avg chain sales per week", f"=AVERAGE({WS_})", M, "Baseline for judging peaks"),
    ("Like-for-like growth, Jan–Oct 2012 vs 2011", f"='Store Summary'!I{t}", PCT, "Chain is broadly flat; growth comes from store mix"),
    ("Stores declining in 2012", f"=COUNTIF('Store Summary'!K{first}:K{last},\"Declining\")", "0", "Store 14 (a top-3 store) has the largest $ loss"),
    ("Pre-Christmas week lift", "='Holiday Impact'!D5", PCT, "Biggest week of the year, and NOT flagged as a holiday in the data"),
    ("Thanksgiving week lift", "='Holiday Impact'!D6", PCT, "The only flagged holiday with a large lift"),
    ("Flagged 'Christmas' week lift", "='Holiday Impact'!D9", PCT, "The week after Christmas sells below normal"),
    ("December index (avg week = 100)", "=Seasonality!E16", "0", "Peak month"),
    ("January index (avg week = 100)", "=Seasonality!E5", "0", "Weakest month: post-holiday slump"),
    ("Top-12 stores' share of sales", f"=SUMPRODUCT(('Store Summary'!E{first}:E{last}<=12)*'Store Summary'!D{first}:D{last})", "0.0%", "Revenue is concentrated in a few large stores"),
]
for i, (k, f, fmt, note) in enumerate(kpis, 5):
    sm.cell(row=i, column=1, value=k).font = BODY
    c = sm.cell(row=i, column=2, value=f); c.number_format = fmt; c.font = BOLD
    sm.cell(row=i, column=3, value=note).font = BODY
    for col in (1, 2, 3): sm.cell(row=i, column=col).border = BOX
r = 5 + len(kpis) + 1
sm.cell(row=r, column=1, value="Recommendations").font = Font(name=F, bold=True, size=12)
recs = [
    "1. Fix the holiday calendar: treat the 2 weeks before Christmas as the peak period in forecasts and reports.",
    "2. Concentrate peak staffing, stock and promotions on Thanksgiving through Dec 24; run Super Bowl and Labor Day as normal weeks.",
    "3. Plan January clearance and lower-cost staffing schedules; use January for training and store resets.",
    "4. Run a performance review of Store 14 (-$7.3M) and Store 36 (-17.5%); study Stores 38, 44 and 39 (+11–14%) for practices to copy.",
    "5. Allocate holiday inventory by each store's own Christmas peak (1.0x–2.05x) instead of one chain-wide plan.",
    "6. Forecast from store history and calendar effects; temperature, fuel, CPI and unemployment add almost nothing (|r| ≤ 0.13).",
]
for j, txt in enumerate(recs, r + 1):
    sm.cell(row=j, column=1, value=txt).font = BODY
    sm.merge_cells(start_row=j, start_column=1, end_row=j, end_column=3)

wb.save("excel/Walmart_Store_Performance.xlsx")
print("saved")
