/* CRIS — App entry (updated: workspace uses its own header) */

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(err) {
    return { error: err };
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 48, fontFamily: "monospace", fontSize: 13, background: "#fff0f0", minHeight: "60vh" }}>
          <div style={{ fontWeight: 700, fontSize: 16, color: "#c00", marginBottom: 16 }}>⚠ Runtime error in WorkspaceScreen</div>
          <pre style={{ whiteSpace: "pre-wrap", color: "#333" }}>{String(this.state.error)}</pre>
          <pre style={{ whiteSpace: "pre-wrap", color: "#888", marginTop: 12, fontSize: 11 }}>{this.state.error?.stack}</pre>
          <button onClick={() => this.setState({ error: null })} style={{ marginTop: 24, padding: "8px 16px", cursor: "pointer" }}>
            Попробовать снова
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

const VALID_ROUTES = ["home", "workspace", "about", "docs"];

const App = () => {
  const [route, setRoute] = React.useState(() => {
    const saved = sessionStorage.getItem("cris_route");
    return VALID_ROUTES.includes(saved) ? saved : "home";
  });
  const [anchor, setAnchor] = React.useState(null);

  React.useEffect(() => {
    sessionStorage.setItem("cris_route", route);
  }, [route]);

  const navigate = React.useCallback((id, anchorId) => {
    setRoute(id);
    if (anchorId) {
      setAnchor(anchorId);
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, []);

  React.useEffect(() => {
    if (!anchor) return;
    let id1, id2;
    id1 = requestAnimationFrame(() => {
      id2 = requestAnimationFrame(() => {
        const el = document.getElementById(anchor);
        if (el) {
          const top = el.getBoundingClientRect().top + window.scrollY - 80;
          window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
        }
        setAnchor(null);
      });
    });
    return () => { cancelAnimationFrame(id1); cancelAnimationFrame(id2); };
  }, [route, anchor]);

  return (
    <>
      {/* [CHANGE] Global header hidden on workspace — it has its own dark header */}
      {route !== "workspace" && <Header route={route} setRoute={navigate} />}
      {route !== "workspace" && <div style={{ height: 64 }} />}

      {route === "home" && <HomeScreen setRoute={navigate} />}

      {route === "workspace" && (
        <ErrorBoundary>
          {/* [CHANGE] Pass setRoute so WorkspaceHeader can navigate back to home */}
          <WorkspaceScreen setRoute={navigate} />
        </ErrorBoundary>
      )}

      {route === "about" && <AboutScreen />}
      {route === "docs"  && <DocsScreen />}
      {route !== "workspace" && <Footer setRoute={navigate} />}
    </>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
