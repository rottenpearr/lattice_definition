/* CRIS — About + Docs */

const AboutScreen = () => {
  const isMobile = useIsMobile();
  return (
  <main>
    <section className="bg-lattice" style={{ padding: isMobile ? "60px 0 40px" : "80px 0 64px", borderBottom: "1px solid var(--hairline)" }}>
      <div className="container" style={{ maxWidth: 920 }}>
        <Eyebrow>О проекте</Eyebrow>
        <h1 className="section-title" style={{ fontSize: isMobile ? 36 : 56, lineHeight: 1.04, margin: "20px 0 24px", letterSpacing: "-0.025em" }}>
          Как CRIS распознаёт<br />тип решётки.
        </h1>
        <p style={{ fontSize: 18, color: "var(--ink-soft)", lineHeight: 1.55, maxWidth: 680, margin: 0 }}>
          Входные координаты проходят предобработку и преобразуются в числовой дескриптор, который подаётся в три независимых классификатора. Каждый возвращает свой результат с оценкой достоверности.
        </p>
      </div>
    </section>
    <section className="section-tight">
      <div className="container" style={{ maxWidth: 920 }}>
        <Eyebrow>Пайплайн обработки</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 24 }}>
          {[
            { n: "01", t: "Нормализация координат", b: "Минимальные координаты сдвигаются в начало, затем все значения делятся на глобальный максимум — ячейка приводится к кубу [0, 1]. Результат не зависит от масштаба и ориентации исходной структуры." },
            { n: "02", t: "Построение KDE-дескриптора", b: "Для каждого типа иона считаются расстояния до всех остальных. Распределение расстояний сглаживается гауссовым KDE на сетке [0, 2] из 200 точек. Векторы по всем типам ионов усредняются в единый 200-мерный дескриптор." },
            { n: "03", t: "Классификатор Random Forest", b: "200-мерный вектор подаётся в Random Forest, обученный на эталонных структурах соединений урана. Модель возвращает вероятности принадлежности к известным структурным фазам (UC, U₂C₃ и др.)." },
            { n: "04", t: "Классификатор CatBoost", b: "Тот же дескриптор подаётся в CatBoost — независимую модель на основе градиентного бустинга. Работает параллельно с RF и возвращает собственный ранкинг типов решёток с оценкой достоверности." },
            { n: "05", t: "Поиск ближайшего эталона в БД", b: "KDE-дескриптор сравнивается с векторами всех эталонных структур в базе по L2-расстоянию. Ближайшее совпадение возвращается как наиболее вероятное реальное соединение с названием вещества и оценкой близости." },
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
        <Eyebrow>Об авторах</Eyebrow>
        <h2 className="section-title" style={{ fontSize: 36, margin: "16px 0 32px", lineHeight: 1.1 }}>Дипломные работы и зоны ответственности</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {[
            {
              name: "Артюшин Артём Александрович",
              initials: "АА",
              photo: "assets/team/artyushin.jpg",
              topic: "«Разработка алгоритмов для системы распознавания типов кристаллических решёток с использованием ядерной оценки плотности радиального распределения и машинного обучения»",
              area: "Математическое и алгоритмическое обоснование метода идентификации · радиальная функция распределения · ядерная оценка плотности · классификатор Random Forest · обучение моделей машинного обучения",
            },
            {
              name: "Маркова Алёна Денисовна",
              initials: "МА",
              photo: "assets/team/markova.jpg",
              topic: "«Разработка программной архитектуры информационной системы CRIS для автоматизированной идентификации типов кристаллических решёток»",
              area: "Программная архитектура комплекса · серверная часть · веб-клиент · эталонная база данных · встраиваемая программная библиотека",
            },
            {
              name: "Черняков Матвей Сергеевич",
              initials: "ЧМ",
              photo: "assets/team/chernyakov.jpg",
              topic: "«Проектирование и внедрение RAG-системы с применением AI/ML-механизмов в программный комплекс CRIS»",
              area: "Подсистема AI/ML-механизмов · RAG-обогащение метаданных · диалоговый ИИ-помощник · формирование обучающего датасета · классификатор CatBoost",
            },
          ].map((a, i) => (
            <Card pad="lg" key={i}>
              <div style={{ display: "flex", flexDirection: isMobile ? "column" : "row", gap: 20, alignItems: isMobile ? "flex-start" : "flex-start" }}>
                <div style={{ flexShrink: 0 }}>
                  {a.photo
                    ? <img src={a.photo} alt={a.name} style={{ width: isMobile ? 80 : 100, height: isMobile ? 80 : 100, borderRadius: "50%", objectFit: "cover", objectPosition: "top center", display: "block" }} />
                    : <div style={{ width: isMobile ? 80 : 100, height: isMobile ? 80 : 100, borderRadius: "50%", background: "var(--ink)", color: "var(--paper)", display: "grid", placeItems: "center", fontFamily: "var(--font-mono)", fontWeight: 600, fontSize: 24, letterSpacing: ".02em" }}>{a.initials}</div>
                  }
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: isMobile ? "flex-start" : "baseline", flexDirection: isMobile ? "column" : "row", gap: isMobile ? 4 : 12 }}>
                    <h3 className="section-title" style={{ fontSize: isMobile ? 17 : 20, margin: 0 }}>{a.name}</h3>
                    {!isMobile && <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--mute)", whiteSpace: "nowrap" }}>diploma · 2026</span>}
                  </div>
                  <p style={{ margin: "8px 0 0", fontSize: isMobile ? 13 : 14, color: "var(--ink-soft)", lineHeight: 1.55, fontStyle: "italic" }}>{a.topic}</p>
                  <div style={{ marginTop: 10, fontSize: 12, color: "var(--cobalt-deep)", fontFamily: "var(--font-mono)" }}>{a.area}</div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </section>
  </main>
  );
};

const DocsScreen = () => {
  const isMobile = useIsMobile();
  return (
  <main style={{ background: "var(--paper)" }}>
    <div className="container" style={{ maxWidth: 1080, padding: isMobile ? "40px 20px" : "64px 32px" }}>
      <div style={{ display: "grid", gridTemplateColumns: isMobile ? "1fr" : "220px 1fr", gap: isMobile ? 24 : 56 }}>
        <aside style={isMobile ? { marginBottom: 8 } : { position: "sticky", top: 96, alignSelf: "start" }}>
          <Eyebrow>Документация</Eyebrow>
          <nav style={{ marginTop: 18, display: "flex", flexDirection: "column", gap: 8, fontSize: 14 }}>
            {["Quick start", "Установка", "Python API", "REST API", "Форматы данных", "GitHub", "Глоссарий"].map((s, i) => (
              <a key={i} style={{ color: i === 0 ? "var(--ink)" : "var(--ink-soft)", fontWeight: i === 0 ? 500 : 400, cursor: "pointer", padding: "4px 0", borderLeft: i === 0 ? "2px solid var(--ink)" : "2px solid transparent", paddingLeft: 12, marginLeft: -12 }}>{s}</a>
            ))}
          </nav>
        </aside>
        <article style={{ minWidth: 0, overflowX: "hidden" }}>
          <Eyebrow>Quick start</Eyebrow>
          <h1 className="section-title" style={{ fontSize: isMobile ? 28 : 44, lineHeight: 1.05, margin: "16px 0 16px" }}>
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
};

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
  <pre style={{ background: "var(--ink)", color: "var(--night-ink)", padding: "16px 18px", borderRadius: 8, fontFamily: "var(--font-mono)", fontSize: 13, lineHeight: 1.55, overflowX: "auto", margin: 0, maxWidth: "100%", boxSizing: "border-box" }}>
    <code style={{ display: "block", minWidth: 0 }}>{children}</code>
  </pre>
);

Object.assign(window, { AboutScreen, DocsScreen });
