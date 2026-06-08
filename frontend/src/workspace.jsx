/* CRIS — Workspace screen (updated: dark header, WsLabel, tab panel) */

const API_BASE = window.location.hostname === "localhost" ? "http://localhost:8002" : "";

/* ── Default sample: UN unit cell (NaCl-type FCC, a=4.89Å) ── */
const DEFAULT_SITES = [
  { label: "U1", x: "0.0000", y: "0.0000", z: "0.0000" },
  { label: "U2", x: "0.5000", y: "0.5000", z: "0.0000" },
  { label: "U3", x: "0.5000", y: "0.0000", z: "0.5000" },
  { label: "U4", x: "0.0000", y: "0.5000", z: "0.5000" },
  { label: "N1", x: "0.5000", y: "0.5000", z: "0.5000" },
  { label: "N2", x: "0.0000", y: "0.0000", z: "0.5000" },
  { label: "N3", x: "0.0000", y: "0.5000", z: "0.0000" },
  { label: "N4", x: "0.5000", y: "0.0000", z: "0.0000" },
];
const DEFAULT_CELL = { a: 4.89, b: 4.89, c: 4.89, alpha: 90, beta: 90, gamma: 90 };

function formatFileSize(bytes, siteCount) {
  const kb = (bytes / 1024).toFixed(1);
  return `${kb} KB · ${siteCount} sites`;
}

/* ── CIF parser → { sites, cell, coordType: "frac" } ── */
function parseCIF(text) {
  const lines = text.split(/\r?\n/);
  const cell  = { a: 5, b: 5, c: 5, alpha: 90, beta: 90, gamma: 90 };
  const stripUnc = v => parseFloat(String(v).replace(/\(.*?\)/, ""));
  for (const line of lines) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const m = t.match(/^(_\S+)\s+(.*)/);
    if (!m) continue;
    const key = m[1].toLowerCase();
    const val = m[2].trim().split(/\s+/)[0];
    if      (key === "_cell_length_a")    { const v = stripUnc(val); if (!isNaN(v)) cell.a = v; }
    else if (key === "_cell_length_b")    { const v = stripUnc(val); if (!isNaN(v)) cell.b = v; }
    else if (key === "_cell_length_c")    { const v = stripUnc(val); if (!isNaN(v)) cell.c = v; }
    else if (key === "_cell_angle_alpha") { const v = stripUnc(val); if (!isNaN(v)) cell.alpha = v; }
    else if (key === "_cell_angle_beta")  { const v = stripUnc(val); if (!isNaN(v)) cell.beta  = v; }
    else if (key === "_cell_angle_gamma") { const v = stripUnc(val); if (!isNaN(v)) cell.gamma = v; }
  }
  const sites = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    if (line.toLowerCase() === "loop_") {
      i++;
      const headers = [];
      while (i < lines.length && lines[i].trim().startsWith("_")) {
        headers.push(lines[i].trim().toLowerCase());
        i++;
      }
      const lIdx = headers.findIndex(h => h === "_atom_site_label");
      const tIdx = headers.findIndex(h => h === "_atom_site_type_symbol");
      const xIdx = headers.findIndex(h => h === "_atom_site_fract_x");
      const yIdx = headers.findIndex(h => h === "_atom_site_fract_y");
      const zIdx = headers.findIndex(h => h === "_atom_site_fract_z");
      if (xIdx >= 0 && yIdx >= 0 && zIdx >= 0) {
        while (i < lines.length) {
          const dl = lines[i].trim();
          if (!dl || dl.startsWith("#")) { i++; continue; }
          if (dl.toLowerCase() === "loop_" || dl.startsWith("_")) break;
          const parts = dl.split(/\s+/).filter(Boolean);
          const maxIdx = Math.max(lIdx >= 0 ? lIdx : 0, tIdx >= 0 ? tIdx : 0, xIdx, yIdx, zIdx);
          if (parts.length > maxIdx) {
            const label = lIdx >= 0 ? parts[lIdx] : (tIdx >= 0 ? parts[tIdx] : `A${sites.length + 1}`);
            const x = stripUnc(parts[xIdx]);
            const y = stripUnc(parts[yIdx]);
            const z = stripUnc(parts[zIdx]);
            if (!isNaN(x) && !isNaN(y) && !isNaN(z)) {
              sites.push({ label, x: x.toFixed(5), y: y.toFixed(5), z: z.toFixed(5) });
            }
          }
          i++;
        }
      } else {
        while (i < lines.length) {
          const dl = lines[i].trim();
          if (!dl || dl.startsWith("#")) { i++; continue; }
          if (dl.toLowerCase() === "loop_" || dl.startsWith("_")) break;
          i++;
        }
      }
    } else { i++; }
  }
  return { sites, cell, coordType: "frac" };
}

/* ── XYZ parser → { sites, cell: null, coordType: "cart" } ── */
function parseXYZ(text) {
  const lines = text.split(/\r?\n/).filter(l => l.trim());
  if (lines.length < 3) return { sites: [], cell: null, coordType: "cart" };
  const count = parseInt(lines[0].trim(), 10);
  const sites = [];
  for (let i = 2; i < lines.length && sites.length < count; i++) {
    const parts = lines[i].trim().split(/\s+/);
    if (parts.length >= 4) {
      const [label, x, y, z] = parts;
      if (!isNaN(parseFloat(x))) {
        sites.push({ label, x: parseFloat(x).toFixed(5), y: parseFloat(y).toFixed(5), z: parseFloat(z).toFixed(5) });
      }
    }
  }
  return { sites, cell: null, coordType: "cart" };
}

/* ══════════════════════════════════════════════════════════
   [CHANGE 1] WORKSPACE HEADER — replaces global nav + toolbar.
   Dark, compact, tool-mode. Logo navigates back to home.
   ══════════════════════════════════════════════════════════ */
