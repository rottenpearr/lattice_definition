"""
CRIS — тестовый прогон (unit + integration).
Генерирует HTML-отчёт test_report.html
Запуск: python test_runner.py
"""
import sys, time, json, datetime
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

# ── Сборщик результатов ───────────────────────────────────────
results = []   # list of dicts: {section, name, status, detail}

def record(section, name, status, detail=""):
    results.append({"section": section, "name": name, "status": status, "detail": detail})
    icon = {"ok": "OK", "fail": "!!", "warn": "??", "info": "--"}[status]
    line = f"  [{icon}] {name}" + (f" - {detail}" if detail else "")
    print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8", errors="replace"))

def section_header(title):
    print(f"\n{'='*58}\n  {title}\n{'='*58}")


# ─────────────────────────────────────────────────────────────
# UNIT 1 — Загрузка ML-моделей
# ─────────────────────────────────────────────────────────────
section_header("UNIT 1/3 — Загрузка ML-моделей")
S = "UNIT 1 — Загрузка ML-моделей"

try:
    from cris.core.ml_predict import predict_catboost, predict_rf, predict_catboost_substance, predict_automl
    record(S, "Импорт cris.core.ml_predict", "ok")
except Exception as e:
    record(S, "Импорт cris.core.ml_predict", "fail", str(e)); sys.exit(1)

_ML = ROOT / "ML"
for name, path in [
    ("CatBoost (сингония)",  _ML / "CatBoost" / "catboost_lattice.cbm"),
    ("CatBoost (вещество)",  _ML / "CatBoost" / "catboost_substance.cbm"),
    ("Random Forest",        _ML / "rf_optimized_model.pkl"),
    ("AutoML ExtraTrees",    _ML / "AutoML"   / "extra_trees.pkl"),
]:
    if path.exists():
        record(S, f"Модель: {name}", "ok", f"{path.stat().st_size//1024} КБ")
    else:
        record(S, f"Модель: {name}", "fail", "файл не найден")


# ─────────────────────────────────────────────────────────────
# UNIT 2 — Инференс на тестовой структуре
# ─────────────────────────────────────────────────────────────
section_header("UNIT 2/3 — Инференс моделей")
S = "UNIT 2 — Инференс моделей"

xyz_files = sorted((ROOT / "data" / "structures" / "micro" / "source").glob("U*.xyz"))
test_xyz  = next((f for f in xyz_files if "UC_" in f.name or "UC2" in f.name), xyz_files[0] if xyz_files else None)

inference_rows = []  # для HTML-таблицы

if not test_xyz:
    record(S, "Тестовый XYZ-файл", "fail", "не найден")
else:
    record(S, "Тестовый файл", "info", test_xyz.name)
    lines  = test_xyz.read_text(encoding="utf-8", errors="replace").strip().splitlines()
    n      = int(lines[0].strip())
    coords = []
    for line in lines[2:2+n]:
        p = line.split()
        if len(p) >= 4:
            coords.append([p[0], float(p[1]), float(p[2]), float(p[3])])
    record(S, "Чтение координат", "ok", f"{len(coords)} атомов")

    from cris.core.coordinates import shift_coordinates, normalize_coordinates
    norm = normalize_coordinates(shift_coordinates(coords))

    for label, fn in [
        ("CatBoost · сингония",  predict_catboost),
        ("CatBoost · вещество",  predict_catboost_substance),
        ("Random Forest",        predict_rf),
        ("AutoML ExtraTrees",    predict_automl),
    ]:
        try:
            t0  = time.time()
            res = fn(norm, top_k=3)
            dt  = time.time() - t0
            if res:
                top = res[0]
                detail = f"top={top['class']}  conf={top['confidence']:.3f}  [{dt:.2f}s]"
                record(S, label, "ok", detail)
                inference_rows.append({
                    "method": label,
                    "top1": top["class"],
                    "conf": f"{top['confidence']:.3f}",
                    "top2": res[1]["class"] if len(res)>1 else "—",
                    "top3": res[2]["class"] if len(res)>2 else "—",
                    "time": f"{dt:.2f}s",
                    "status": "ok",
                })
            else:
                record(S, label, "warn", "пустой результат")
                inference_rows.append({"method": label, "top1":"—","conf":"—","top2":"—","top3":"—","time":"—","status":"warn"})
        except Exception as e:
            record(S, label, "fail", str(e))
            inference_rows.append({"method": label, "top1":"ERR","conf":"—","top2":"—","top3":"—","time":"—","status":"fail"})


