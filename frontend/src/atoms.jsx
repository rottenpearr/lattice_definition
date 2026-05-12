/* ============================================================
   CRIS — Atoms: Button, Eyebrow, Chip, Card, Field, Seg, etc.
   ============================================================ */

const Button = ({ variant = "primary", size = "md", icon, iconRight, children, onDark = false, ...rest }) => {
  const cls = [
    "btn",
    `btn-${variant}`,
    size === "sm" && "btn-sm",
    size === "lg" && "btn-lg",
    !children && "btn-icon",
    onDark && "btn-on-dark",
  ].filter(Boolean).join(" ");
  return (
    <button className={cls} {...rest}>
      {icon}
      {children}
      {iconRight}
    </button>
  );
};

const Eyebrow = ({ children }) => <span className="eyebrow">{children}</span>;

const Chip = ({ tone = "default", children, dot = false }) => {
  const toneCls = {
    default: "", info: "chip-info", ok: "chip-ok", warn: "chip-warn",
    bad: "chip-bad", live: "chip-live", ink: "chip-ink",
  }[tone] || "";
  return (
    <span className={`chip ${toneCls}`}>
      {dot && <span className="chip-dot" />}
      {children}
    </span>
  );
};

const Card = ({ pad = "md", children, className = "", style }) => (
  <div className={`card ${pad === "lg" ? "card-pad-lg" : "card-pad"} ${className}`} style={style}>
    {children}
  </div>
);

const Field = ({ label, children }) => (
  <label className="field">
    <span className="field-label">{label}</span>
    {children}
  </label>
);

const Seg = ({ options, value, onChange }) => (
  <div className="seg">
    {options.map((o) => (
      <button key={o.value} className={value === o.value ? "active" : ""} onClick={() => onChange(o.value)}>
        {o.label}
      </button>
    ))}
  </div>
);

const KV = ({ k, v, mono = true }) => (
  <div style={{ display: "flex", justifyContent: "space-between", gap: 16, padding: "8px 0", borderBottom: "1px solid var(--hairline)" }}>
    <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--mute)" }}>{k}</span>
    <span style={{ fontFamily: mono ? "var(--font-mono)" : "var(--font-body)", fontSize: 13, color: "var(--ink)", fontVariantNumeric: "tabular-nums" }}>{v}</span>
  </div>
);

const SectionTitle = ({ eyebrow, title, lead, align = "left", small = false }) => (
  <div style={{ textAlign: align, maxWidth: 720, margin: align === "center" ? "0 auto" : undefined }}>
    {eyebrow && <div style={{ marginBottom: 18 }}><Eyebrow>{eyebrow}</Eyebrow></div>}
    <h2 className="section-title" style={{ fontSize: small ? 32 : 44, margin: 0, lineHeight: 1.06 }}>{title}</h2>
    {lead && <p style={{ marginTop: 16, fontSize: 17, lineHeight: 1.55, color: "var(--ink-soft)" }}>{lead}</p>}
  </div>
);

const Logo = ({ size = 32, color = "currentColor", node = "#2540FF" }) => (
  <svg width={size * 56 / 56} height={size} viewBox="0 0 56 56" fill="none">
    <g transform="translate(4,8)" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 14 L28 6 L46 14 L28 22 Z" />
      <path d="M10 32 L28 24 L46 32 L28 40 Z" />
      <path d="M10 14 L10 32" />
      <path d="M28 6  L28 24" />
      <path d="M46 14 L46 32" />
      <path d="M28 22 L28 40" />
    </g>
    <circle cx="32" cy="30" r="3.6" fill={node} />
  </svg>
);

const Wordmark = ({ color = "var(--ink)", node = "var(--cobalt)" }) => (
  <div style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
    <Logo size={28} color={color} node={node} />
    <span style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 22, letterSpacing: "-0.02em", color }}>
      CRIS
    </span>
  </div>
);

Object.assign(window, { Button, Eyebrow, Chip, Card, Field, Seg, KV, SectionTitle, Logo, Wordmark });