const WorkspaceHeader = ({ stage, result, file, onReset, onHelp, setRoute }) => {
  const confidence = result?.lattice?.confidence;
  const matched    = result?.success;

  const status = stage === "result"
    ? matched
      ? { dot: "#34C472", label: `${result.lattice?.name_en ?? "matched"} · ${confidence != null ? confidence.toFixed(2) : "—"}`, color: "#34C472" }
      : { dot: "#C8841A", label: "no match", color: "#C8841A" }
    : stage === "running"
    ? { dot: "var(--signal)", label: "computing", color: "var(--signal)", pulse: true }
    : { dot: "rgba(255,255,255,0.22)", label: "idle", color: "rgba(255,255,255,0.35)" };

  const isMobileHdr = useIsMobile();

  const handleGoHome = () => {
    const isDirty = file !== null || stage === "running" || stage === "result";
    if (isDirty && !window.confirm("Данные текущего анализа не сохранятся.\nВыйти из Workspace?")) return;
    setRoute?.("home");
  };

  return (
    <header style={{
      height: 56, background: "var(--ink)",
      borderBottom: "1px solid rgba(255,255,255,0.07)",
      display: "flex", alignItems: "center",
      padding: "0 16px", gap: 12, flexShrink: 0, zIndex: 50,
    }}>
      <div onClick={handleGoHome} style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8, userSelect: "none", flexShrink: 0 }}>
        <Logo size={24} color="var(--night-ink)" node="var(--signal)" />
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 17, letterSpacing: "-0.015em", color: "var(--night-ink)" }}>CRIS</span>
      </div>
      {!isMobileHdr && (
        <>
          <div style={{ width: 1, height: 18, background: "rgba(255,255,255,0.12)", flexShrink: 0 }} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(255,255,255,0.3)", flexShrink: 0 }}>workspace</span>
        </>
      )}
      <div style={{ flex: 1 }} />
      {/* Status chip */}
      {!isMobileHdr && (
        <div style={{ display: "flex", alignItems: "center", gap: 7, fontFamily: "var(--font-mono)", fontSize: 11, color: status.color }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: status.dot, flexShrink: 0,
            ...(status.pulse ? { animation: "pulse-signal 1.4s infinite var(--ease-in-out)" } : {}) }} />
          {status.label}
        </div>
      )}
      <Button variant="ghost" size="sm" onDark icon={<IconHelp size={16} />} onClick={onHelp}
        style={{ padding: "8px" }} title="Подсказка" />
      <Button variant="ghost" size="sm" onDark icon={<IconRotate size={16} />} onClick={onReset}
        style={{ padding: "8px" }} title="Сбросить" />
    </header>
  );
};

/* ══════════════════════════════════════════════════════════
   [CHANGE 2] WsLabel — replaces <Eyebrow> inside panels.
   Small cobalt bar prefix, no horizontal dash/rule.
   ══════════════════════════════════════════════════════════ */
const WsLabel = ({ children }) => (
  <div style={{
    display: "inline-flex", alignItems: "center", gap: 7,
    fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em",
    textTransform: "uppercase", color: "var(--mute)", fontWeight: 500,
  }}>
    <span style={{ display: "block", width: 3, height: 10, background: "var(--cobalt)", borderRadius: 1.5, flexShrink: 0 }} />
    {children}
  </div>
);

/* ══════════════════════════════════════════════════════════
   WORKSPACE SCREEN
   ══════════════════════════════════════════════════════════ */