# ─────────────────────────────────────────────────────────────
# UNIT 3 — БД
# ─────────────────────────────────────────────────────────────
section_header("UNIT 3/3 — База данных")
S = "UNIT 3 — База данных"
n_rr_before = 0

try:
    from cris.db.connection import get_cursor
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM reference_structure"); v = cur.fetchone()[0]
        record(S, "Таблица reference_structure", "ok", f"{v} записей")
        cur.execute("SELECT COUNT(*) FROM lattice_type"); v2 = cur.fetchone()[0]
        record(S, "Таблица lattice_type", "ok", f"{v2} типов решёток")
        cur.execute("SELECT COUNT(*) FROM recognition_session"); v3 = cur.fetchone()[0]
        record(S, "Таблица recognition_session", "ok", f"{v3} сессий")
        cur.execute("SELECT COUNT(*) FROM recognition_result"); n_rr_before = cur.fetchone()[0]
        record(S, "Таблица recognition_result", "ok", f"{n_rr_before} записей")
except Exception as e:
    record(S, "Подключение к PostgreSQL", "fail", str(e))


# ─────────────────────────────────────────────────────────────
# INTEGRATION 1 — /api/analyze сквозной инференс
# ─────────────────────────────────────────────────────────────
section_header("INTEGRATION 1/2 — Сквозной инференс /api/analyze")
S = "INTEGRATION 1 — /api/analyze"
import urllib.request, urllib.error

API = "http://localhost:8002"
api_alive = False
api_result = None

try:
    with urllib.request.urlopen(f"{API}/api/health", timeout=3) as r:
        health = json.loads(r.read())
    record(S, "API /health", "ok", f"version={health.get('version')}")
    api_alive = True
except Exception as e:
    record(S, "API /health", "fail", str(e))

if api_alive and coords:
    payload = json.dumps({
        "sites":   [{"label": c[0], "x": c[1], "y": c[2], "z": c[3]} for c in coords],
        "methods": ["db", "catboost", "catboost_substance", "rf", "automl"],
    }).encode()
    try:
        req = urllib.request.Request(f"{API}/api/analyze", data=payload,
                                     headers={"Content-Type":"application/json"}, method="POST")
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=120) as r:
            api_result = json.loads(r.read())
        dt = time.time() - t0
        record(S, "POST /api/analyze", "ok", f"{dt:.2f}s")
        record(S, "session_id создан", "ok" if api_result.get("session_id") else "warn",
               api_result.get("session_id","—"))
        if api_result.get("lattice"):
            lt = api_result["lattice"]
            record(S, "Результат БД (сингония)", "ok",
                   f"{lt.get('name_en','—')}  conf={lt.get('confidence')}")
        else:
            record(S, "Результат БД (сингония)", "warn", "совпадений не найдено")

        for mr in api_result.get("ml_results", []):
            st = "ok" if mr.get("name_en") else "warn"
            record(S, f"ML [{mr['method']}]", st,
                   f"{mr.get('name_en','—')}  {mr.get('confidence',0):.1f}%")

        with get_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM recognition_result")
            n_rr_after = cur.fetchone()[0]
        delta = n_rr_after - n_rr_before
        record(S, "Запись в recognition_result", "ok" if delta > 0 else "warn",
               f"+{delta} новых записей (итого {n_rr_after})")
    except Exception as e:
        record(S, "POST /api/analyze", "fail", str(e))


# ─────────────────────────────────────────────────────────────
# INTEGRATION 2 — Пакетный прогон по структурам
# ─────────────────────────────────────────────────────────────
section_header("INTEGRATION 2/2 — Пакетный прогон (5 структур)")
S = "INTEGRATION 2 — Пакетный прогон"

