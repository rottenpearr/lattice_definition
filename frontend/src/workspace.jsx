/* CRIS — Workspace screen (drag-n-drop, manual input, pipeline, verdict, chat) */

const API_BASE = "http://localhost:8002";

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

/* ── File size formatter ── */
function formatFileSize(bytes, siteCount) {
  const kb = (bytes / 1024).toFixed(1);
  return `${kb} KB · ${siteCount} sites`;
}

/* ── CIF parser → { sites, cell, coordType: "frac" } ── */
function parseCIF(text) {
  const lines = text.split(/\r?\n/);
  const cell  = { a: 5, b: 5, c: 5, alpha: 90, beta: 90, gamma: 90 };

  // Strip uncertainty notation e.g. "4.890(1)" → 4.890
  const stripUnc = v => parseFloat(String(v).replace(/\(.*?\)/, ""));

  // Key-value pass: grab cell params
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

  // Loop pass: find atom_site block with fract coords
  const sites = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    if (line.toLowerCase() === "loop_") {
      i++;
      // Collect header tags
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
        // Parse data rows
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
        // Skip non-atom_site loop data
        while (i < lines.length) {
          const dl = lines[i].trim();
          if (!dl || dl.startsWith("#")) { i++; continue; }
          if (dl.toLowerCase() === "loop_" || dl.startsWith("_")) break;
          i++;
        }
      }
    } else {
      i++;
    }
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

/* ============================================================
   WORKSPACE SCREEN
   ============================================================ */
const WorkspaceScreen = () => {
  const [stage, setStage]         = React.useState("input"); // input | running | result
  const [mode,  setMode]          = React.useState("file");  // file | manual
  const [file,  setFile]          = React.useState(null);    // null until file is loaded
  const [sites, setSites]         = React.useState([]);      // empty on start
  const [cell,  setCell]          = React.useState(DEFAULT_CELL);
  const [coordType, setCoordType] = React.useState("frac");
  const screenshotApiRef = React.useRef(null);

  /* Предупреждение при попытке закрыть/перезагрузить страницу */
  React.useEffect(() => {
    const isDirty = file !== null || stage === "running" || stage === "result";
    if (!isDirty) return;
    const handler = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [file, stage]);

  const start = () => {
    setStage("running");

    // Логируем сессию в БД (fire & forget — не блокирует UI)
    if (sites.length >= 2) {
      const cartSites = sites.map(s => {
        const fx = parseFloat(s.x) || 0;
        const fy = parseFloat(s.y) || 0;
        const fz = parseFloat(s.z) || 0;
        const [cx, cy, cz] = coordType === "cart"
          ? [fx, fy, fz]
          : fracToCart(fx, fy, fz, cell);
        return { label: s.label, x: cx, y: cy, z: cz };
      });
      fetch(`${API_BASE}/api/session`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ sites: cartSites }),
      }).catch(() => {}); // молча игнорируем если API недоступен
    }

    setTimeout(() => setStage("result"), 2400);
  };

  const reset = () => setStage("input");

  const handleScreenshot = () => {
    if (!screenshotApiRef.current) return;
    const dataUrl = screenshotApiRef.current.screenshot();
    const a = document.createElement("a");
    a.href     = dataUrl;
    a.download = "lattice_snapshot.png";
    a.click();
  };

  /* Called by FileInput after successful parse */
  const handleFileLoad = ({ file: f, sites: s, cell: cl, coordType: ct }) => {
    setFile({ name: f.name, size: formatFileSize(f.size, s.length) });
    setSites(s);
    if (cl) setCell(cl);
    setCoordType(ct || "frac");
  };

  /* Called by FileInput when user clicks X */
  const handleFileClear = () => {
    setFile(null);
    setSites(DEFAULT_SITES);
    setCell(DEFAULT_CELL);
    setCoordType("frac");
  };

  return (
    <main style={{ background: "var(--paper)", minHeight: "calc(100vh - 64px)" }}>
      <WorkspaceToolbar stage={stage} onReset={reset} />
      <div style={{ display: "grid", gridTemplateColumns: "360px 1fr 380px", height: "calc(100vh - 64px - 56px)", minHeight: 640 }}>
        <WsLeftPanel
          stage={stage} mode={mode} setMode={setMode}
          file={file}
          onFileLoad={handleFileLoad}
          onFileClear={handleFileClear}
          sites={sites} setSites={setSites}
          onStart={start}
        />
        <WsCenter
          stage={stage}
          sites={sites}
          cell={cell}
          coordType={coordType}
          onScreenshot={handleScreenshot}
          onViewerReady={(api) => { screenshotApiRef.current = api; }}
        />
        <WsRightPanel stage={stage} />
      </div>
    </main>
  );
};

