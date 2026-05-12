/* ============================================================
   CRIS — Header & Footer
   ============================================================ */

const HEADER_H = 64;

const Header = ({ route, setRoute }) => {
  const [hidden, setHidden] = React.useState(false);
  const lastY = React.useRef(0);

  /* Hide on scroll-down, reveal on scroll-up or near top */
  React.useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      if (y <= 10) {
        setHidden(false);
      } else if (y > lastY.current + 40) {
        setHidden(true);
      } else if (y < lastY.current - 10) {
        setHidden(false);
      }
      lastY.current = y;
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* Always show header when route changes */
  React.useEffect(() => {
    setHidden(false);
    lastY.current = window.scrollY;
  }, [route]);

  const items = [
    { id: "home",      label: "Главная" },
    { id: "workspace", label: "Рабочее пространство" },
    { id: "about",     label: "О проекте" },
    { id: "docs",      label: "Документация" },
  ];

  return (
    <header style={{
      position:   "fixed",
      top: 0, left: 0, right: 0,
      zIndex:     50,
      height:     HEADER_H,
      background: "rgba(242,239,232,0.92)",
      backdropFilter: "blur(12px)",
      borderBottom: "1px solid var(--hairline)",
      transform:  hidden ? "translateY(-100%)" : "translateY(0)",
      transition: "transform 0.28s cubic-bezier(0.4, 0, 0.2, 1)",
      willChange: "transform",
    }}>
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: HEADER_H }}>
        <a onClick={() => setRoute("home")} style={{ cursor: "pointer" }}><Wordmark /></a>
        <nav style={{ display: "flex", gap: 28 }}>
          {items.map(i => (
            <span
              key={i.id}
              className={`nav-link ${route === i.id ? "active" : ""}`}
              onClick={() => setRoute(i.id)}
              style={{ cursor: "pointer" }}
            >
              {i.label}
            </span>
          ))}
        </nav>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <Button variant="ghost" size="sm" icon={<IconGithub size={16} />}>GitHub</Button>
          <Button variant="primary" size="sm" iconRight={<IconArrowRight size={14} />} onClick={() => setRoute("workspace")}>
            Открыть workspace
          </Button>
        </div>
      </div>
    </header>
  );
};

const Footer = ({ setRoute }) => (
  <footer style={{ background: "var(--ink)", color: "var(--night-ink)", padding: "64px 0 32px" }}>
    <div className="container" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 48 }}>
      <div>
        <Wordmark color="var(--night-ink)" node="var(--signal)" />
        <p style={{ marginTop: 16, fontSize: 14, color: "var(--night-mute)", lineHeight: 1.6, maxWidth: 360 }}>
          Crystal Recognition & Identification System. Веб-сервис для определения типа кристаллической решётки по координатам ионов.
        </p>
        <div style={{ marginTop: 20, display: "flex", gap: 8, alignItems: "center", fontSize: 13, color: "var(--night-mute)", fontFamily: "var(--font-mono)" }}>
          <IconMail size={14} /> team@cris.science
        </div>
      </div>
      <FooterCol title="Сервис" links={[
        ["Главная", () => setRoute("home")],
        ["Workspace", () => setRoute("workspace")],
        ["Документация", () => setRoute("docs")],
      ]} />
      <FooterCol title="Проект" links={[
        ["О методах", () => setRoute("about")],
        ["Команда", () => setRoute("about", "team")],
        ["GitHub", null],
        ["Patentr", null],
      ]} />
      <FooterCol title="Связь" links={[
        ["team@cris.science", null],
        ["bugs@cris.science", null],
        ["press@cris.science", null],
      ]} />
    </div>
    <div className="container" style={{ marginTop: 48, paddingTop: 24, borderTop: "1px solid var(--night-line)", display: "flex", justifyContent: "space-between", color: "var(--night-mute)", fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".04em" }}>
      <span>© 2026 CRIS · MIT licence</span>
      <span>build 2026.05.12 · v0.4.1</span>
    </div>
  </footer>
);

const FooterCol = ({ title, links }) => (
  <div>
    <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--night-mute)", marginBottom: 16 }}>{title}</div>
    <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
      {links.map(([label, onClick], i) => (
        <li key={i}>
          <span
            onClick={onClick || undefined}
            style={{ fontSize: 14, color: "var(--night-ink)", cursor: onClick ? "pointer" : "default", opacity: onClick ? 1 : 0.7 }}
          >
            {label}
          </span>
        </li>
      ))}
    </ul>
  </div>
);

Object.assign(window, { Header, Footer });