batch_rows = []
if api_alive:
    test_files = list((ROOT / "data" / "structures" / "micro" / "source").glob("U*.xyz"))[:5]
    for xyz in test_files:
        lines_ = xyz.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        n_ = int(lines_[0].strip())
        sites_ = []
        for ln in lines_[2:2+n_]:
            p = ln.split()
            if len(p) >= 4:
                sites_.append({"label": p[0], "x": float(p[1]), "y": float(p[2]), "z": float(p[3])})
        if not sites_: continue
        payload_ = json.dumps({"sites": sites_, "methods": ["catboost_substance","rf","automl"]}).encode()
        try:
            req_ = urllib.request.Request(f"{API}/api/analyze", data=payload_,
                                          headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req_, timeout=120) as r_:
                res_ = json.loads(r_.read())
            ml_ = {m["method"]: (m.get("name_en","—"), round(m.get("confidence",0),1))
                   for m in res_.get("ml_results", [])}
            row = {
                "file":     xyz.name,
                "n_atoms":  n_,
                "catboost": f"{ml_.get('catboost_substance',('—',0))[0]} ({ml_.get('catboost_substance',('—',0))[1]}%)",
                "rf":       f"{ml_.get('rf',('—',0))[0]} ({ml_.get('rf',('—',0))[1]}%)",
                "automl":   f"{ml_.get('automl',('—',0))[0]} ({ml_.get('automl',('—',0))[1]}%)",
                "status":   "ok",
            }
            batch_rows.append(row)
            record(S, xyz.name, "ok",
                   f"CB={row['catboost']}  RF={row['rf']}  AML={row['automl']}")
        except Exception as e:
            batch_rows.append({"file": xyz.name, "n_atoms": n_, "catboost":"ERR","rf":"ERR","automl":"ERR","status":"fail"})
            record(S, xyz.name, "fail", str(e))
else:
    record(S, "Пакетный прогон", "warn", "пропущен — API недоступен")


# ─────────────────────────────────────────────────────────────
# Генерация HTML-отчёта
# ─────────────────────────────────────────────────────────────
total   = len(results)
passed  = sum(1 for r in results if r["status"] == "ok")
failed  = sum(1 for r in results if r["status"] == "fail")
warned  = sum(1 for r in results if r["status"] == "warn")

STATUS_COLOR = {"ok": "#16a34a", "fail": "#dc2626", "warn": "#d97706", "info": "#6b7280"}
STATUS_LABEL = {"ok": "ПРОЙДЕН", "fail": "ОШИБКА",  "warn": "ЗАМЕЧАНИЕ", "info": "ИНФО"}
STATUS_BG    = {"ok": "#f0fdf4", "fail": "#fef2f2",  "warn": "#fffbeb",   "info": "#f9fafb"}

def badge(status):
    c = STATUS_COLOR[status]; bg = STATUS_BG[status]; lbl = STATUS_LABEL[status]
    return f'<span style="background:{bg};color:{c};border:1px solid {c};border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600">{lbl}</span>'

