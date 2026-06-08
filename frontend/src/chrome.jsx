/* ============================================================
   CRIS — Header & Footer
   ============================================================ */

const HEADER_H = 64;

const Header = ({ route, setRoute }) => {
  const isMobile = useIsMobile();
  const [hidden,   setHidden]   = React.useState(false);
  const [menuOpen, setMenuOpen] = React.useState(false);
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
    setMenuOpen(false);
    lastY.current = window.scrollY;
  }, [route]);

  const items = [
    { id: "home",  label: "Главная" },
    { id: "about", label: "О проекте" },
    { id: "docs",  label: "Документация" },
  ];

  const navigate = (id) => { setRoute(id); setMenuOpen(false); };

  return (
    <header style={{
      position:   "fixed",
      top: 0, left: 0, right: 0,
      zIndex:     50,
      background: "rgba(242,239,232,0.92)",
      backdropFilter: "blur(12px)",
      borderBottom: "1px solid var(--hairline)",
      transform:  hidden ? "translateY(-100%)" : "translateY(0)",
      transition: "transform 0.28s cubic-bezier(0.4, 0, 0.2, 1)",
      willChange: "transform",
    }}>
      {/* ── Main bar ── */}
      <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: HEADER_H }}>
        <a onClick={() => navigate("home")} style={{ cursor: "pointer" }}><Wordmark /></a>

        {/* Desktop nav */}
        {!isMobile && (
          <nav style={{ display: "flex", gap: 28 }}>
            {items.map(i => (
              <span key={i.id} className={`nav-link ${route === i.id ? "active" : ""}`}
                onClick={() => navigate(i.id)} style={{ cursor: "pointer" }}>
                {i.label}
              </span>
            ))}
          </nav>
        )}

        {/* Desktop buttons */}
        {!isMobile && (
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <Button variant="ghost" size="sm" icon={<IconGithub size={16} />}
              onClick={() => window.open("https://github.com/rottenpearr/lattice_definition", "_blank")}>GitHub</Button>
            <Button variant="primary" size="sm" iconRight={<IconArrowRight size={14} />}
              onClick={() => navigate("workspace")}>Открыть workspace</Button>
          </div>
        )}

        {/* Mobile hamburger */}
        {isMobile && (
          <button
            onClick={() => setMenuOpen(o => !o)}
            style={{ background: "transparent", border: "none", cursor: "pointer", padding: 8, color: "var(--ink)", display: "flex", alignItems: "center" }}
            aria-label="Меню"
          >
            {menuOpen ? <IconClose size={22} /> : <IconMenu size={22} />}
          </button>
        )}
      </div>

      {/* ── Mobile dropdown menu ── */}
      {isMobile && menuOpen && (
        <div style={{
          background: "rgba(242,239,232,0.98)", backdropFilter: "blur(12px)",
          borderTop: "1px solid var(--hairline)",
          padding: "12px 0 20px",
        }}>
          <div className="container" style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            {items.map(i => (
              <span key={i.id}
                onClick={() => navigate(i.id)}
                style={{
                  display: "block", padding: "13px 0",
                  fontSize: 16, fontWeight: route === i.id ? 600 : 400,
                  color: route === i.id ? "var(--ink)" : "var(--ink-soft)",
                  borderBottom: "1px solid var(--hairline)", cursor: "pointer",
                }}>
                {i.label}
              </span>
            ))}
            <div style={{ marginTop: 16, display: "flex", flexDirection: "column", gap: 10 }}>
              <Button variant="primary" iconRight={<IconArrowRight size={14} />}
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => navigate("workspace")}>Открыть workspace</Button>
              <Button variant="ghost" icon={<IconGithub size={16} />}
                style={{ width: "100%", justifyContent: "center" }}
                onClick={() => window.open("https://github.com/rottenpearr/lattice_definition", "_blank")}>GitHub</Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

const Footer = ({ setRoute }) => {
  const isMobile = useIsMobile();
  return (
  <footer style={{ background: "var(--ink)", color: "var(--night-ink)", padding: "64px 0 32px" }}>
    <div className="container" style={{ display: "grid", gridTemplateColumns: isMobile ? "1fr 1fr" : "2fr 1fr 1fr 1fr", gap: isMobile ? 32 : 48 }}>
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
        ["GitHub", () => window.open("https://github.com/rottenpearr/lattice_definition", "_blank")],
        ["Патент", null],
      ]} />
      <FooterCol title="Связь" links={[
        ["team@cris.science", null],
        ["bugs@cris.science", null],
        ["press@cris.science", null],
      ]} />
    </div>
    <div className="container" style={{ marginTop: 48, paddingTop: 24, borderTop: "1px solid var(--night-line)", display: "flex", justifyContent: "space-between", color: "var(--night-mute)", fontFamily: "var(--font-mono)", fontSize: 12, letterSpacing: ".04em" }}>
      <span>© 2026 CRIS · MIT licence</span>
      <span>build 2026.05.12 · v0.4.3</span>
    </div>
  </footer>
  );
};

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