const WorkspaceToolbar = ({ stage, onReset }) => (
  <div style={{ borderBottom: "1px solid var(--hairline)", background: "var(--paper)", height: 56, display: "flex", alignItems: "center", padding: "0 24px", gap: 24 }}>
    <div className="eyebrow">Workspace · session 2026-05-12-14:08</div>
    <div style={{ flex: 1 }} />
    <Chip dot tone={stage === "result" ? "ok" : stage === "running" ? "live" : "default"}>
      {stage === "result" ? "matched · 0.87" : stage === "running" ? "computing" : "idle"}
    </Chip>
    <Button variant="ghost" size="sm" icon={<IconHelp size={14} />}>Подсказка</Button>
    <Button variant="ghost" size="sm" icon={<IconRotate size={14} />} onClick={onReset}>Сбросить</Button>
  </div>
);

/* ============================================================
   LEFT PANEL — input
   ============================================================ */
const WsLeftPanel = ({ stage, mode, setMode, file, onFileLoad, onFileClear, sites, setSites, onStart }) => (
  <aside style={{ borderRight: "1px solid var(--hairline)", padding: 24, overflowY: "auto", background: "var(--paper)" }}>
    <Eyebrow>01 · Input</Eyebrow>
    <h3 className="section-title" style={{ fontSize: 22, margin: "10px 0 18px", lineHeight: 1.2 }}>Структура для распознавания</h3>
    <div style={{ marginBottom: 16 }}>
      <Seg
        value={mode}
        onChange={setMode}
        options={[
          { value: "file",   label: "Файл" },
          { value: "manual", label: "Координаты" },
        ]}
      />
    </div>
    {mode === "file"
      ? <FileInput file={file} onFileLoad={onFileLoad} onClear={onFileClear} />
      : <ManualInput sites={sites} setSites={setSites} />}
    <div style={{ marginTop: 20, padding: 16, background: "var(--card)", borderRadius: 10, border: "1px solid var(--hairline)" }}>
      <Eyebrow>Параметры</Eyebrow>
      <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 12 }}>
        <Field label="Метод">
          <select className="select">
            <option value="ensemble">Ensemble (RF + CatBoost + DB)</option>
            <option value="catboost">CatBoost</option>
            <option value="rf">Random Forest</option>
            <option value="kde">KDE Classifier</option>
            <option value="db">DB matching</option>
          </select>
        </Field>
        <Field label="Top-N результатов">
          <input className="input mono" defaultValue="5" />
        </Field>
      </div>
    </div>
    <div style={{ marginTop: 24 }}>
      <Button
        variant="primary" size="lg"
        iconRight={<IconArrowRight size={16} />}
        onClick={onStart}
        disabled={stage === "running"}
        style={{ width: "100%" }}
      >
        {stage === "running" ? "Распознавание…" : "Распознать решётку"}
      </Button>
    </div>
  </aside>
);