const WorkspaceScreen = ({ setRoute }) => {
  const isMobile   = useIsMobile();
  const [mobileTab, setMobileTab] = React.useState("input"); // "input" | "viewer" | "results"

  const [stage, setStage]         = React.useState("input");
  const [mode,  setMode]          = React.useState("file");
  const [file,  setFile]          = React.useState(null);
  const [sites, setSites]         = React.useState([]);
  const [cell,  setCell]          = React.useState(DEFAULT_CELL);
  const [coordType, setCoordType] = React.useState("frac");
  const [sessionId, setSessionId] = React.useState(null);
  const [result,    setResult]    = React.useState(null);
  const [apiError,  setApiError]  = React.useState(null);
  const [methods,        setMethods]        = React.useState({ db: true, catboost: true, catboost_substance: true, rf: true, automl: true });
  const [methodSection,  setMethodSection]  = React.useState("substance");
  const [resultSection,  setResultSection]  = React.useState("substance");
  const [showHelp,       setShowHelp]       = React.useState(false);
  const screenshotApiRef = React.useRef(null);

  React.useEffect(() => {
    const isDirty = file !== null || stage === "running" || stage === "result";
    if (!isDirty) return;
    const handler = (e) => { e.preventDefault(); e.returnValue = ""; };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [file, stage]);

  const start = async () => {
    if (sites.length < 2) return;
    setStage("running");
    setResult(null);
    setApiError(null);

    const cartSites = sites.map(s => {
      const fx = parseFloat(s.x) || 0;
      const fy = parseFloat(s.y) || 0;
      const fz = parseFloat(s.z) || 0;
      const [cx, cy, cz] = coordType === "cart"
        ? [fx, fy, fz]
        : fracToCart(fx, fy, fz, cell);
      return { label: s.label, x: cx, y: cy, z: cz };
    });

    try {
      const res  = await fetch(`${API_BASE}/api/analyze`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sites: cartSites,
          methods: Object.entries(methods).filter(([, v]) => v).map(([k]) => k),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setResult(data);
      if (data.session_id) setSessionId(data.session_id);
    } catch (e) {
      setApiError(e.message);
    } finally {
      setStage("result");
      // На мобиле автоматически переходим на вкладку результатов
      setMobileTab("results");
    }
  };

  const reset = () => {
    setStage("input"); setResult(null); setApiError(null); setSessionId(null);
    setFile(null); setSites([]); setCell(DEFAULT_CELL); setCoordType("frac");
    setMode("file"); setMobileTab("input");
  };

  const handleScreenshot = () => {
    if (!screenshotApiRef.current) return;
    const dataUrl = screenshotApiRef.current.screenshot();
    const a = document.createElement("a");
    a.href = dataUrl; a.download = "lattice_snapshot.png"; a.click();
  };

  const handleFileLoad = ({ file: f, sites: s, cell: cl, coordType: ct }) => {
    setFile({ name: f.name, size: formatFileSize(f.size, s.length) });
    setSites(s);
    if (cl) setCell(cl);
    setCoordType(ct || "frac");
  };

  const handleFileClear = () => {
    setFile(null); setSites(DEFAULT_SITES); setCell(DEFAULT_CELL); setCoordType("frac");
  };

  /* ── Переключение таба + resize-триггер для Three.js ── */
  const switchTab = (tab) => {
    setMobileTab(tab);
    if (tab === "viewer") {
      // Three.js ResizeObserver сработает, но дополнительный dispatch гарантирует корректный размер
      requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
    }
  };

  /* ── Мобильный tab-bar ── */
  const MobileTabBar = () => {
    const tabs = [
      { id: "input",   icon: <IconLayers size={20} />,  label: "Данные"    },
      { id: "viewer",  icon: <IconCube size={20} />,    label: "3D"        },
      { id: "results", icon: <IconChart size={20} />,   label: "Результат" },
    ];
    return (
      <div style={{
        display: "flex", borderTop: "1px solid rgba(255,255,255,0.08)",
        background: "var(--ink)", flexShrink: 0, zIndex: 40,
        paddingBottom: "env(safe-area-inset-bottom, 0px)",
      }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => switchTab(t.id)}
            style={{
              flex: 1, border: "none", background: "transparent", cursor: "pointer",
              padding: "10px 4px 10px", display: "flex", flexDirection: "column",
              alignItems: "center", gap: 4,
              color: mobileTab === t.id ? "var(--signal)" : "rgba(255,255,255,0.4)",
              transition: "color 0.15s",
            }}>
            {t.icon}
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".06em", textTransform: "uppercase" }}>{t.label}</span>
          </button>
        ))}
      </div>
    );
  };

  return (
    /* 100dvh учитывает адресную строку браузера на iOS/Android */
    <div style={{ display: "flex", flexDirection: "column", height: "100dvh", minHeight: "-webkit-fill-available", position: "relative" }}>
      <WorkspaceHeader stage={stage} result={result} file={file} onReset={reset} onHelp={() => setShowHelp(true)} setRoute={setRoute} />

      {/* ── Панели ── */}
      {isMobile ? (
        /* Мобиль: все панели в одном стеке, visibility переключается (НЕ display:none!) */
        /* Это критично для Three.js — display:none убивает WebGL размеры */
        <div style={{ flex: 1, minHeight: 0, position: "relative", overflow: "hidden" }}>

          {/* Панель данных (Input) */}
          <div style={{
            position: "absolute", inset: 0,
            visibility: mobileTab === "input" ? "visible" : "hidden",
            pointerEvents: mobileTab === "input" ? "auto" : "none",
            display: "flex", flexDirection: "column",
            overflowY: "auto", zIndex: mobileTab === "input" ? 2 : 1,
          }}>
            <WsLeftPanel stage={stage} mode={mode} setMode={setMode}
              file={file} onFileLoad={handleFileLoad} onFileClear={handleFileClear}
              sites={sites} setSites={setSites}
              methods={methods} setMethods={setMethods}
              section={methodSection} setSection={setMethodSection}
              onStart={start}
            />
          </div>

          {/* Панель 3D — всегда в DOM, только visibility меняется */}
          <div style={{
            position: "absolute", inset: 0,
            visibility: mobileTab === "viewer" ? "visible" : "hidden",
            pointerEvents: mobileTab === "viewer" ? "auto" : "none",
            display: "flex", flexDirection: "column",
            zIndex: mobileTab === "viewer" ? 2 : 1,
          }}>
            <WsCenter stage={stage} sites={sites} cell={cell} coordType={coordType}
              onScreenshot={handleScreenshot}
              onViewerReady={(api) => { screenshotApiRef.current = api; }}
            />
          </div>

          {/* Панель результатов */}
          <div style={{
            position: "absolute", inset: 0,
            visibility: mobileTab === "results" ? "visible" : "hidden",
            pointerEvents: mobileTab === "results" ? "auto" : "none",
            display: "flex", flexDirection: "column",
            overflowY: "auto", zIndex: mobileTab === "results" ? 2 : 1,
          }}>
            <WsRightPanel stage={stage} result={result} apiError={apiError} siteCount={sites.length} methods={methods} sessionId={sessionId} section={resultSection} setSection={setResultSection} />
          </div>

        </div>
      ) : (
        /* Десктоп: 3 колонки */
        <div style={{ display: "grid", gridTemplateColumns: "360px 1fr 380px", flex: 1, minHeight: 0 }}>
          <WsLeftPanel
            stage={stage} mode={mode} setMode={setMode}
            file={file} onFileLoad={handleFileLoad} onFileClear={handleFileClear}
            sites={sites} setSites={setSites}
            methods={methods} setMethods={setMethods}
            section={methodSection} setSection={setMethodSection}
            onStart={start}
          />
          <WsCenter
            stage={stage} sites={sites} cell={cell} coordType={coordType}
            onScreenshot={handleScreenshot}
            onViewerReady={(api) => { screenshotApiRef.current = api; }}
          />
          <WsRightPanel stage={stage} result={result} apiError={apiError} siteCount={sites.length} methods={methods} sessionId={sessionId} section={resultSection} setSection={setResultSection} />
        </div>
      )}

      {/* ── Мобильный tab-bar внизу ── */}
      {isMobile && <MobileTabBar />}

      {/* ── Help overlay ── */}
      {showHelp && (
        <div
          onClick={() => setShowHelp(false)}
          style={{
            position: "fixed", inset: 0, zIndex: 200,
            background: "rgba(10,14,28,0.72)", backdropFilter: "blur(4px)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              background: "var(--paper)", borderRadius: 16, padding: "36px 40px",
              maxWidth: 520, width: "90%", boxShadow: "0 24px 64px rgba(0,0,0,0.35)",
              position: "relative",
            }}
          >
            <button
              onClick={() => setShowHelp(false)}
              style={{ position: "absolute", top: 16, right: 16, background: "transparent", border: "none", cursor: "pointer", color: "var(--mute)", padding: 4 }}
            >
              <IconClose size={18} />
            </button>

            <div style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 20, marginBottom: 4 }}>
              Как пользоваться воркспейсом
            </div>
            <div style={{ fontSize: 12, color: "var(--mute)", fontFamily: "var(--font-mono)", marginBottom: 24 }}>CRIS · краткая инструкция</div>

            <ol style={{ paddingLeft: 20, margin: 0, display: "flex", flexDirection: "column", gap: 14 }}>
              {[
                { title: "Загрузите структуру", text: "Перетащите CIF или XYZ-файл в левую панель, нажмите «выберите файл» или выберите один из готовых примеров. Также можно ввести координаты вручную через вкладку «Ручной ввод»." },
                { title: "Проверьте 3D-вид", text: "Центральная панель отображает атомы в реальном времени. Используйте мышь для вращения, колёсико для масштаба. Кнопка «screenshot» сохраняет снимок." },
                { title: "Выберите методы", text: "В левой панели выберите методы распознавания — по базе данных, ML-моделям (сингония / вещество) или их комбинацию. Затем нажмите «Распознать решётку»." },
                { title: "Читайте результаты", text: "В правой панели появятся результаты по всем выбранным методам. Переключайте вкладки «Вещество» и «Сингония» для просмотра соответствующих выводов." },
                { title: "Сброс и экспорт", text: "«Сбросить» (верхняя панель) очищает все данные. Кнопка DOCX в правой панели экспортирует отчёт." },
              ].map((item, i) => (
                <li key={i} style={{ paddingLeft: 4 }}>
                  <span style={{ fontWeight: 600, fontSize: 14 }}>{item.title}</span>
                  <div style={{ fontSize: 13, color: "var(--mute)", marginTop: 3, lineHeight: 1.5 }}>{item.text}</div>
                </li>
              ))}
            </ol>

            <div style={{ marginTop: 28, textAlign: "right" }}>
              <button
                onClick={() => setShowHelp(false)}
                style={{ background: "var(--cobalt)", color: "#fff", border: "none", borderRadius: 8, padding: "10px 22px", fontSize: 14, fontWeight: 600, cursor: "pointer" }}
              >
                Понятно
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── LEFT PANEL ── */
const SECTION_METHODS = {
  substance: [
    { key: "db",                 label: "По базе данных",      note: "точное совпадение координат" },
    { key: "catboost_substance", label: "CatBoost",            note: "ML, конкретные соединения (UC, UN2…)" },
    { key: "rf",                 label: "Random Forest",       note: "ML, конкретные соединения" },
    { key: "automl",             label: "AutoML (ExtraTrees)", note: "ML, FLAML — конкретные соединения" },
  ],
  syngony: [
    { key: "db",       label: "По базе данных",  note: "точное совпадение координат" },
    { key: "catboost", label: "CatBoost",         note: "ML, 8 типов кристаллических систем" },
  ],
};

const WsLeftPanel = ({ stage, mode, setMode, file, onFileLoad, onFileClear, sites, setSites, methods, setMethods, section, setSection, onStart }) => (
  <aside style={{ borderRight: "1px solid var(--hairline)", padding: 24, overflowY: "auto", background: "var(--paper)" }}>
    <WsLabel>Input</WsLabel>
    <h3 className="section-title" style={{ fontSize: 22, margin: "10px 0 18px", lineHeight: 1.2 }}>Структура для распознавания</h3>
    <div style={{ marginBottom: 16 }}>
      <Seg value={mode} onChange={setMode} options={[{ value: "file", label: "Файл" }, { value: "manual", label: "Координаты" }]} />
    </div>
    {mode === "file"
      ? <FileInput file={file} onFileLoad={onFileLoad} onClear={onFileClear} />
      : <ManualInput sites={sites} setSites={setSites} />}

    <div style={{ marginTop: 20, padding: 16, background: "var(--card)", borderRadius: 10, border: "1px solid var(--hairline)" }}>
      <WsLabel>Методы</WsLabel>

      {/* Section tabs inside the card */}
      <SectionTabs active={section} onChange={setSection} />

      <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10 }}>
        {SECTION_METHODS[section].map(({ key, label, note }) => (
          <label key={key} style={{ display: "flex", alignItems: "flex-start", gap: 10, cursor: "pointer" }}>
            <input
              type="checkbox" checked={!!methods[key]}
              onChange={e => setMethods(m => ({ ...m, [key]: e.target.checked }))}
              style={{ marginTop: 2, accentColor: "var(--cobalt)", width: 14, height: 14, flexShrink: 0 }}
            />
            <div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--ink)" }}>{label}</div>
              <div style={{ fontSize: 11, color: "var(--mute)" }}>{note}</div>
            </div>
          </label>
        ))}
      </div>
    </div>

    <div style={{ marginTop: 24 }}>
      <Button variant="primary" size="lg" iconRight={<IconArrowRight size={16} />} onClick={onStart}
        disabled={stage === "running"} style={{ width: "100%" }}>
        {stage === "running" ? "Распознавание…" : "Распознать решётку"}
      </Button>
    </div>
  </aside>
);

