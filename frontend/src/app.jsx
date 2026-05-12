/* CRIS — App entry */

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

const App = () => {
  const [route, setRoute] = React.useState("home");
  const [anchor, setAnchor] = React.useState(null);

  /* Navigate: change route + optional anchor scroll */
  const navigate = React.useCallback((id, anchorId) => {
    setRoute(id);
    if (anchorId) {
      setAnchor(anchorId);
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, []);

  /* After route renders, scroll to pending anchor with header offset */
  React.useEffect(() => {
    if (!anchor) return;
    // Double-rAF: first frame React commits DOM, second frame layout is stable
    let id1, id2;
    id1 = requestAnimationFrame(() => {
      id2 = requestAnimationFrame(() => {
        const el = document.getElementById(anchor);
        if (el) {
          const top = el.getBoundingClientRect().top + window.scrollY - 80; // 64px header + 16px gap
          window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
        }
        setAnchor(null);
      });
    });
    return () => { cancelAnimationFrame(id1); cancelAnimationFrame(id2); };
  }, [route, anchor]);

  return (
    <>
      <Header route={route} setRoute={navigate} />
      {/* Spacer so content starts below the fixed header */}
      <div style={{ height: 64 }} />
      {route === "home" && <HomeScreen setRoute={navigate} />}
      {route === "workspace" && (
        <ErrorBoundary>
          <WorkspaceScreen />
        </ErrorBoundary>
      )}
      {route === "about" && <AboutScreen />}
      {route === "docs" && <DocsScreen />}
      {route !== "workspace" && <Footer setRoute={navigate} />}
    </>
  );
};

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