/* ── Interactive file drop zone ── */
const FileInput = ({ file, onFileLoad, onClear }) => {
  const inputRef = React.useRef(null);
  const [dragOver, setDragOver] = React.useState(false);
  const [parseError, setParseError] = React.useState(null);

  const processFile = (f) => {
    if (!f) return;
    const name = f.name.toLowerCase();
    if (!name.endsWith(".cif") && !name.endsWith(".xyz")) {
      setParseError("Поддерживаются только .cif и .xyz файлы");
      return;
    }
    setParseError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const parsed = name.endsWith(".cif") ? parseCIF(text) : parseXYZ(text);
        if (parsed.sites.length === 0) {
          setParseError("Не удалось найти атомы в файле");
          return;
        }
        if (onFileLoad) onFileLoad({ file: f, ...parsed });
      } catch (err) {
        setParseError("Ошибка парсинга: " + err.message);
      }
    };
    reader.onerror = () => setParseError("Не удалось прочитать файл");
    reader.readAsText(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    processFile(e.dataTransfer.files[0]);
  };

  const onDragOver  = (e) => { e.preventDefault(); setDragOver(true); };
  const onDragLeave = ()  => setDragOver(false);

  const onInputChange = (e) => {
    processFile(e.target.files[0]);
    // Reset so same file can be re-selected
    e.target.value = "";
  };

  return (
    <div>
      {/* Drop zone */}
      <div
        style={{
          border: `1.5px dashed ${dragOver ? "var(--cobalt)" : "var(--hairline-strong)"}`,
          borderRadius: 10,
          padding: 22,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 8,
          background: dragOver ? "rgba(59,130,246,0.06)" : "var(--card)",
          textAlign: "center",
          cursor: "pointer",
          transition: "border-color 0.15s, background 0.15s",
          userSelect: "none",
        }}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => inputRef.current && inputRef.current.click()}
      >
        <IconUpload size={28} style={{ color: dragOver ? "var(--cobalt)" : undefined }} />
        <div style={{ fontSize: 14, fontWeight: 500 }}>
          {dragOver ? "Отпустите файл" : "Перетащите CIF/XYZ"}
        </div>
        <div style={{ fontSize: 12, color: "var(--mute)" }}>
          или <span style={{ color: "var(--cobalt)", textDecoration: "underline" }}>выберите файл</span>
        </div>
        <div style={{ fontSize: 11, color: "var(--mute)", fontFamily: "var(--font-mono)" }}>
          до 1000 ионов · fractional · Wyckoff
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept=".cif,.xyz"
        style={{ display: "none" }}
        onChange={onInputChange}
      />

      {/* Parse error */}
      {parseError && (
        <div style={{
          marginTop: 8,
          fontSize: 12,
          color: "#f56565",
          padding: "8px 12px",
          background: "rgba(245,101,101,0.08)",
          borderRadius: 6,
          border: "1px solid rgba(245,101,101,0.2)",
        }}>
          ⚠ {parseError}
        </div>
      )}

      {/* Loaded file chip */}
      {file && (
        <div style={{
          marginTop: 12,
          padding: "10px 12px",
          border: "1px solid var(--hairline)",
          borderRadius: 6,
          display: "flex",
          alignItems: "center",
          gap: 10,
          background: "var(--card)",
        }}>
          <IconCube size={14} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              fontFamily: "var(--font-mono)",
              fontSize: 12,
              color: "var(--ink)",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}>{file.name}</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--mute)" }}>
              {file.size}
            </div>
          </div>
          <button
            style={{ background: "transparent", border: "none", color: "var(--mute)", cursor: "pointer" }}
            onClick={(e) => { e.stopPropagation(); if (onClear) onClear(); }}
            title="Убрать файл"
          >
            <IconClose size={14} />
          </button>
        </div>
      )}
    </div>
  );
};