const EXAMPLES = [
  { label: "UC₂",  filename: "UC2_mp-1102444.xyz" },
  { label: "UO₂",  filename: "UO2_mp-865305.xyz"  },
  { label: "U₂N₃", filename: "U2N3_mp-973.xyz"    },
];

const FileInput = ({ file, onFileLoad, onClear }) => {
  const inputRef = React.useRef(null);
  const [dragOver,    setDragOver]    = React.useState(false);
  const [parseError,  setParseError]  = React.useState(null);
  const [loadingEx,   setLoadingEx]   = React.useState(null);

  const processFile = (f) => {
    if (!f) return;
    const name = f.name.toLowerCase();
    if (!name.endsWith(".cif") && !name.endsWith(".xyz")) {
      setParseError("Поддерживаются только .cif и .xyz файлы"); return;
    }
    setParseError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text   = e.target.result;
        const parsed = name.endsWith(".cif") ? parseCIF(text) : parseXYZ(text);
        if (parsed.sites.length === 0) { setParseError("Не удалось найти атомы в файле"); return; }
        if (onFileLoad) onFileLoad({ file: f, ...parsed });
      } catch (err) { setParseError("Ошибка парсинга: " + err.message); }
    };
    reader.onerror = () => setParseError("Не удалось прочитать файл");
    reader.readAsText(f);
  };

  const onDrop      = (e) => { e.preventDefault(); setDragOver(false); processFile(e.dataTransfer.files[0]); };
  const onDragOver  = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = ()  => setDragOver(false);
  const onInputChange = (e) => { processFile(e.target.files[0]); e.target.value = ""; };

  const loadExample = async (filename, label) => {
    setLoadingEx(filename);
    setParseError(null);
    try {
      const res = await fetch(`${API_BASE}/api/example/${filename}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const text = await res.text();
      const parsed = parseXYZ(text);
      if (parsed.sites.length === 0) { setParseError("Пример не содержит атомов"); return; }
      const byteLen = new TextEncoder().encode(text).length;
      if (onFileLoad) onFileLoad({ file: { name: filename, size: byteLen }, ...parsed });
    } catch (err) {
      setParseError("Не удалось загрузить пример: " + err.message);
    } finally {
      setLoadingEx(null);
    }
  };

  return (
    <div>
      <div
        style={{
          border: `1.5px dashed ${dragOver ? "var(--cobalt)" : "var(--hairline-strong)"}`,
          borderRadius: 10, padding: 22,
          display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
          background: dragOver ? "rgba(37,64,255,0.05)" : "var(--card)",
          textAlign: "center", cursor: "pointer",
          transition: "border-color .15s, background .15s", userSelect: "none",
        }}
        onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
        onClick={() => inputRef.current?.click()}
      >
        <IconUpload size={28} style={{ color: dragOver ? "var(--cobalt)" : undefined }} />
        <div style={{ fontSize: 14, fontWeight: 500 }}>{dragOver ? "Отпустите файл" : "Перетащите CIF/XYZ"}</div>
        <div style={{ fontSize: 12, color: "var(--mute)" }}>или <span style={{ color: "var(--cobalt)", textDecoration: "underline" }}>выберите файл</span></div>
        <div style={{ fontSize: 11, color: "var(--mute)", fontFamily: "var(--font-mono)" }}>до 1000 ионов · fractional · Wyckoff</div>
      </div>
      <input ref={inputRef} type="file" accept=".cif,.xyz" style={{ display: "none" }} onChange={onInputChange} />

      {/* Example links */}
      <div style={{ marginTop: 8, display: "flex", gap: 12, justifyContent: "center" }}>
        {EXAMPLES.map(({ label, filename }) => (
          <button
            key={filename}
            onClick={() => loadExample(filename, label)}
            disabled={loadingEx !== null}
            style={{
              background: "transparent", border: "none", padding: 0,
              color: "var(--cobalt)", fontSize: 12, cursor: loadingEx ? "default" : "pointer",
              textDecoration: "underline", fontFamily: "var(--font-sans)",
              opacity: loadingEx && loadingEx !== filename ? 0.4 : 1,
              transition: "opacity .15s",
            }}
          >
            {loadingEx === filename ? "Загрузка…" : label}
          </button>
        ))}
      </div>
      {parseError && (
        <div style={{ marginTop: 8, fontSize: 12, color: "#e53e3e", padding: "8px 12px", background: "rgba(229,62,62,0.07)", borderRadius: 6, border: "1px solid rgba(229,62,62,0.18)" }}>
          ⚠ {parseError}
        </div>
      )}
      {file && (
        <div style={{ marginTop: 12, padding: "10px 12px", border: "1px solid var(--hairline)", borderRadius: 6, display: "flex", alignItems: "center", gap: 10, background: "var(--card)" }}>
          <IconCube size={14} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{file.name}</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--mute)" }}>{file.size}</div>
          </div>
          <button style={{ background: "transparent", border: "none", color: "var(--mute)", cursor: "pointer" }}
            onClick={(e) => { e.stopPropagation(); if (onClear) onClear(); }}>
            <IconClose size={14} />
          </button>
        </div>
      )}
    </div>
  );
};

const ManualInput = ({ sites, setSites }) => {
  const updateSite = (i, key, val) => setSites(sites.map((s, idx) => idx === i ? { ...s, [key]: val } : s));
  const removeSite = (i) => setSites(sites.filter((_, idx) => idx !== i));
  const addSite    = ()  => setSites([...sites, { label: `X${sites.length + 1}`, x: "0.0000", y: "0.0000", z: "0.0000" }]);
  return (
    <div>
      <div style={{ background: "var(--card)", border: "1px solid var(--hairline)", borderRadius: 10, overflowX: "auto" }}>
        <div style={{ minWidth: 280 }}>
        <div style={{ display: "grid", gridTemplateColumns: "52px 68px 68px 68px 24px", padding: "7px 8px", background: "var(--paper-deep)", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--mute)" }}>
          <span style={{ paddingLeft: 6 }}>label</span>
          <span style={{ paddingLeft: 6 }}>x</span>
          <span style={{ paddingLeft: 6 }}>y</span>
          <span style={{ paddingLeft: 6 }}>z</span>
          <span />
        </div>
        {sites.map((s, i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "52px 68px 68px 68px 24px", padding: "2px 8px", alignItems: "center", borderTop: i ? "1px solid var(--hairline)" : "none" }}>
            <input className="input mono" value={s.label} onChange={e => updateSite(i, "label", e.target.value)} style={{ padding: "5px 6px", fontSize: 12, border: "none", background: "transparent", width: "100%" }} />
            {["x", "y", "z"].map(axis => (
              <input key={axis} className="input mono" value={s[axis]} onChange={e => updateSite(i, axis, e.target.value)} style={{ padding: "5px 6px", fontSize: 12, border: "none", background: "transparent", width: "100%" }} />
            ))}
            <button onClick={() => removeSite(i)} style={{ background: "transparent", border: "none", color: "var(--mute)", cursor: "pointer" }}><IconClose size={12} /></button>
          </div>
        ))}
        </div>
      </div>
      <button onClick={addSite}
        style={{ marginTop: 8, background: "transparent", border: "1px dashed var(--hairline-strong)", borderRadius: 6, padding: "8px 12px", width: "100%", color: "var(--mute)", fontFamily: "var(--font-mono)", fontSize: 12, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
        <IconPlus size={12} /> добавить ион
      </button>
    </div>
  );
};

/* ── CENTER ── */
const WsCenter = ({ stage, sites, cell, coordType, onScreenshot, onViewerReady }) => {
  const [zoomPct, setZoomPct] = React.useState(100);
  const viewerApiRef = React.useRef(null);

  const normSites = React.useMemo(() => sites.map(s => ({
    ...s, symbol: s.symbol || parseSymbol(s.label),
  })), [sites]);

  const handleViewerReady = (api) => {
    viewerApiRef.current = api;
    if (onViewerReady) onViewerReady(api);
  };

  const handleZoomIn  = () => viewerApiRef.current?.zoomIn?.();
  const handleZoomOut = () => viewerApiRef.current?.zoomOut?.();

  return (
    /* flex:1 нужен на мобиле — section находится в flex-колонке и без него схлопывается до 0px */
    <section className="viewer" style={{ position: "relative", color: "var(--night-ink)", flex: 1, minHeight: 0 }}>
      <div style={{ position: "absolute", top: 16, left: 16, right: 16, display: "flex", justifyContent: "space-between", zIndex: 5, pointerEvents: "none" }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--night-mute)" }}>
          3D viewer · {stage === "result" ? "result" : normSites.length > 0 ? `preview · ${normSites.length} sites · ${coordType}` : "—"}
        </div>
        <div style={{ display: "flex", gap: 8, pointerEvents: "all" }}>
          <DarkChip icon={<IconCamera size={12} />} onClick={onScreenshot}>screenshot</DarkChip>
          <DarkChip icon={<IconRotate size={12} />}>reset view</DarkChip>
        </div>
      </div>

      {normSites.length > 0
        ? <LatticeViewer3D sites={normSites} cell={cell} coordType={coordType} onReady={handleViewerReady} onZoomChange={setZoomPct} />
        : <ViewerEmpty />}
      {stage === "running" && <ViewerPipeline />}

      <div style={{ position: "absolute", bottom: 16, left: 16, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--night-mute)", display: "flex", gap: 18, zIndex: 5, pointerEvents: "none" }}>
        <span><span style={{ color: "#FF5C5C" }}>●</span> X</span>
        <span><span style={{ color: "#5CFF8F" }}>●</span> Y</span>
        <span><span style={{ color: "#5C8FFF" }}>●</span> Z</span>
      </div>
      <div style={{ position: "absolute", bottom: 16, right: 16, display: "flex", gap: 6, zIndex: 5, alignItems: "center" }}>
        {normSites.length > 0 && (
          <DarkChip>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, minWidth: 36, textAlign: "center", letterSpacing: ".04em" }}>{zoomPct}%</span>
          </DarkChip>
        )}
        <DarkChip icon={<IconMinus size={12} />} onClick={handleZoomOut} />
        <DarkChip icon={<IconPlus  size={12} />} onClick={handleZoomIn} />
      </div>
    </section>
  );
};

const DarkChip = ({ icon, children, onClick }) => (
  <button onClick={onClick} style={{ display: "inline-flex", gap: 6, alignItems: "center", padding: children ? "5px 10px" : 6, background: "rgba(14,16,20,0.72)", backdropFilter: "blur(10px)", border: "1px solid var(--night-line)", borderRadius: 6, color: "var(--night-ink)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".04em", cursor: "pointer" }}>
    {icon}{children}
  </button>
);

const ViewerEmpty = () => (
  <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", textAlign: "center", padding: 40 }}>
    <div style={{ fontFamily: "var(--font-display)", fontSize: 22, color: "var(--night-ink)", marginTop: 20 }}>Загрузите данные слева</div>
    <div style={{ marginTop: 6, fontSize: 14, color: "var(--night-mute)" }}>3D-сцена появится после добавления ионов</div>
  </div>
);

const ViewerPipeline = () => (
  <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", padding: 40, background: "rgba(0,0,0,0.55)", zIndex: 4, backdropFilter: "blur(3px)" }}>
    <div style={{ width: 460, background: "rgba(14,16,20,0.85)", backdropFilter: "blur(16px)", border: "1px solid var(--night-line)", borderRadius: 10, padding: 28 }}>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--night-mute)", marginBottom: 18 }}>ML pipeline · live</div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">parse_input</span><span className="pipeline-time">0.04s</span></div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">normalize_coordinates</span><span className="pipeline-time">0.12s</span></div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">compute_pairwise_distances</span><span className="pipeline-time">0.31s</span></div>
      <div className="pipeline-step active"><span className="pipeline-dot" /><span className="pipeline-label">compute_kde_spectrum</span><span className="pipeline-time">…</span></div>
      <div className="pipeline-step pending"><span className="pipeline-dot" /><span className="pipeline-label">ensemble_predict (rf + catboost)</span><span className="pipeline-time">—</span></div>
      <div className="pipeline-step pending"><span className="pipeline-dot" /><span className="pipeline-label">match_reference_structure</span><span className="pipeline-time">—</span></div>
    </div>
  </div>
);

/* ══════════════════════════════════════════════════════════
   [CHANGE 3] RIGHT PANEL — tab switcher replaces draggable divider.
   ══════════════════════════════════════════════════════════ */
const WsRightPanel = ({ stage, result, apiError, siteCount, methods, sessionId, section, setSection }) => {
  const [tab, setTab]                   = React.useState("verdict");
  const [chatMessages, setChatMessages] = React.useState([]);

  React.useEffect(() => {
    if (stage === "result") setTab("verdict");
  }, [stage]);

  // Сбрасываем историю чата при каждом новом анализе
  React.useEffect(() => {
    if (stage === "running") setChatMessages([]);
  }, [stage]);

  return (
    <aside style={{ borderLeft: "1px solid var(--hairline)", display: "flex", flexDirection: "column", background: "var(--paper)", overflow: "hidden" }}>

      {/* Tab bar */}
      <div style={{ display: "flex", alignItems: "flex-end", borderBottom: "1px solid var(--hairline)", padding: "0 20px", flexShrink: 0 }}>
        {[["verdict", "Результат"], ["chat", "AI · Чат"]].map(([id, label]) => (
          <button key={id} onClick={() => setTab(id)} style={{
            padding: "14px 0", marginRight: 20,
            border: "none", background: "transparent",
            fontFamily: "var(--font-body)", fontSize: 13,
            fontWeight: tab === id ? 500 : 400,
            color: tab === id ? "var(--ink)" : "var(--mute)",
            cursor: "pointer",
            borderBottom: `2px solid ${tab === id ? "var(--ink)" : "transparent"}`,
            marginBottom: -1,
            transition: "color var(--t-fast), border-color var(--t-fast)",
            whiteSpace: "nowrap",
          }}>{label}</button>
        ))}
      </div>

      {/* Verdict — всегда в DOM, скрываем через display */}
      <div style={{ display: tab === "verdict" ? "flex" : "none", flex: 1, overflowY: "auto", padding: 24, minHeight: 0, flexDirection: "column" }}>
        {stage === "result"
          ? <VerdictBlock result={result} apiError={apiError} siteCount={siteCount} methods={methods} section={section} setSection={setSection} />
          : <VerdictPlaceholder />}
      </div>

      {/* Chat — всегда в DOM, история не теряется при смене таба */}
      <div style={{ display: tab === "chat" ? "flex" : "none", flex: 1, flexDirection: "column", minHeight: 0, overflow: "hidden" }}>
        <ChatPanel
          stage={stage}
          sessionId={sessionId}
          result={result}
          messages={chatMessages}
          setMessages={setChatMessages}
        />
      </div>
    </aside>
  );
};

/* ── Verdict ── */
const VerdictPlaceholder = () => (
  <div>
    {/* [CHANGE 2] WsLabel */}
    <WsLabel>Verdict</WsLabel>
    <p style={{ marginTop: 16, color: "var(--mute)", fontSize: 14, lineHeight: 1.6 }}>После запуска здесь появится тип решётки, эталонное вещество и экспорт.</p>
  </div>
);

const RankingRow = ({ item, top }) => (
  <div style={{ marginTop: 7, display: "grid", gridTemplateColumns: "80px 1fr 36px", gap: 8, alignItems: "center", fontFamily: "var(--font-mono)", fontSize: 12 }}>
    <span style={{ color: top ? "var(--cobalt)" : "var(--ink-soft)" }}>{item.name_en ?? item.name_ru}</span>
    <div style={{ height: 4, background: "var(--hairline)", borderRadius: 2, overflow: "hidden" }}>
      <div style={{ height: "100%", width: `${item.prob * 100}%`, background: top ? "var(--cobalt)" : "var(--mute-soft)", borderRadius: 2 }} />
    </div>
    <span style={{ color: "var(--mute)", textAlign: "right" }}>{item.prob.toFixed(2)}</span>
  </div>
);

const MethodResult = ({ label, result, active, emptyText = "Нет данных" }) => {
  // считаем результат «пустым» если нет ни имени, ни предсказаний (модель не смогла загрузиться)
  const hasData = result && (result.name_en || (result.ranking && result.ranking.length > 0));
  return (
  <div style={{ border: `1px solid ${active && hasData ? "var(--cobalt)" : "var(--hairline)"}`, borderRadius: 8, padding: "12px 14px", marginTop: 10 }}>
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--mute)" }}>{label}</span>
      {!active
        ? <Chip tone="default">не выбран</Chip>
        : !hasData
        ? <Chip tone="warn">нет данных</Chip>
        : <Chip tone="ok" dot>{result.confidence != null ? result.confidence.toFixed(2) : "—"}</Chip>}
    </div>
    {active && hasData ? (
      <>
        <div style={{ fontSize: 18, fontWeight: 600, color: "var(--ink)" }}>{result.name_en ?? "—"}</div>
        {result.name_ru && <div style={{ fontSize: 12, color: "var(--ink-soft)", marginTop: 2 }}>{result.name_ru}</div>}
        {result.ranking?.length > 0 && (
          <div style={{ marginTop: 8 }}>
            {result.ranking.slice(0, 3).map((item, i) => <RankingRow key={i} item={item} top={i === 0} />)}
          </div>
        )}
      </>
    ) : active ? (
      <div style={{ fontSize: 12, color: "var(--mute)" }}>{emptyText}</div>
    ) : null}
  </div>
  );
};

/* ── Inner section tab bar ── */
const SectionTabs = ({ active, onChange }) => (
  <div style={{ display: "flex", borderBottom: "1px solid var(--hairline)", marginTop: 14, marginBottom: 0 }}>
    {[["substance", "По веществу"], ["syngony", "Сингония"]].map(([id, label]) => (
      <button key={id} onClick={() => onChange(id)} style={{
        padding: "8px 14px 9px", border: "none", background: "transparent",
        fontFamily: "var(--font-body)", fontSize: 12, fontWeight: active === id ? 600 : 400,
        color: active === id ? "var(--ink)" : "var(--mute)",
        borderBottom: `2px solid ${active === id ? "var(--cobalt)" : "transparent"}`,
        marginBottom: -1, cursor: "pointer", letterSpacing: ".01em",
        transition: "color var(--t-fast), border-color var(--t-fast)",
      }}>{label}</button>
    ))}
  </div>
);

const VerdictBlock = ({ result, apiError, siteCount, methods, section, setSection }) => {
  const [cited,       setCited]       = React.useState(false);
  const [docxLoading, setDocxLoading] = React.useState(false);

  const handleExportJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "cris_result.json"; a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportDOCX = async () => {
    if (!result || docxLoading) return;
    setDocxLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/export/docx`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(result),
      });
      if (!resp.ok) throw new Error("export failed");
      const blob = await resp.blob();
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href = url; a.download = "cris_result.docx"; a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("DOCX export:", e);
    } finally {
      setDocxLoading(false);
    }
  };

  const handleCite = () => {
    if (!result?.success) return;
    const { lattice, structure } = result;
    const activeMethods = [
      methods?.db                 && "DB matching",
      methods?.catboost           && "CatBoost",
      methods?.catboost_substance && "CatBoost-substance",
      methods?.rf                 && "Random Forest",
      methods?.automl             && "AutoML (ExtraTrees)",
    ].filter(Boolean).join(" + ") || "DB matching";
    const lines = [
      [structure?.name, structure?.formula && structure.formula !== structure.name ? `(${structure.formula})` : null, lattice?.name_en ? `, ${lattice.name_en}` : "", structure?.sg_hm ? `, ${structure.sg_hm}` : ""].filter(Boolean).join(" "),
      [structure?.cell_a != null ? `a = ${structure.cell_a.toFixed(3)} Å.` : null, lattice?.confidence != null ? `Confidence: ${lattice.confidence.toFixed(2)}.` : null].filter(Boolean).join(" "),
      structure?.sg_number ? `Space group ${structure.sg_number}.` : null,
      `Identified by CRIS v0.4.3 (${activeMethods}).`,
    ].filter(Boolean).join(" ");
    navigator.clipboard.writeText(lines).then(() => { setCited(true); setTimeout(() => setCited(false), 2000); });
  };

  if (apiError) return (
    <div>
      <WsLabel>Verdict</WsLabel>
      <div style={{ marginTop: 16, padding: "12px 14px", background: "rgba(229,62,62,0.07)", border: "1px solid rgba(229,62,62,0.18)", borderRadius: 8, fontSize: 13, color: "#c53030" }}>
        ⚠ {apiError}
      </div>
    </div>
  );

  const dbLatticeResult   = result?.success ? {
    name_en: result.lattice?.name_en, name_ru: result.lattice?.name_ru,
    confidence: result.lattice?.confidence, ranking: result.lattice_ranking,
  } : null;
  const dbSubstanceResult = result?.success && result.structure ? {
    name_en:    result.structure.name,
    name_ru:    result.structure.formula && result.structure.formula !== result.structure.name ? result.structure.formula : null,
    confidence: result.structure.confidence,
    ranking:    result.structure_ranking ?? [],
  } : null;
  const catboostResult          = result?.ml_results?.find(r => r.method === "catboost")           ?? null;
  const catboostSubstanceResult = result?.ml_results?.find(r => r.method === "catboost_substance") ?? null;
  const rfResult                = result?.ml_results?.find(r => r.method === "rf")                 ?? null;
  const automlResult            = result?.ml_results?.find(r => r.method === "automl")             ?? null;

  const structure = result?.success ? result.structure : null;

  return (
    <div>
      <WsLabel>Verdict</WsLabel>

      {/* Site count chip */}
      {siteCount > 0 && (
        <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
          <Chip tone="info">{siteCount} ions</Chip>
          {structure?.cell_a != null && <Chip tone="info">a = {structure.cell_a.toFixed(3)} Å</Chip>}
          {structure?.sg_hm         && <Chip tone="info">{structure.sg_hm}</Chip>}
        </div>
      )}

      {/* Section tabs */}
      <SectionTabs active={section} onChange={setSection} />

      {/* ── СИНГОНИЯ ── */}
      {section === "syngony" && (
        <div style={{ marginTop: 14 }}>
          {dbLatticeResult ? (
            <>
              <h3 className="section-title" style={{ fontSize: 26, margin: "0 0 4px" }}>{dbLatticeResult.name_en ?? "—"}</h3>
              {dbLatticeResult.name_ru && <div style={{ fontSize: 13, color: "var(--ink-soft)", marginBottom: 8 }}>{dbLatticeResult.name_ru}</div>}
            </>
          ) : (
            <p style={{ marginTop: 4, color: "var(--mute)", fontSize: 14 }}>{result?.message || "Совпадений в базе не найдено"}</p>
          )}
          <MethodResult label="По базе данных"      result={dbLatticeResult}  active={!!methods?.db}       emptyText="Нет совпадений в базе данных" />
          <MethodResult label="CatBoost · сингония" result={catboostResult}   active={!!methods?.catboost} emptyText="Нет данных от модели" />
        </div>
      )}

      {/* ── ПО ВЕЩЕСТВУ ── */}
      {section === "substance" && (
        <div style={{ marginTop: 14 }}>
          {dbSubstanceResult ? (
            <>
              <h3 className="section-title" style={{ fontSize: 26, margin: "0 0 4px" }}>{dbSubstanceResult.name_en ?? "—"}</h3>
              {dbSubstanceResult.name_ru && <div style={{ fontSize: 13, color: "var(--ink-soft)", marginBottom: 8 }}>{dbSubstanceResult.name_ru}</div>}
            </>
          ) : (
            <p style={{ marginTop: 4, color: "var(--mute)", fontSize: 14 }}>{result?.message || "Совпадений в базе не найдено"}</p>
          )}
          <MethodResult label="По базе данных"      result={dbSubstanceResult}      active={!!methods?.db}                  emptyText="Нет совпадений в базе данных" />
          <MethodResult label="CatBoost · вещество" result={catboostSubstanceResult} active={!!methods?.catboost_substance}  emptyText="Нет данных от модели" />
          <MethodResult label="Random Forest"        result={rfResult}                active={!!methods?.rf}                  emptyText="Нет данных от модели" />
          <MethodResult label="AutoML (ExtraTrees)" result={automlResult}            active={!!methods?.automl}              emptyText="Модель недоступна (требуется переобучение)" />
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <Button variant="quiet" size="sm" icon={<IconDownload size={14} />}
          onClick={handleExportJSON} disabled={!result}>JSON</Button>
        <Button variant="quiet" size="sm" icon={<IconDownload size={14} />}
          onClick={handleExportDOCX} disabled={!result || docxLoading}>
          {docxLoading ? "…" : "DOCX"}</Button>
        <Button variant="ghost" size="sm" icon={<IconCopy size={14} />}
          onClick={handleCite} disabled={!result?.success}>
          {cited ? "Скопировано!" : "Цитата"}
        </Button>
      </div>
    </div>
  );
};

/* ── Анимация "печатает..." ── */
const TypingDots = () => {
  const [dots, setDots] = React.useState(1);
  React.useEffect(() => {
    const id = setInterval(() => setDots(d => d === 3 ? 1 : d + 1), 420);
    return () => clearInterval(id);
  }, []);
  return (
    <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--mute)" }}>
      {"печатает" + ".".repeat(dots)}
    </span>
  );
};

