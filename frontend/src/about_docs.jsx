/* CRIS — About + Docs */

const AboutScreen = () => (
  <main>
    <section className="bg-lattice" style={{ padding: "80px 0 64px", borderBottom: "1px solid var(--hairline)" }}>
      <div className="container" style={{ maxWidth: 920 }}>
        <Eyebrow>О проекте</Eyebrow>
        <h1 className="section-title" style={{ fontSize: 56, lineHeight: 1.04, margin: "20px 0 24px", letterSpacing: "-0.025em" }}>
          Как CRIS распознаёт<br />тип решётки.
        </h1>
        <p style={{ fontSize: 18, color: "var(--ink-soft)", lineHeight: 1.55, maxWidth: 680, margin: 0 }}>
          Четыре независимых метода голосуют параллельно. Их прогнозы объединяются в ансамблевый ранкинг с явной оценкой согласованности.
        </p>
      </div>
    </section>
    <section className="section-tight">
      <div className="container" style={{ maxWidth: 920 }}>
        <Eyebrow>Методы распознавания</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 24 }}>
          {[
            { n: "01", t: "Нормализация координат", b: "Минимум сдвигается в начало координат, всё делится на глобальный максимум — получаем куб [0, 1]. Это делает совпадение независимым от масштаба и положения ячейки." },
            { n: "02", t: "KDE-спектр попарных расстояний", b: "Считаем все попарные расстояния между ионами, прогоняем через гауссов KDE. Получаем непрерывный спектр, устойчивый к небольшим шумам и вакансиям." },
            { n: "03", t: "Random Forest по KDE-вектору", b: "Дискретизованный KDE-вектор подаётся в RF, обученный на 1240+ эталонных структурах (Materials Project + COD). Возвращает дистрибуцию по 8 типам решёток." },
            { n: "04", t: "CatBoost-классификатор", b: "Параллельная модель на тех же фичах, но с другим деревьями решений. Используется как проверка-голосование: согласие моделей повышает confidence." },
            { n: "05", t: "Сравнение с эталонной БД", b: "Top-1 предсказание используется для поиска ближайшей реальной структуры в эталонной БД по L2-расстоянию KDE. Возвращает имя вещества и ссылки на COD/MP." },
          ].map((m, i) => (
            <Card pad="lg" key={i} style={{ display: "grid", gridTemplateColumns: "60px 1fr", gap: 24, alignItems: "start" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: "var(--cobalt)" }}>{m.n}</div>
              <div>
                <h3 className="section-title" style={{ fontSize: 22, margin: "0 0 8px", lineHeight: 1.25 }}>{m.t}</h3>
                <p style={{ margin: 0, fontSize: 15, color: "var(--ink-soft)", lineHeight: 1.6 }}>{m.b}</p>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
    <section id="team" className="section" style={{ background: "var(--paper-deep)", borderTop: "1px solid var(--hairline)" }}>
      <div className="container" style={{ maxWidth: 920 }}>
        <Eyebrow>Подробнее об авторах</Eyebrow>
        <h2 className="section-title" style={{ fontSize: 36, margin: "16px 0 32px", lineHeight: 1.1 }}>Дипломные работы и зоны ответственности</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            { name: "Артюшин", topic: "«Развитие системы распознавания типов кристаллических решёток с применением методов радиального распределения ближайших соседей и машинного обучения»", area: "ML-инженер · RF / CatBoost · ансамбли · работа с патентом" },
            { name: "Маркова", topic: "«Внедрение механизмов распознавания типов кристаллических решёток для автоматизации определения методов молекулярно-динамических исследований»", area: "Архитектор БД · поисковик эталонов · интеграция COD / Materials Project" },
            { name: "Черняков", topic: "«Развитие системы глобального распознавания типов кристаллов с применением методов AI/ML для численного материаловедения»", area: "Backend · собственная нейросеть · 3D-визуализация · математика на numpy" },
          ].map((a, i) => (
            <Card pad="lg" key={i}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12 }}>
                <h3 className="section-title" style={{ fontSize: 22, margin: 0 }}>{a.name}</h3>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--mute)" }}>diploma · 2026</span>
              </div>
              <p style={{ margin: "10px 0 0", fontSize: 14, color: "var(--ink-soft)", lineHeight: 1.55 }}>{a.topic}</p>
              <div style={{ marginTop: 12, fontSize: 13, color: "var(--cobalt-deep)", fontFamily: "var(--font-mono)" }}>{a.area}</div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  </main>
);

