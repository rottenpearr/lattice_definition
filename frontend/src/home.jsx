/* CRIS — Home screen */

const HomeScreen = ({ setRoute }) => (
  <main>
    <Hero setRoute={setRoute} />
    <FeaturesSection />
    <DescriptionSection />
    <TeamSection />
    <EmbedSection setRoute={setRoute} />
  </main>
);

/* ---------- Hero ---------- */
const Hero = ({ setRoute }) => (
  <section className="bg-lattice" style={{ paddingTop: 96, paddingBottom: 120, borderBottom: "1px solid var(--hairline)" }}>
    <div className="container" style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 64, alignItems: "center" }}>
      <div>
        <Eyebrow>Crystal recognition · v0.4.3</Eyebrow>
        <h1 className="section-title" style={{ fontSize: 72, lineHeight: 1.02, margin: "20px 0 24px", letterSpacing: "-0.025em" }}>
          Определяем тип<br />кристаллической<br />решётки<span style={{ color: "var(--cobalt)" }}>.</span>
        </h1>
        <p style={{ fontSize: 19, color: "var(--ink-soft)", lineHeight: 1.5, maxWidth: 540, margin: 0 }}>
          Загрузите CIF/XYZ или введите координаты ионов вручную. Система определит тип кристаллической решётки, найдёт ближайшую эталонную структуру и построит 3D-визуализацию ячейки.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 32 }}>
          <Button variant="primary" size="lg" iconRight={<IconArrowRight size={16} />} onClick={() => setRoute("workspace")}>
            Перейти в workspace
          </Button>
          <Button variant="secondary" size="lg" icon={<IconBook size={16} />} onClick={() => setRoute("docs")}>
            Быстрый старт
          </Button>
        </div>
        <div style={{ marginTop: 32, display: "flex", gap: 28, fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".06em", color: "var(--mute)", textTransform: "uppercase" }}>
          <span>● 3 метода распознавания</span><span>● 1240+ эталонных структур</span><span>● открытый исходный код</span>
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
      <span style={{ color: "var(--signal)" }}>● распознано</span>
    </div>
    <div style={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center", height: 270 }}>
      <LatticeDiagram size={250} />
    </div>
    <div style={{ position: "relative", borderTop: "1px solid var(--night-line)", paddingTop: 14, marginTop: 8, display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 8, fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--night-mute)" }}>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>тип</div><div style={{ color: "var(--night-ink)", fontSize: 13 }}>FCC · кубическая ГЦК</div></div>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>совпадение</div><div style={{ color: "var(--night-ink)", fontSize: 13 }}>UN · mp-2731</div></div>
      <div><div style={{ textTransform: "uppercase", letterSpacing: ".08em", marginBottom: 2 }}>уверенность</div><div style={{ color: "var(--signal)", fontSize: 13 }}>0.87</div></div>
    </div>
  </div>
);

const LatticeDiagram = ({ size = 220, animated = true }) => {
  // FCC unit cell: 8 corners + 6 face-centre atoms
  const project = ([x, y, z]) => {
    const sx = (x - z) * 60 + size / 2;
    const sy = (x + z) * 30 + y * -60 + size / 2 + 30;
    return [sx, sy];
  };

  // Corners of the unit cell
  const corners = [];
  for (let z = 0; z < 2; z++) for (let y = 0; y < 2; y++) for (let x = 0; x < 2; x++) {
    corners.push([x, y, z]);
  }

  // 6 face-centre atoms (FCC positions)
  const faceCentres = [
    [0.5, 0.5, 0],   // top face
    [0.5, 0.5, 1],   // bottom face
    [0.5, 0,   0.5], // front face
    [0.5, 1,   0.5], // back face
    [0,   0.5, 0.5], // left face
    [1,   0.5, 0.5], // right face
  ];

  // Cube-frame edges (corners only, for a clean outline)
  const edges = [];
  for (let i = 0; i < corners.length; i++) for (let j = i + 1; j < corners.length; j++) {
    const [a, b, c] = corners[i], [d, e, f] = corners[j];
    if (Math.abs(a - d) + Math.abs(b - e) + Math.abs(c - f) === 1) edges.push([corners[i], corners[j]]);
  }

  // Index 0 → (0.5,0.5,0) — top face centre is the "detected" highlighted atom
  const highlightIdx = 0;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      {/* Cube-frame edges */}
      {edges.map(([n1, n2], i) => {
        const [x1, y1] = project(n1), [x2, y2] = project(n2);
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(255,255,255,0.28)" strokeWidth="1" />;
      })}
      {/* Corner atoms — cobalt blue */}
      {corners.map((n, i) => {
        const [cx, cy] = project(n);
        return (
          <circle key={`c${i}`} cx={cx} cy={cy} r={5}
                  fill="var(--cobalt)"
                  stroke="rgba(255,255,255,0.4)"
                  strokeWidth="1.5" />
        );
      })}
      {/* Face-centre atoms — slightly lighter, one pulsing green */}
      {faceCentres.map((n, i) => {
        const [cx, cy] = project(n);
        const highlight = i === highlightIdx;
        return (
          <circle key={`f${i}`} cx={cx} cy={cy} r={highlight ? 7 : 5}
                  fill={highlight ? "var(--signal)" : "rgba(100,140,255,0.9)"}
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
    { eyebrow: "01 · INPUT", title: "Любой источник данных", body: "CIF, XYZ или ручной ввод координат. Поддерживаются макроструктуры до 1000 ионов, нормализация координат в куб [0, 1] проходит автоматически." },
    { eyebrow: "02 · METHOD", title: "Ансамбль методов, не один", body: "Random Forest, CatBoost и поиск по внутренней базе данных работают параллельно. Доступны ранжирование и достоверность по каждому методу." },
    { eyebrow: "03 · VERDICT", title: "Не только тип, но и структура", body: "Кроме типа кристаллической решётки, система возвращает наиболее вероятную эталонную структуру и ссылки на эталоны в COD и Materials Project." },
    { eyebrow: "04 · ASK", title: "AI-ассистент в контексте анализа", body: "GigaChat-2-Max отвечает на вопросы в контексте сессии. Спросите про вещество, метод или интерпретацию результата." },
    { eyebrow: "05 · 3D", title: "Удобная визуализация", body: "Интерактивная 3D-сцена элементарной ячейки с возможностью вращения и масштабирования прямо в браузере." },
    { eyebrow: "06 · EMBED", title: "Встраиваемая библиотека", body: "Тот же ансамбль доступен как пакет `cris-core`. REST API и Python SDK работают с теми же эталонами." },
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
const API_BASE_HOME = "http://localhost:8002";

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
    { n: "3",          l: "метода распознавания" },
    { n: "0.94",       l: "точность распознавания" },
    { n: sessionCount, l: "сессий распознавания" },
  ];

  return (
    <section className="section-tight" style={{ background: "var(--paper-deep)", borderTop: "1px solid var(--hairline)", borderBottom: "1px solid var(--hairline)" }}>
      <div className="container" style={{ display: "grid", gridTemplateColumns: "1fr 1.1fr", gap: 64, alignItems: "center" }}>
        <div>
          <Eyebrow>Что это и зачем</Eyebrow>
          <h2 className="section-title" style={{ fontSize: 40, lineHeight: 1.08, margin: "16px 0 20px" }}>
            Кристаллография<br />без часов ручной работы.
          </h2>
          <p style={{ fontSize: 16, color: "var(--ink-soft)", lineHeight: 1.6, margin: 0 }}>
            Распознавание типа решётки по позициям атомов — рутинная, но утомительная задача в материаловедении и MD-исследованиях. CRIS делает её одним запросом: подайте координаты, получите тип, эталон и оценку достоверности.
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
    { initials: "АА", photo: null,                        name: "Артюшин Артём",   role: "Математическое и алгоритмическое обоснование · РФР · KDE · Random Forest" },
    { initials: "МА", photo: "assets/team/markova.jpg",   name: "Маркова Алёна",   role: "Программная архитектура · серверная часть · веб-клиент · БД · библиотека" },
    { initials: "ЧМ", photo: "assets/team/chernyakov.jpg",name: "Черняков Матвей", role: "AI/ML-механизмы · RAG · ИИ-ассистент · датасет · CatBoost" },
  ];
  return (
    <section className="section">
      <div className="container">
        <SectionTitle eyebrow="Команда" title="Авторы" lead="CRIS — результат трёх дипломных работ в области численного материаловедения и распознавания." />
        <div style={{ marginTop: 48, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 24 }}>
          {team.map((t, i) => (
            <Card pad="lg" key={i}>
              {t.photo
                ? <img src={t.photo} alt={t.name} style={{ width: 96, height: 96, borderRadius: "50%", objectFit: "cover", objectPosition: "top center", display: "block" }} />
                : <div style={{ width: 96, height: 96, borderRadius: 999, background: "var(--ink)", color: "var(--paper)", display: "grid", placeItems: "center", fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: 22, letterSpacing: ".02em" }}>{t.initials}</div>
              }
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
const EmbedSection = ({ setRoute }) => (
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
          <Button variant="primary" size="lg" icon={<IconGithub size={16} />} iconRight={<IconArrowUpRight size={14} />} onClick={() => window.open("https://github.com/rottenpearr/lattice_definition", "_blank")}>github.com/rottenpearr/lattice_definition</Button>
          <Button variant="secondary" size="lg" onDark icon={<IconBook size={16} />} onClick={() => setRoute("docs")}>Документация</Button>
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