/* ── Рендер текста: LaTeX + базовый Markdown ── */
const renderWithLatex = (text) => {
  const kt = window.katex;

  // Токены: \begin{...}...\end{...}, $$...$$, $...$, **...**, *...*
  const regex = /(\\begin\{[^}]+\}[\s\S]+?\\end\{[^}]+\}|\$\$[\s\S]+?\$\$|\$[^$\n]+?\$|\*\*[^*]+\*\*|\*[^*\n]+\*)/g;
  const parts = [];
  let last = 0, match, key = 0;

  const pushText = (str) => {
    str.split("\n").forEach((line, i, arr) => {
      parts.push(<span key={key++}>{line}</span>);
      if (i < arr.length - 1) parts.push(<br key={key++} />);
    });
  };

  const renderDisplay = (inner) => {
    try {
      const html = kt.renderToString(inner.trim(), { displayMode: true, throwOnError: false });
      parts.push(<span key={key++} dangerouslySetInnerHTML={{ __html: html }}
        style={{ display: "block", textAlign: "center", margin: "3px 0", overflowX: "auto" }} />);
    } catch { pushText(inner); }
  };

  while ((match = regex.exec(text)) !== null) {
    if (match.index > last) pushText(text.slice(last, match.index));

    const raw = match[0];
    if (!kt) { pushText(raw); }
    else if (raw.startsWith("\\begin{")) {
      renderDisplay(raw);
    } else if (raw.startsWith("$$")) {
      renderDisplay(raw.slice(2, -2));
    } else if (raw.startsWith("$")) {
      try {
        const html = kt.renderToString(raw.slice(1, -1).trim(), { displayMode: false, throwOnError: false });
        parts.push(<span key={key++} dangerouslySetInnerHTML={{ __html: html }} style={{ verticalAlign: "middle" }} />);
      } catch { pushText(raw); }
    } else if (raw.startsWith("**")) {
      parts.push(<strong key={key++}>{raw.slice(2, -2)}</strong>);
    } else if (raw.startsWith("*")) {
      parts.push(<em key={key++}>{raw.slice(1, -1)}</em>);
    } else {
      pushText(raw);
    }

    last = match.index + raw.length;
  }

  if (last < text.length) pushText(text.slice(last));
  return <span>{parts}</span>;
};