const DocsScreen = () => (
  <main style={{ background: "var(--paper)" }}>
    <div className="container" style={{ maxWidth: 1080, padding: "64px 32px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: 56 }}>
        <aside style={{ position: "sticky", top: 96, alignSelf: "start" }}>
          <Eyebrow>Документация</Eyebrow>
          <nav style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 8, fontSize: 14 }}>
            {["Quick start", "Установка", "Python API", "REST API", "Форматы данных", "GitHub", "Глоссарий"].map((s, i) => (
              <a key={i} style={{ color: i === 0 ? "var(--ink)" : "var(--ink-soft)", fontWeight: i === 0 ? 500 : 400, cursor: "pointer", padding: "4px 0", borderLeft: i === 0 ? "2px solid var(--ink)" : "2px solid transparent", paddingLeft: 12, marginLeft: -12 }}>{s}</a>
            ))}
          </nav>
        </aside>
        <article>
          <Eyebrow>Quick start</Eyebrow>
          <h1 className="section-title" style={{ fontSize: 44, lineHeight: 1.05, margin: "16px 0 16px" }}>
            От установки до первого вердикта за 3 минуты.
          </h1>
          <p style={{ fontSize: 17, color: "var(--ink-soft)", lineHeight: 1.55, margin: "0 0 32px" }}>
            CRIS можно использовать двумя путями: через веб-интерфейс на этом сайте, либо встроить в свой Python-пайплайн как библиотеку.
          </p>

          <DocStep n="01" title="Установка библиотеки">
            <CodeBlock>{`pip install cris-core`}</CodeBlock>
            <p style={{ fontSize: 14, color: "var(--ink-soft)", marginTop: 10 }}>Требует Python 3.9+. PostgreSQL не нужен — модель и эталонная база лежат внутри пакета.</p>
          </DocStep>

          <DocStep n="02" title="Распознавание из CIF">
            <CodeBlock>{`from cris import identify

verdict = identify("UN_supercell.cif")
print(verdict.type)         # 'cubic_f'
print(verdict.substance)    # 'Uranium nitride · UN'
print(verdict.confidence)   # 0.87`}</CodeBlock>
          </DocStep>

          <DocStep n="03" title="Свои координаты">
            <CodeBlock>{`from cris import identify_coords

coords = [
    ("U", 0.0, 0.0, 0.0),
    ("U", 0.5, 0.5, 0.0),
    ("N", 0.5, 0.5, 0.5),
    ("N", 0.0, 0.0, 0.5),
]
verdict = identify_coords(coords, method="ensemble")
verdict.top(5)`}</CodeBlock>
          </DocStep>

          <DocStep n="04" title="REST API">
            <CodeBlock>{`curl -X POST https://api.cris.science/v1/identify \\
  -H "Content-Type: application/json" \\
  -d '{"format":"xyz","data":"U 0 0 0\\nU 0.5 0.5 0\\n..."}'`}</CodeBlock>
            <p style={{ fontSize: 14, color: "var(--ink-soft)", marginTop: 10 }}>Ответ — JSON со структурой <code style={{ fontFamily: "var(--font-mono)", background: "var(--cobalt-wash)", padding: "2px 6px", borderRadius: 4, fontSize: 13, color: "var(--cobalt-deep)" }}>VerdictPayload</code>. Подробности — на странице REST API.</p>
          </DocStep>

          <div style={{ marginTop: 40, padding: 24, background: "var(--cobalt-wash)", borderRadius: 10, display: "flex", gap: 20, alignItems: "center" }}>
            <IconInfo size={20} />
            <div>
              <div style={{ fontWeight: 500, marginBottom: 4 }}>Нужна интеграция?</div>
              <div style={{ fontSize: 14, color: "var(--ink-soft)" }}>Напишите на team@cris.science — поможем встроить ансамбль в ваш пайплайн или развернуть on-prem.</div>
            </div>
          </div>
        </article>
      </div>
    </div>
  </main>
);

const DocStep = ({ n, title, children }) => (
  <div style={{ marginBottom: 32 }}>
    <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginBottom: 12 }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".08em", color: "var(--cobalt)" }}>{n}</span>
      <h2 className="section-title" style={{ fontSize: 24, margin: 0 }}>{title}</h2>
    </div>
    {children}
  </div>
);

const CodeBlock = ({ children }) => (
  <pre style={{ background: "var(--ink)", color: "var(--night-ink)", padding: "16px 18px", borderRadius: 8, fontFamily: "var(--font-mono)", fontSize: 13, lineHeight: 1.55, overflowX: "auto", margin: 0 }}>
    <code>{children}</code>
  </pre>
);

Object.assign(window, { AboutScreen, DocsScreen });
