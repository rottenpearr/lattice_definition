/* CRIS — Home screen */

const HomeScreen = ({ setRoute }) => (
  <main>
    <Hero setRoute={setRoute} />
    <FeaturesSection />
    <DescriptionSection />
    <TeamSection />
    <EmbedSection />
  </main>
);

/* ---------- Hero ---------- */
const Hero = ({ setRoute }) => (
  <section className="bg-lattice" style={{ paddingTop: 96, paddingBottom: 120, borderBottom: "1px solid var(--hairline)" }}>
    <div className="container" style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 64, alignItems: "center" }}>
      <div>
        <Eyebrow>Crystal recognition · v0.4.1</Eyebrow>
        <h1 className="section-title" style={{ fontSize: 72, lineHeight: 1.02, margin: "20px 0 24px", letterSpacing: "-0.025em" }}>
          Определяем тип<br />кристаллической<br />решётки по координатам<span style={{ color: "var(--cobalt)" }}>.</span>
        </h1>
        <p style={{ fontSize: 19, color: "var(--ink-soft)", lineHeight: 1.5, maxWidth: 540, margin: 0 }}>
          Загрузите CIF/XYZ или введите координаты ионов вручную. Ансамбль RF + CatBoost + KDE-сравнение вернёт тип решётки Браве, ближайшее эталонное вещество и 3D-визуализацию ячейки.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 32 }}>
          <Button variant="primary" size="lg" iconRight={<IconArrowRight size={16} />} onClick={() => setRoute("workspace")}>
            Перейти в workspace
          </Button>
          <Button variant="secondary" size="lg" icon={<IconBook size={16} />} onClick={() => setRoute("docs")}>
            Quick start
          </Button>
        </div>
        <div style={{ marginTop: 32, display: "flex", gap: 28, fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".06em", color: "var(--mute)", textTransform: "uppercase" }}>
          <span>● 8 типов решёток</span><span>● 4 ML-метода</span><span>● 1240+ эталонных структур</span>
        </div>
      </div>
      <HeroVisual />
    </div>
  </section>
);

const HeroVisual = () => (
  <div style={{ background: "var(--night)", borderRadius: 14, padding: 24, position: "relative", overflow: "hidden",
                boxShadow: "var(--shadow-pop)", aspectRatio: "5 / 4" }}>
    <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 30% 25%, rgba(37,64,255,0.22), transparent 55%), radial-gradient(circle at 70% 80%, rgba(220,255,58,0.12), transparent 55%)" }} />
    <div style={{ position: "relative", display: "flex", justifyContent: "space-between", color: "var(--night-mute)", fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase" }}>
      <span>3d viewer · live</span>
      <span style={{ color: "var(--signal)" }}>● matched</span>
    </div>
    <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", height: 240 }}>
      <LatticeDiagram size={220} />
    </div>
    <div style={{ position: "relative", borderTop: "1px solid var(--night-line)", paddingTop: 14, marginTop: 8, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--night-mute)" }}>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>type</div><div style={{ color: "var(--night-ink)", fontSize: 13 }}>cubic_f · FCC</div></div>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>match</div><div style={{ color: "var(--night-ink)", fontSize: 13 }}>UN · mp-2731</div></div>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>conf.</div><div style={{ color: "var(--signal)", fontSize: 13 }}>0.87</div></div>
    </div>
  </div>
);

const LatticeDiagram = ({ size = 220, animated = true }) => {
  // 2x2x2 FCC-ish isometric lattice
  const nodes = [];
  for (let z = 0; z < 2; z++) for (let y = 0; y < 2; y++) for (let x = 0; x < 2; x++) {
    nodes.push([x, y, z]);
  }
  const project = ([x, y, z]) => {
    const sx = (x - z) * 60 + size / 2;
    const sy = (x + z) * 30 + y * -60 + size / 2 + 30;
    return [sx, sy];
  };
  const edges = [];
  for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
    const [a, b, c] = nodes[i], [d, e, f] = nodes[j];
    if (Math.abs(a - d) + Math.abs(b - e) + Math.abs(c - f) === 1) edges.push([nodes[i], nodes[j]]);
  }
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {edges.map(([n1, n2], i) => {
        const [x1, y1] = project(n1), [x2, y2] = project(n2);
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(255,255,255,0.32)" strokeWidth="1" />;
      })}
      {nodes.map((n, i) => {
        const [cx, cy] = project(n);
        const highlight = i === 5;
        return (
          <circle key={i} cx={cx} cy={cy} r={highlight ? 7 : 5}
                  fill={highlight ? "var(--signal)" : "var(--cobalt)"}
                  stroke={highlight ? "var(--signal)" : "rgba(255,255,255,0.4)"}
                  strokeWidth="1.5"
                  style={animated && highlight ? { animation: "node-pulse 1.6s ease-in-out infinite" } : {}} />
        );
      })}
    </svg>
  );
};