/* ── Chat ── */
const ChatPanel = ({ stage, sessionId, result, messages, setMessages }) => {
  const [input,   setInput]   = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error,   setError]   = React.useState(null);
  const bottomRef = React.useRef(null);
  const inputRef  = React.useRef(null);
  const active    = stage === "result" && !!sessionId;

  React.useEffect(() => {
    if (stage === "running") setError(null);
  }, [stage]);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "nearest" });
  }, [messages, loading]);

  // Строим строку с ML-результатами для системного промпта (Bug 2 fix)
  const buildResultContext = () => {
    if (!result) return null;
    const parts = [];
    const ml = result.ml_results || [];
    if (result.success && result.structure?.name) {
      parts.push(`База данных: ${result.structure.name}`);
      if (result.lattice?.name_en) parts.push(`Тип решётки (DB): ${result.lattice.name_en}`);
    }
    const cbSubst = ml.find(r => r.method === "catboost_substance");
    if (cbSubst?.name_en) parts.push(`CatBoost-вещество: ${cbSubst.name_en} (${cbSubst.confidence?.toFixed(1)}%)`);
    const rf = ml.find(r => r.method === "rf");
    if (rf?.name_en) parts.push(`Random Forest: ${rf.name_en} (${rf.confidence?.toFixed(1)}%)`);
    const cbSyng = ml.find(r => r.method === "catboost");
    if (cbSyng?.name_en) parts.push(`CatBoost-сингония: ${cbSyng.name_en} (${cbSyng.confidence?.toFixed(1)}%)`);
    return parts.length ? parts.join("\n") : null;
  };

  const send = async () => {
    const text = input.trim();
    if (!text || loading || !active) return;
    const userMsg = { role: "user", content: text };
    const history = [...messages, userMsg];
    setMessages(history); setInput(""); setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          messages: history,
          result_context: buildResultContext() || undefined,
        }),
      });
      if (!res.ok) { const err = await res.json().catch(() => ({})); throw new Error(err.detail || `HTTP ${res.status}`); }
      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); inputRef.current?.focus(); }
  };

  const onKeyDown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "16px 20px 20px", minHeight: 0, overflow: "hidden" }}>
      {/* [CHANGE 2] WsLabel instead of eyebrow span */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, flexShrink: 0 }}>
        <IconSparkles size={14} />
        <WsLabel>GigaChat MAX 2</WsLabel>
      </div>

      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 10, minHeight: 0 }}>
        {!active && stage !== "result" && <p style={{ margin: 0, color: "var(--mute)", fontSize: 13, fontStyle: "italic" }}>AI-ассистент включается после распознавания.</p>}
        {!active && stage === "result" && !sessionId && <p style={{ margin: 0, color: "var(--mute)", fontSize: 13, fontStyle: "italic" }}>Сессия не создана — повторите анализ.</p>}
        {active && messages.length === 0 && <p style={{ margin: 0, color: "var(--mute)", fontSize: 13, fontStyle: "italic" }}>Спросите про решётку, вещество или методы распознавания.</p>}
        {messages.map((m, i) => (
          <div key={i} style={{
            alignSelf:    m.role === "user" ? "flex-end" : "flex-start",
            background:   m.role === "user" ? "var(--cobalt)" : "var(--card)",
            color:        m.role === "user" ? "white" : "var(--ink)",
            border:       m.role === "assistant" ? "1px solid var(--hairline)" : "none",
            borderRadius: m.role === "user" ? "10px 10px 2px 10px" : "10px 10px 10px 2px",
            padding: "10px 14px", fontSize: 13, maxWidth: "88%", lineHeight: 1.6,
          }}>
            {m.role === "assistant" ? renderWithLatex(m.content) : m.content}
          </div>
        ))}
        {loading && (
          <div style={{ alignSelf: "flex-start", background: "var(--card)", border: "1px solid var(--hairline)", borderRadius: 10, padding: "10px 14px" }}>
            <TypingDots />
          </div>
        )}
        {error && (
          <div style={{ alignSelf: "flex-start", background: "#fff0f0", border: "1px solid #ffc0c0", borderRadius: 10, padding: "10px 14px", fontSize: 13, color: "#c00", maxWidth: "88%" }}>
            Ошибка: {error}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div style={{
        marginTop: 12, flexShrink: 0,
        display: "flex", gap: 8, alignItems: "center",
        border: `1px solid ${active ? "var(--hairline-strong)" : "var(--hairline)"}`,
        borderRadius: 8, background: "var(--card)",
        padding: "4px 4px 4px 14px", opacity: active ? 1 : 0.5,
      }}>
        <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={onKeyDown}
          placeholder={active ? "Спросите про вещество… (Enter)" : "Запустите распознавание"}
          disabled={!active || loading}
          style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontSize: 14, padding: "8px 0" }}
        />
        <Button variant="primary" size="sm" disabled={!active || loading || !input.trim()} icon={<IconSend size={14} />} onClick={send} />
      </div>
    </div>
  );
};

Object.assign(window, { WorkspaceScreen });