def rows_html(section_name):
    out = ""
    for r in results:
        if r["section"] != section_name: continue
        out += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9">{r['name']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;color:#475569;font-size:13px">{r['detail']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;text-align:right">{badge(r['status'])}</td>
        </tr>"""
    return out

def infer_table():
    if not inference_rows: return "<p style='color:#94a3b8'>Нет данных</p>"
    rows = ""
    for r in inference_rows:
        bg = STATUS_BG[r["status"]]
        rows += f"""
        <tr style="background:{bg}">
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;font-weight:500">{r['method']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;font-weight:600;color:#1e40af">{r['top1']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9">{r['conf']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;color:#64748b">{r['top2']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;color:#64748b">{r['top3']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;font-family:monospace;font-size:12px">{r['time']}</td>
        </tr>"""
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead><tr style="background:#f8fafc;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em">
        <th style="padding:8px 12px;text-align:left">Метод</th>
        <th style="padding:8px 12px;text-align:left">Top-1</th>
        <th style="padding:8px 12px;text-align:left">Conf</th>
        <th style="padding:8px 12px;text-align:left">Top-2</th>
        <th style="padding:8px 12px;text-align:left">Top-3</th>
        <th style="padding:8px 12px;text-align:left">Время</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

def batch_table():
    if not batch_rows: return "<p style='color:#94a3b8'>API недоступен — пропущено</p>"
    rows = ""
    for r in batch_rows:
        rows += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;font-family:monospace;font-size:12px">{r['file']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;text-align:center">{r['n_atoms']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9">{r['catboost']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9">{r['rf']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9">{r['automl']}</td>
          <td style="padding:8px 12px;border-bottom:1px solid #f1f5f9;text-align:right">{badge(r['status'])}</td>
        </tr>"""
    return f"""
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead><tr style="background:#f8fafc;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em">
        <th style="padding:8px 12px;text-align:left">Файл</th>
        <th style="padding:8px 12px;text-align:center">Атомов</th>
        <th style="padding:8px 12px;text-align:left">CatBoost</th>
        <th style="padding:8px 12px;text-align:left">Random Forest</th>
        <th style="padding:8px 12px;text-align:left">AutoML</th>
        <th style="padding:8px 12px;text-align:right">Статус</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>"""

def section_card(title, section_name, extra=""):
    return f"""
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:24px;overflow:hidden">
      <div style="background:#f8fafc;border-bottom:1px solid #e2e8f0;padding:14px 20px">
        <h2 style="margin:0;font-size:15px;font-weight:600;color:#0f172a">{title}</h2>
      </div>
      <table style="width:100%;border-collapse:collapse;font-size:14px">
        <tbody>{rows_html(section_name)}</tbody>
      </table>
      {extra}
    </div>"""

now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
overall_color = "#16a34a" if failed == 0 else "#dc2626"
overall_label = "ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if failed == 0 else f"ОШИБОК: {failed}"

html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>CRIS — Отчёт о тестировании</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          background: #f1f5f9; color: #0f172a; padding: 32px; }}
  h1 {{ font-size: 22px; font-weight: 700; }}
  h2 {{ font-size: 15px; }}
</style>
</head>
<body>
<div style="max-width:900px;margin:0 auto">

  <!-- Header -->
  <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:24px 28px;margin-bottom:24px">
    <div style="display:flex;justify-content:space-between;align-items:flex-start">
      <div>
        <div style="font-size:11px;font-weight:600;color:#6366f1;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px">
          CRIS · Crystal Recognition &amp; Identification System
        </div>
        <h1>Отчёт о тестировании</h1>
        <div style="margin-top:6px;font-size:13px;color:#64748b">{now}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:28px;font-weight:700;color:{overall_color}">{overall_label}</div>
        <div style="margin-top:6px;font-size:13px;color:#64748b">
          Всего: {total} &nbsp;·&nbsp;
          <span style="color:#16a34a">✓ {passed}</span> &nbsp;·&nbsp;
          <span style="color:#dc2626">✗ {failed}</span> &nbsp;·&nbsp;
          <span style="color:#d97706">⚠ {warned}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Этап 1 -->
  <div style="font-size:11px;font-weight:700;color:#6366f1;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px">
    Этап 1 — Автономное тестирование компонентов
  </div>

  {section_card("UNIT 1 &nbsp;·&nbsp; Загрузка ML-моделей", "UNIT 1 — Загрузка ML-моделей")}
  {section_card("UNIT 2 &nbsp;·&nbsp; Инференс моделей",
                "UNIT 2 — Инференс моделей",
                f'<div style="padding:0 0 16px">{infer_table()}</div>'
                if inference_rows else "")}
  {section_card("UNIT 3 &nbsp;·&nbsp; Подключение к PostgreSQL", "UNIT 3 — База данных")}

  <!-- Этап 2 -->
  <div style="font-size:11px;font-weight:700;color:#6366f1;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px;margin-top:8px">
    Этап 2 — Интеграционное тестирование
  </div>

  {section_card("INTEGRATION 1 &nbsp;·&nbsp; Сквозной инференс через /api/analyze", "INTEGRATION 1 — /api/analyze")}
  {section_card("INTEGRATION 2 &nbsp;·&nbsp; Пакетный прогон по структурам",
                "INTEGRATION 2 — Пакетный прогон",
                f'<div style="padding:0 0 16px">{batch_table()}</div>')}

  <!-- Footer -->
  <div style="text-align:center;font-size:12px;color:#94a3b8;margin-top:8px">
    Сформировано автоматически · CRIS v0.4.3
  </div>

</div>
</body>
</html>"""

report_path = ROOT / "test_report.html"
report_path.write_text(html, encoding="utf-8")
print(f"\n{'='*58}")
print(f"  Отчёт сохранён: {report_path}")
print(f"  Итог: {passed} пройдено / {failed} ошибок / {warned} замечаний")
print(f"{'='*58}\n")