/* ---------- Features ---------- */
const FeaturesSection = () => {
  const features = [
    { eyebrow: "01 · INPUT", title: "Любой источник данных", body: "CIF, XYZ или ручной ввод координат. Поддерживаются supercell до 1000 ионов, нормализация в куб [0, 1] идёт автоматически." },
    { eyebrow: "02 · METHOD", title: "Ансамбль ML, не один метод", body: "Random Forest, CatBoost и KDE-similarity голосуют параллельно. Видны все ранкинги и confidence по каждому методу." },
    { eyebrow: "03 · VERDICT", title: "Не только тип, но и вещество", body: "Кроме типа решётки Браве, сервис возвращает наиболее вероятное вещество и ссылки на эталоны в COD / Materials Project." },
    { eyebrow: "04 · ASK", title: "AI-агент рядом с вердиктом", body: "GigaChat MAX 2 знает базу CRIS и научные источники. Спросите про вещество, метод или интерпретацию результата." },
    { eyebrow: "05 · 3D", title: "Поворачиваемая визуализация", body: "Интерактивная 3D-сцена ячейки в стиле VESTA. Скриншот, экспорт в PNG/POSCAR — в одно нажатие." },
    { eyebrow: "06 · EMBED", title: "Библиотека для своего пайплайна", body: "Тот же ансамбль доступен как pip-пакет `cris-core`. REST API и Python SDK работают с теми же эталонами." },
  ];
  return (
    <section className="section">
      <div className="container">
        <SectionTitle eyebrow="Ключевые особенности" title="Шесть причин использовать CRIS" lead="Всё, что нужно для распознавания решётки в рабочем процессе — от загрузки до встраивания в свой пайплайн." />
        <div style={{ marginTop: 56, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
          {features.map((f, i) => (
            <Card pad="lg" key={i}>
              <Eyebrow>{f.eyebrow}</Eyebrow>
              <h3 className="section-title" style={{ fontSize: 22, margin: "16px 0 12px", lineHeight: 1.2 }}>{f.title}</h3>
              <p style={{ margin: 0, fontSize: 15, color: "var(--ink-soft)", lineHeight: 1.55 }}>{f.body}</p>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ---------- Description ---------- */
const API_BASE_HOME = "http://localhost:8001";

const DescriptionSection = () => {
  const [liveStats, setLiveStats] = React.useState(null);

  React.useEffect(() => {
    fetch(`${API_BASE_HOME}/api/stats`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) setLiveStats(data); })
      .catch(() => {});
  }, []);

  const structCount  = liveStats ? `${liveStats.struct_count}+`  : "1240+";
  const latticeCount = liveStats ? String(liveStats.lattice_count) : "8";
  const sessionCount = liveStats ? String(liveStats.session_count) : "—";

  const statCards = [
    { n: structCount,  l: "эталонных структур" },
    { n: latticeCount, l: "типов решёток Браве" },
    { n: "0.94",       l: "F1 на тестовом сете" },
    { n: sessionCount, l: "сессий распознавания" },
  ];

  return (
    <section className="section-tight" style={{ background: "var(--paper-deep)", borderTop: "1px solid var(--hairline)", borderBottom: "1px solid var(--hairline)" }}>
      <div className="container" style={{ display: "grid", gridTemplateColumns: "1fr 1.1fr", gap: 64, alignItems: "center" }}>
        <div>
          <Eyebrow>Что это и зачем</Eyebrow>
          <h2 className="section-title" style={{ fontSize: 40, lineHeight: 1.08, margin: "16px 0 20px" }}>
            Кристаллография<br />без VESTA, MS и часов ручной работы.
          </h2>
          <p style={{ fontSize: 16, color: "var(--ink-soft)", lineHeight: 1.6, margin: 0 }}>
            Распознавание типа решётки по позициям атомов — рутинная, но утомительная задача в материаловедении и MD-исследованиях. CRIS делает её одним запросом: подайте координаты, получите тип, эталон и confidence.
          </p>
          <p style={{ fontSize: 16, color: "var(--ink-soft)", lineHeight: 1.6, marginTop: 16 }}>
            Веб-сервис нужен научному сообществу как открытая, воспроизводимая альтернатива закрытым коммерческим пакетам — с прозрачным датасетом, открытыми весами моделей и полным аудит-логом каждого распознавания.
          </p>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {statCards.map((s, i) => (
            <Card pad="lg" key={i}>
              <div style={{ fontFamily: "var(--font-display)", fontSize: 44, fontWeight: 500, letterSpacing: "-0.022em", color: "var(--ink)", fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>{s.n}</div>
              <div style={{ marginTop: 10, fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--mute)" }}>{s.l}</div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ---------- Team ---------- */
const TeamSection = () => {
  const team = [
    { initials: "АА", name: "Артюшин", role: "ML-инженер · радиальное распределение, ансамбли" },
    { initials: "МА", name: "Маркова",  role: "Архитектор БД · поисковик эталонов, COD/MP" },
    { initials: "ЧЕ", name: "Черняков", role: "Backend + 3D · нейросеть, визуализация, материаловедение" },
  ];
  return (
    <section className="section">
      <div className="container">
        <SectionTitle eyebrow="Команда" title="Три исследователя, один пайплайн" lead="CRIS — результат трёх дипломных работ в области численного материаловедения и распознавания." />
        <div style={{ marginTop: 48, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
          {team.map((t, i) => (
            <Card pad="lg" key={i}>
              <div style={{ width: 56, height: 56, borderRadius: 999, background: "var(--ink)", color: "var(--paper)", display: "grid", placeItems: "center", fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: 16, letterSpacing: ".02em" }}>{t.initials}</div>
              <div style={{ marginTop: 20, fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 500, color: "var(--ink)" }}>{t.name}</div>
              <div style={{ marginTop: 6, fontSize: 14, color: "var(--ink-soft)", lineHeight: 1.5 }}>{t.role}</div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

/* ---------- Embed / GitHub ---------- */
const EmbedSection = () => (
  <section className="section" style={{ background: "var(--ink)", color: "var(--night-ink)" }}>
    <div className="container" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 64, alignItems: "center" }}>
      <div>
        <div className="eyebrow" style={{ color: "var(--night-mute)" }}>
          <style>{`.eyebrow{color:var(--night-mute);} .eyebrow::before{background:var(--signal);}`}</style>
          Open source · MIT
        </div>
        <h2 className="section-title" style={{ fontSize: 44, color: "var(--night-ink)", margin: "20px 0 20px", letterSpacing: "-0.022em", lineHeight: 1.05 }}>
          Встройте CRIS<br />в свой исследовательский пайплайн.
        </h2>
        <p style={{ fontSize: 16, color: "var(--night-mute)", lineHeight: 1.6, margin: 0, maxWidth: 480 }}>
          Тот же ансамбль распознавания доступен как Python-пакет и REST API. Один интерфейс — для веб-приложения и для batch-режима на кластере.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 32 }}>
          <Button variant="primary" size="lg" icon={<IconGithub size={16} />} iconRight={<IconArrowUpRight size={14} />}>github.com/cris-team/cris</Button>
          <Button variant="secondary" size="lg" onDark icon={<IconBook size={16} />}>Docs</Button>
        </div>
      </div>
      <div style={{ background: "var(--night-elev)", borderRadius: 10, border: "1px solid var(--night-line)", padding: 20, fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--night-ink)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", color: "var(--night-mute)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", marginBottom: 16 }}>
          <span>$ install + use</span>
          <span style={{ display: "inline-flex", gap: 6, alignItems: "center", color: "var(--signal)" }}><IconCopy size={12}/>copy</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, lineHeight: 1.6 }}>
          <div><span style={{ color: "var(--signal)" }}>$</span> pip install cris-core</div>
          <div style={{ color: "var(--night-mute)" }}># or in Python:</div>
          <div><span style={{ color: "#8AB4FF" }}>from</span> cris <span style={{ color: "#8AB4FF" }}>import</span> identify</div>
          <div>verdict = identify(<span style={{ color: "#DCFF3A" }}>"un_supercell.cif"</span>)</div>
          <div>verdict.type   <span style={{ color: "var(--night-mute)" }}># 'cubic_f'</span></div>
          <div>verdict.confidence  <span style={{ color: "var(--night-mute)" }}># 0.87</span></div>
        </div>
      </div>
    </div>
  </section>
);

Object.assign(window, { HomeScreen, LatticeDiagram });