const ManualInput = ({ sites, setSites }) => {
  const updateSite = (i, key, val) => {
    const next = sites.map((s, idx) => idx === i ? { ...s, [key]: val } : s);
    setSites(next);
  };
  const removeSite = (i) => setSites(sites.filter((_, idx) => idx !== i));
  const addSite    = ()  => setSites([...sites, { label: `X${sites.length + 1}`, x: "0.0000", y: "0.0000", z: "0.0000" }]);

  return (
    <div>
      <div style={{ background: "var(--card)", border: "1px solid var(--hairline)", borderRadius: 10, overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "56px 1fr 1fr 1fr 28px", padding: "8px 10px", background: "var(--paper-deep)", fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--mute)" }}>
          <span>label</span><span style={{ color: "#FF6B6B" }}>x</span><span style={{ color: "#6BFF9E" }}>y</span><span style={{ color: "#6B9EFF" }}>z</span><span />
        </div>
        {sites.map((s, i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "56px 1fr 1fr 1fr 28px", padding: "3px 8px", alignItems: "center", borderTop: i ? "1px solid var(--hairline)" : "none" }}>
            <input
              className="input mono"
              value={s.label}
              onChange={e => updateSite(i, "label", e.target.value)}
              style={{ padding: "5px 6px", fontSize: 12, border: "none", background: "transparent" }}
            />
            {["x", "y", "z"].map(axis => (
              <input
                key={axis}
                className="input mono"
                value={s[axis]}
                onChange={e => updateSite(i, axis, e.target.value)}
                style={{ padding: "5px 6px", fontSize: 12, border: "none", background: "transparent" }}
              />
            ))}
            <button onClick={() => removeSite(i)} style={{ background: "transparent", border: "none", color: "var(--mute)", cursor: "pointer" }}>
              <IconClose size={12} />
            </button>
          </div>
        ))}
      </div>
      <button
        onClick={addSite}
        style={{ marginTop: 8, background: "transparent", border: "1px dashed var(--hairline-strong)", borderRadius: 6, padding: "8px 12px", width: "100%", color: "var(--mute)", fontFamily: "var(--font-mono)", fontSize: 12, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
      >
        <IconPlus size={12} /> добавить ион
      </button>
    </div>
  );
};

/* ============================================================
   CENTER — 3D viewer + pipeline
   ============================================================ */
const WsCenter = ({ stage, sites, cell, coordType, onScreenshot, onViewerReady }) => {
  const [zoomPct, setZoomPct] = React.useState(100);
  const viewerApiRef = React.useRef(null);

  /* Normalise sites — memoised so identity is stable across zoom re-renders.
     Without useMemo, every setZoomPct call creates a new array reference,
     which triggers LatticeViewer3D's useEffect and resets the camera. */
  const normSites = React.useMemo(() => sites.map(s => ({
    ...s,
    symbol: s.symbol || parseSymbol(s.label),
  })), [sites]);

  const handleViewerReady = (api) => {
    viewerApiRef.current = api;
    if (onViewerReady) onViewerReady(api);
  };

  const handleZoomIn  = () => viewerApiRef.current?.zoomIn?.();
  const handleZoomOut = () => viewerApiRef.current?.zoomOut?.();

  return (
    <section className="viewer" style={{ position: "relative", color: "var(--night-ink)" }}>
      {/* Top overlay */}
      <div style={{ position: "absolute", top: 16, left: 16, right: 16, display: "flex", justifyContent: "space-between", zIndex: 5, pointerEvents: "none" }}>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--night-mute)" }}>
          3D viewer · {stage === "result" ? "UN_supercell_5x5x5" : stage === "input" && sites.length > 0 ? `preview · ${sites.length} sites · ${coordType}` : "—"}
        </div>
        <div style={{ display: "flex", gap: 8, pointerEvents: "all" }}>
          <DarkChip icon={<IconCamera size={12} />} onClick={onScreenshot}>screenshot</DarkChip>
          <DarkChip icon={<IconDownload size={12} />}>POSCAR</DarkChip>
          <DarkChip icon={<IconRotate size={12} />}>reset view</DarkChip>
        </div>
      </div>

      {/* 3D viewer — always mounted so OrbitControls are live */}
      {normSites.length > 0 ? (
        <LatticeViewer3D
          sites={normSites}
          cell={cell}
          coordType={coordType}
          onReady={handleViewerReady}
          onZoomChange={setZoomPct}
        />
      ) : (
        <ViewerEmpty />
      )}

      {/* Pipeline overlay while running */}
      {stage === "running" && <ViewerPipeline />}

      {/* Bottom axis legend */}
      <div style={{ position: "absolute", bottom: 16, left: 16, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--night-mute)", display: "flex", gap: 18, zIndex: 5, pointerEvents: "none" }}>
        <span><span style={{ color: "#FF5C5C" }}>●</span> X</span>
        <span><span style={{ color: "#5CFF8F" }}>●</span> Y</span>
        <span><span style={{ color: "#5C8FFF" }}>●</span> Z</span>
      </div>

      {/* Zoom controls */}
      <div style={{ position: "absolute", bottom: 16, right: 16, display: "flex", gap: 6, zIndex: 5, alignItems: "center" }}>
        {normSites.length > 0 && (
          <DarkChip>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, minWidth: 36, textAlign: "center", letterSpacing: ".04em" }}>
              {zoomPct}%
            </span>
          </DarkChip>
        )}
        <DarkChip icon={<IconMinus size={12} />} onClick={handleZoomOut} />
        <DarkChip icon={<IconPlus size={12} />}  onClick={handleZoomIn} />
      </div>
    </section>
  );
};

const DarkChip = ({ icon, children, onClick }) => (
  <button
    onClick={onClick}
    style={{ display: "inline-flex", gap: 6, alignItems: "center", padding: children ? "5px 10px" : 6, background: "rgba(14,16,20,0.72)", backdropFilter: "blur(10px)", border: "1px solid var(--night-line)", borderRadius: 6, color: "var(--night-ink)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".04em", cursor: "pointer" }}
  >
    {icon}{children}
  </button>
);

const ViewerEmpty = () => (
  <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", textAlign: "center", padding: 40 }}>
    <div>
      <LatticeDiagram size={260} animated={false} />
      <div style={{ marginTop: 20, fontFamily: "var(--font-display)", fontSize: 22, color: "var(--night-ink)" }}>Загрузите данные слева</div>
      <div style={{ marginTop: 6, fontSize: 14, color: "var(--night-mute)" }}>3D-сцена появится после добавления ионов</div>
    </div>
  </div>
);

const ViewerPipeline = () => (
  <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", padding: 40, background: "rgba(0,0,0,0.55)", zIndex: 4, backdropFilter: "blur(3px)" }}>
    <div style={{ width: 460, background: "rgba(14,16,20,0.85)", backdropFilter: "blur(16px)", border: "1px solid var(--night-line)", borderRadius: 10, padding: 28 }}>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--night-mute)", marginBottom: 18 }}>ML pipeline · live</div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">parse_input · {DEFAULT_SITES.length} sites</span><span className="pipeline-time">0.04s</span></div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">normalize_coordinates</span><span className="pipeline-time">0.12s</span></div>
      <div className="pipeline-step done"  ><span className="pipeline-dot" /><span className="pipeline-label">compute_pairwise_distances</span><span className="pipeline-time">0.31s</span></div>
      <div className="pipeline-step active"><span className="pipeline-dot" /><span className="pipeline-label">compute_kde_spectrum</span><span className="pipeline-time">…</span></div>
      <div className="pipeline-step pending"><span className="pipeline-dot" /><span className="pipeline-label">ensemble_predict (rf + catboost)</span><span className="pipeline-time">—</span></div>
      <div className="pipeline-step pending"><span className="pipeline-dot" /><span className="pipeline-label">match_reference_structure</span><span className="pipeline-time">—</span></div>
    </div>
  </div>
);

/* ============================================================
   RIGHT PANEL — verdict + chat
   ============================================================ */
/* Mock verdict context — заменить на реальные данные когда ML подключат */
const MOCK_VERDICT_CONTEXT = {
  lattice_type: "Кубическая гранецентрированная (FCC)",
  lattice_en:   "cubic_f",
  formula:      "UN",
  confidence:   0.87,
  sg_hm:        "Fm-3m",
  ion_count:    8,
};

const WsRightPanel = ({ stage }) => {
  const panelRef   = React.useRef(null);
  const [splitPct, setSplitPct] = React.useState(52); // % высоты под вердикт
  const dragging   = React.useRef(false);

  const onDividerMouseDown = (e) => {
    e.preventDefault();
    dragging.current = true;
    document.body.style.cursor = "row-resize";
    document.body.style.userSelect = "none";

    const onMouseMove = (ev) => {
      if (!dragging.current || !panelRef.current) return;
      const rect = panelRef.current.getBoundingClientRect();
      const pct  = ((ev.clientY - rect.top) / rect.height) * 100;
      setSplitPct(Math.min(Math.max(pct, 20), 78)); // зажимаем 20%–78%
    };

    const onMouseUp = () => {
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup",   onMouseUp);
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup",   onMouseUp);
  };

  return (
    <aside ref={panelRef} style={{ borderLeft: "1px solid var(--hairline)", display: "flex", flexDirection: "column", background: "var(--paper)", minHeight: 0, overflow: "hidden" }}>

      {/* Блок вердикта — высота задаётся splitPct */}
      <div style={{ height: `${splitPct}%`, flex: "0 0 auto", overflowY: "auto", minHeight: 0 }}>
        {stage === "result" ? <VerdictBlock /> : <VerdictPlaceholder />}
      </div>

      {/* Разделитель */}
      <div
        onMouseDown={onDividerMouseDown}
        style={{
          flexShrink:  0,
          height:      6,
          cursor:      "row-resize",
          background:  "var(--hairline)",
          borderTop:   "1px solid var(--hairline)",
          borderBottom:"1px solid var(--hairline)",
          display:     "flex",
          alignItems:  "center",
          justifyContent: "center",
          transition:  "background 0.15s",
        }}
        onMouseEnter={e => e.currentTarget.style.background = "var(--cobalt-wash)"}
        onMouseLeave={e => e.currentTarget.style.background = "var(--hairline)"}
      >
        {/* три точки-ручка */}
        <div style={{ display: "flex", gap: 3 }}>
          {[0,1,2].map(i => <div key={i} style={{ width: 3, height: 3, borderRadius: "50%", background: "var(--mute)" }} />)}
        </div>
      </div>

      {/* Чат — занимает остаток */}
      <ChatPanel stage={stage} context={stage === "result" ? MOCK_VERDICT_CONTEXT : null} />
    </aside>
  );
};

const VerdictPlaceholder = () => (
  <div>
    <Eyebrow>02 · Verdict</Eyebrow>
    <p style={{ marginTop: 16, color: "var(--mute)", fontSize: 14 }}>После запуска здесь появится тип решётки, эталонное вещество и экспорт.</p>
  </div>
);

const VerdictBlock = () => (
  <div>
    <Eyebrow>02 · Verdict</Eyebrow>
    <div style={{ marginTop: 14, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
      <h3 className="section-title" style={{ fontSize: 28, margin: 0 }}>cubic_f</h3>
      <Chip tone="ok" dot>0.87</Chip>
    </div>
    <div style={{ marginTop: 4, fontSize: 14, color: "var(--ink-soft)" }}>FCC · face-centered cubic · space group 225</div>
    <div style={{ marginTop: 14, display: "flex", gap: 6, flexWrap: "wrap" }}>
      <Chip tone="info">8 ions / cell</Chip>
      <Chip tone="info">a = 4.890 Å</Chip>
      <Chip tone="info">α=β=γ = 90°</Chip>
    </div>
    <hr className="hr" style={{ margin: "18px 0" }} />
    <Eyebrow>Probable substance</Eyebrow>
    <div style={{ marginTop: 10, fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 500 }}>Uranium nitride · UN</div>
    <div style={{ fontSize: 13, color: "var(--ink-soft)", marginTop: 4 }}>
      Тугоплавкое керамическое топливо. Высокая теплопроводность, плотность 14.32 г/см³. Используется в реакторах IV поколения.
    </div>
    <div style={{ marginTop: 12, display: "flex", gap: 6 }}>
      <Chip>mp-2731</Chip>
      <Chip>COD 1531114</Chip>
    </div>
    <hr className="hr" style={{ margin: "18px 0" }} />
    <Eyebrow>Top-5 ranking</Eyebrow>
    {[
      ["cubic_f",  "FCC",                  0.87, true ],
      ["cubic_p",  "primitive cubic",      0.07, false],
      ["cubic_i",  "BCC",                  0.04, false],
      ["tetra_p",  "primitive tetragonal", 0.01, false],
      ["hex_p",    "hexagonal",            0.01, false],
    ].map(([k, v, p, top], i) => (
      <div key={i} style={{ marginTop: 8, display: "grid", gridTemplateColumns: "76px 1fr 38px", gap: 10, alignItems: "center", fontFamily: "var(--font-mono)", fontSize: 12 }}>
        <span style={{ color: top ? "var(--cobalt)" : "var(--ink-soft)" }}>{k}</span>
        <div style={{ height: 4, background: "var(--hairline)", borderRadius: 2, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${p * 100}%`, background: top ? "var(--cobalt)" : "var(--mute-soft)" }} />
        </div>
        <span style={{ color: "var(--mute)", textAlign: "right" }}>{p.toFixed(2)}</span>
      </div>
    ))}
    <div style={{ display: "flex", gap: 8, marginTop: 18 }}>
      <Button variant="quiet" size="sm" icon={<IconDownload size={14} />}>JSON</Button>
      <Button variant="quiet" size="sm" icon={<IconDownload size={14} />}>DOCX</Button>
      <Button variant="ghost"  size="sm" icon={<IconCopy    size={14} />}>Цитата</Button>
    </div>
  </div>
);

const ChatPanel = ({ stage, context }) => {
  const [messages, setMessages] = React.useState([]); // [{role:"user"|"assistant", content:""}]
  const [input,    setInput]    = React.useState("");
  const [loading,  setLoading]  = React.useState(false);
  const [error,    setError]    = React.useState(null);
  const bottomRef = React.useRef(null);
  const inputRef  = React.useRef(null);

  const active = stage === "result";

  /* Сбрасываем историю когда пользователь запускает новое распознавание */
  React.useEffect(() => {
    if (stage === "running") {
      setMessages([]);
      setError(null);
    }
  }, [stage]);

  /* Автоскролл вниз при каждом новом сообщении */
  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading || !active) return;

    const userMsg = { role: "user", content: text };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history,
          context:  context || null,
        }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: 24, minHeight: 0, overflow: "hidden" }}>

      {/* Заголовок */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14, flexShrink: 0 }}>
        <IconSparkles size={14} />
        <span className="eyebrow" style={{ margin: 0 }}>AI · GigaChat MAX 2</span>
        {loading && (
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--mute)", fontFamily: "var(--font-mono)" }}>
            печатает…
          </span>
        )}
      </div>

      {/* Лента сообщений */}
      <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 12, minHeight: 0 }}>

        {/* Заглушка до распознавания */}
        {!active && (
          <p style={{ margin: 0, color: "var(--mute)", fontSize: 13, fontStyle: "italic" }}>
            AI-ассистент включается после распознавания.
          </p>
        )}

        {/* Подсказка после вердикта, если диалог пустой */}
        {active && messages.length === 0 && (
          <p style={{ margin: 0, color: "var(--mute)", fontSize: 13, fontStyle: "italic" }}>
            Спросите про решётку, вещество или методы распознавания.
          </p>
        )}

        {/* Сообщения */}
        {messages.map((m, i) => (
          <div key={i} style={{
            alignSelf:    m.role === "user" ? "flex-end" : "flex-start",
            background:   m.role === "user" ? "var(--cobalt)" : "var(--card)",
            color:        m.role === "user" ? "white" : "var(--ink)",
            border:       m.role === "assistant" ? "1px solid var(--hairline)" : "none",
            borderRadius: 10,
            padding:      "10px 14px",
            fontSize:     14,
            maxWidth:     "85%",
            lineHeight:   1.55,
            whiteSpace:   "pre-wrap",
          }}>
            {m.content}
          </div>
        ))}

        {/* Индикатор загрузки */}
        {loading && (
          <div style={{
            alignSelf: "flex-start", background: "var(--card)",
            border: "1px solid var(--hairline)", borderRadius: 10,
            padding: "10px 14px", fontSize: 14, color: "var(--mute)",
            fontFamily: "var(--font-mono)",
          }}>
            ···
          </div>
        )}

        {/* Ошибка */}
        {error && (
          <div style={{
            alignSelf: "flex-start", background: "#fff0f0",
            border: "1px solid #ffc0c0", borderRadius: 10,
            padding: "10px 14px", fontSize: 13, color: "#c00", maxWidth: "85%",
          }}>
            Ошибка: {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Поле ввода */}
      <div style={{
        marginTop: 12, flexShrink: 0,
        display: "flex", gap: 8, alignItems: "center",
        border: `1px solid ${active ? "var(--hairline-strong)" : "var(--hairline)"}`,
        borderRadius: 6, background: "var(--card)",
        padding: "4px 4px 4px 12px",
        opacity: active ? 1 : 0.5,
      }}>
        <input
          ref={inputRef}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={active ? "Спросите про вещество… (Enter)" : "Запустите распознавание"}
          disabled={!active || loading}
          style={{ flex: 1, border: "none", outline: "none", background: "transparent", fontSize: 14, padding: "8px 0" }}
        />
        <Button
          variant="primary" size="sm"
          disabled={!active || loading || !input.trim()}
          icon={<IconSend size={14} />}
          onClick={send}
        />
      </div>
    </div>
  );
};

Object.assign(window, { WorkspaceScreen });
