/* ================================================================
   CRIS — LatticeViewer3D
   WebGL 3D visualisation of crystal lattice sites (VESTA-style).

   Props:
     sites    : [{label, symbol, x, y, z}]  coordinates (frac or cart)
     cell     : {a, b, c, alpha, beta, gamma}  Å / degrees (optional)
     coordType: "frac" | "cart"  — fractional (default) or Cartesian Å
     onReady  : (api) => void  — called once with { screenshot }
   ================================================================ */

/* ── Helpers ──────────────────────────────────────────────────── */

const CPK_COLORS = {
  H: 0xFFFFFF, He: 0xD9FFFF, Li: 0xCC80FF, Be: 0xC2FF00,
  B: 0xFFB5B5, C: 0x909090, N: 0x3050F8, O: 0xFF0D0D,
  F: 0x90E050, Ne: 0xB3E3F5, Na: 0xAB5CF2, Mg: 0x8AFF00,
  Al: 0xBFA6A6, Si: 0xF0C8A0, P: 0xFF8000, S: 0xFFFF30,
  Cl: 0x1FF01F, K: 0x8F40D4, Ca: 0x3DFF00, Ti: 0xBFC2C7,
  Cr: 0x8A99C7, Mn: 0x9C7AC7, Fe: 0xE06633, Co: 0xF090A0,
  Ni: 0x50D050, Cu: 0xC88033, Zn: 0x7D80B0, Se: 0xFFA100,
  Br: 0xA62929, Ag: 0xC0C0C0, Sn: 0x668080, Bi: 0x9E4FB5,
  U: 0x0099FF, Pu: 0x006BFF, Th: 0x429EB0,
};

const CPK_RADII = {
  H: 0.31, C: 0.77, N: 0.75, O: 0.73, F: 0.71,
  P: 1.06, S: 1.02, Cl: 0.99, Fe: 1.24, Cu: 1.28,
  Al: 1.43, Na: 1.86, Ni: 1.25, Zn: 1.33, Ti: 1.47,
  U: 1.56, Pu: 1.51, Th: 1.65,
};

function atomColor(sym)  { return CPK_COLORS[sym] ?? 0xAAAAAA; }
function atomRadius(sym) { return ((CPK_RADII[sym] ?? 1.0) * 0.32); }

/* Fractional → Cartesian using standard crystallographic matrix */
function fracToCart(fx, fy, fz, cell) {
  const { a = 5, b = 5, c = 5, alpha = 90, beta = 90, gamma = 90 } = cell || {};
  const toR  = d => d * Math.PI / 180;
  const ca = Math.cos(toR(alpha));
  const cb = Math.cos(toR(beta));
  const cg = Math.cos(toR(gamma));
  const sg = Math.sin(toR(gamma));
  const vol = Math.sqrt(Math.max(0, 1 - ca*ca - cb*cb - cg*cg + 2*ca*cb*cg));
  return [
    a*fx + b*cg*fy + c*cb*fz,
    b*sg*fy + c*(ca - cb*cg)/sg*fz,
    c*vol/sg*fz,
  ];
}

/* Parse element symbol from label like "U1", "Fe2a", "Cl" */
function parseSymbol(label) {
  const m = (label || "").match(/^([A-Z][a-z]?)/);
  return m ? m[1] : label;
}

/* Build unit-cell edges (8 vertices of parallelepiped) */
function buildCellEdges(cell) {
  const { a = 5, b = 5, c = 5 } = cell || {};
  const corners = [
    [0,0,0],[1,0,0],[0,1,0],[1,1,0],
    [0,0,1],[1,0,1],[0,1,1],[1,1,1],
  ].map(([fx,fy,fz]) => fracToCart(fx*a/a||fx, fy*b/b||fy, fz*c/c||fz, cell));

  const edgeIdx = [
    [0,1],[2,3],[4,5],[6,7],
    [0,2],[1,3],[4,6],[5,7],
    [0,4],[1,5],[2,6],[3,7],
  ];
  const pts = [];
  edgeIdx.forEach(([i,j]) => {
    pts.push(...corners[i], ...corners[j]);
  });
  return pts;
}

/* ── Main Component ───────────────────────────────────────────── */

const LatticeViewer3D = ({ sites = [], cell = null, coordType = "frac", onReady, onZoomChange }) => {
  const { useRef, useEffect, useState } = React;

  const mountRef = useRef(null);
  const axisRef  = useRef(null); // separate canvas for axis indicator
  const stateRef = useRef({});
  const [tooltip, setTooltip] = useState(null);

  useEffect(() => {
    if (!mountRef.current || !axisRef.current || typeof THREE === "undefined") return;
    const el = mountRef.current;
    const W  = el.clientWidth  || 800;
    const H  = el.clientHeight || 600;

    /* ── Main renderer ─────────────────────────────────── */
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(W, H);
    renderer.setClearColor(0x000000, 0);
    el.appendChild(renderer.domElement);

    /* ── Axis renderer — owns its own fixed canvas ─────── */
    const axisRenderer = new THREE.WebGLRenderer({
      canvas:    axisRef.current,
      antialias: true,
      alpha:     true,
    });
    axisRenderer.setPixelRatio(window.devicePixelRatio);
    axisRenderer.setSize(80, 80);
    axisRenderer.setClearColor(0x000000, 0);

    const axisScene  = new THREE.Scene();
    const axisCamera = new THREE.OrthographicCamera(-2, 2, 2, -2, 0, 10);
    axisCamera.position.set(0, 0, 5);
    axisScene.add(new THREE.AxesHelper(1.5));
    axisScene.add(new THREE.AmbientLight(0xffffff, 1));

    /* ── Main scene ────────────────────────────────────── */
    const scene  = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, W / H, 0.01, 1000);

    /* ── Lights ────────────────────────────────────────── */
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(12, 18, 10);
    scene.add(sun);
    const fill = new THREE.DirectionalLight(0x99aaff, 0.35);
    fill.position.set(-10, -8, -10);
    scene.add(fill);

    /* ── OrbitControls ─────────────────────────────────── */
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.minDistance   = 1;
    controls.maxDistance   = 200;
    controls.rotateSpeed   = 0.7;
    controls.zoomSpeed     = 1.2;

    /* ── Unit cell wireframe (skip for cart without cell) ── */
    if (coordType !== "cart" || cell) {
      const cellPts = buildCellEdges(cell);
      const cellGeo = new THREE.BufferGeometry();
      cellGeo.setAttribute("position", new THREE.Float32BufferAttribute(cellPts, 3));
      const cellMat = new THREE.LineBasicMaterial({ color: 0x4466cc, opacity: 0.55, transparent: true });
      scene.add(new THREE.LineSegments(cellGeo, cellMat));
    }

    /* ── Atoms ─────────────────────────────────────────── */
    const meshes = [];
    const sphereCache = {};

    sites.forEach(site => {
      const sym = site.symbol || parseSymbol(site.label);
      const r   = atomRadius(sym);
      if (!sphereCache[sym]) {
        sphereCache[sym] = new THREE.SphereGeometry(r, 28, 18);
      }
      const mat  = new THREE.MeshPhongMaterial({
        color:     atomColor(sym),
        shininess: 90,
        specular:  0x333333,
      });
      const mesh = new THREE.Mesh(sphereCache[sym], mat);
      const fx = parseFloat(site.x) || 0;
      const fy = parseFloat(site.y) || 0;
      const fz = parseFloat(site.z) || 0;
      const [cx, cy, cz] = coordType === "cart"
        ? [fx, fy, fz]
        : fracToCart(fx, fy, fz, cell);
      mesh.position.set(cx, cy, cz);
      mesh.userData = { label: site.label, symbol: sym, x: site.x, y: site.y, z: site.z, cx, cy, cz };
      scene.add(mesh);
      meshes.push(mesh);
    });

    /* ── Bonds (distance-based) ─────────────────────────── */
    if (sites.length > 1 && sites.length <= 300) {
      const positions = meshes.map(m => m.position);
      const bondMat = new THREE.LineBasicMaterial({ color: 0x888899, opacity: 0.4, transparent: true });
      for (let i = 0; i < positions.length; i++) {
        for (let j = i + 1; j < positions.length; j++) {
          const dist = positions[i].distanceTo(positions[j]);
          const ri = atomRadius(meshes[i].userData.symbol);
          const rj = atomRadius(meshes[j].userData.symbol);
          if (dist < (ri + rj) * 3.5 && dist > 0.3) {
            const pts = [positions[i].clone(), positions[j].clone()];
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            scene.add(new THREE.Line(geo, bondMat));
          }
        }
      }
    }

    /* ── Camera / target placement — start farther away ─── */
    if (meshes.length > 0) {
      const box = new THREE.Box3();
      meshes.forEach(m => box.expandByObject(m));

      // Also expand by cell corners so camera fits the whole unit cell,
      // not just the atom cluster (handles sparse / 2-atom structures)
      if (cell) {
        [[0,0,0],[1,0,0],[0,1,0],[1,1,0],[0,0,1],[1,0,1],[0,1,1],[1,1,1]].forEach(([fx,fy,fz]) => {
          const [cx,cy,cz] = fracToCart(fx, fy, fz, cell);
          box.expandByPoint(new THREE.Vector3(cx, cy, cz));
        });
      }

      const center = new THREE.Vector3();
      box.getCenter(center);
      const size = Math.max(box.getSize(new THREE.Vector3()).length(), 6);
      controls.target.copy(center);
      camera.position
        .copy(center)
        .addScaledVector(new THREE.Vector3(1, 0.7, 1.5).normalize(), size * 2.8);
      controls.update();
    } else {
      camera.position.set(8, 6, 12);
    }

    /* ── Raycaster (hover) ──────────────────────────────── */
    const raycaster = new THREE.Raycaster();
    const mouse     = new THREE.Vector2();

    const onMouseMove = (e) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width)  *  2 - 1;
      mouse.y = -((e.clientY - rect.top)  / rect.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const hits = raycaster.intersectObjects(meshes);
      if (hits.length > 0) {
        const ud = hits[0].object.userData;
        setTooltip({ ...ud, px: e.clientX - rect.left, py: e.clientY - rect.top });
        renderer.domElement.style.cursor = "crosshair";
        meshes.forEach(m => {
          m.material.emissive.setHex(m === hits[0].object ? 0x334466 : 0x000000);
        });
      } else {
        setTooltip(null);
        renderer.domElement.style.cursor = "";
        meshes.forEach(m => m.material.emissive.setHex(0x000000));
      }
    };
    renderer.domElement.addEventListener("mousemove", onMouseMove);

    /* ── Reset camera API ──────────────────────────────── */
    // Save state right after fitCamera so resetCamera can restore it
    const initialCamPos = camera.position.clone();
    const initialTarget = controls.target.clone();

    const resetCamera = () => {
      camera.position.copy(initialCamPos);
      controls.target.copy(initialTarget);
      controls.update();
    };

    /* ── Zoom API ───────────────────────────────────────── */
    const initialDist = camera.position.distanceTo(controls.target);

    const getZoomPct = () => {
      const d = camera.position.distanceTo(controls.target);
      return d > 0 ? Math.round((initialDist / d) * 100) : 100;
    };

    const zoomIn = () => {
      const offset = camera.position.clone().sub(controls.target);
      const next   = Math.max(offset.length() * 0.8, controls.minDistance);
      camera.position.copy(controls.target).addScaledVector(offset.normalize(), next);
      controls.update();
    };

    const zoomOut = () => {
      const offset = camera.position.clone().sub(controls.target);
      const next   = Math.min(offset.length() * 1.25, controls.maxDistance);
      camera.position.copy(controls.target).addScaledVector(offset.normalize(), next);
      controls.update();
    };

    /* ── Screenshot API ─────────────────────────────────── */
    const takeScreenshot = () => {
      renderer.render(scene, camera);
      return renderer.domElement.toDataURL("image/png");
    };
    if (onReady) onReady({ screenshot: takeScreenshot, zoomIn, zoomOut, resetCamera });

    /* ── Resize ─────────────────────────────────────────── */
    const onResize = () => {
      const W2 = el.clientWidth  || 800;
      const H2 = el.clientHeight || 600;
      renderer.setSize(W2, H2);
      camera.aspect = W2 / H2;
      camera.updateProjectionMatrix();
      // axis canvas stays 80×80 — no resize needed
    };
    const ro = new ResizeObserver(onResize);
    ro.observe(el);

    /* ── Animate ────────────────────────────────────────── */
    let raf;
    let lastPct = 100;
    const animate = () => {
      raf = requestAnimationFrame(animate);
      controls.update();

      // Main scene
      renderer.render(scene, camera);

      // Notify parent of zoom changes
      if (onZoomChange) {
        const pct = getZoomPct();
        if (pct !== lastPct) { lastPct = pct; onZoomChange(pct); }
      }

      // Axis gizmo — keep it centred on origin, mirroring main camera direction
      const gizmoDir = camera.position.clone()
        .sub(controls.target)
        .normalize()
        .multiplyScalar(5);
      axisCamera.position.copy(gizmoDir);
      axisCamera.up.copy(camera.up);
      axisCamera.lookAt(0, 0, 0);
      axisRenderer.render(axisScene, axisCamera);
    };
    animate();

    stateRef.current = { renderer, axisRenderer, scene, camera, controls, meshes };

    /* ── Cleanup ────────────────────────────────────────── */
    return () => {
      cancelAnimationFrame(raf);
      renderer.domElement.removeEventListener("mousemove", onMouseMove);
      ro.disconnect();
      renderer.dispose();
      axisRenderer.dispose();
      if (renderer.domElement.parentNode === el) {
        el.removeChild(renderer.domElement);
      }
    };
  }, [sites, cell, coordType]);

  return (
    <div ref={mountRef} style={{ position: "absolute", inset: 0 }}>
      {/* Axis indicator — pinned to bottom-left via CSS, never moves */}
      <div style={{
        position:       "absolute",
        left:           12,
        bottom:         52,   /* above the X/Y/Z text labels */
        width:          80,
        height:         80,
        zIndex:         6,
        pointerEvents:  "none",
        borderRadius:   8,
        overflow:       "hidden",
        background:     "rgba(8,10,18,0.45)",
        backdropFilter: "blur(8px)",
        border:         "1px solid rgba(255,255,255,0.07)",
      }}>
        <canvas ref={axisRef} />
      </div>

      {tooltip && <AtomTooltip data={tooltip} />}
    </div>
  );
};

/* ── Atom Tooltip ─────────────────────────────────────────────── */
const AtomTooltip = ({ data }) => (
  <div style={{
    position:       "absolute",
    left:           data.px + 16,
    top:            data.py - 14,
    background:     "rgba(10,12,18,0.92)",
    backdropFilter: "blur(12px)",
    border:         "1px solid rgba(255,255,255,0.10)",
    borderRadius:   8,
    padding:        "10px 14px",
    pointerEvents:  "none",
    fontFamily:     "var(--font-mono, monospace)",
    fontSize:       12,
    color:          "rgba(232,236,248,0.95)",
    zIndex:         20,
    minWidth:       170,
    lineHeight:     1.9,
    boxShadow:      "0 4px 24px rgba(0,0,0,0.45)",
  }}>
    <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 5, letterSpacing: ".02em" }}>
      {data.label}&nbsp;
      <span style={{ color: "#5C9BFF", fontWeight: 400 }}>· {data.symbol}</span>
    </div>
    <div style={{ color: "rgba(180,190,220,0.7)", fontSize: 11, fontVariantNumeric: "tabular-nums" }}>
      <span style={{ color: "#FF6B6B" }}>x</span> = {parseFloat(data.x).toFixed(5)}<br />
      <span style={{ color: "#6BFF9E" }}>y</span> = {parseFloat(data.y).toFixed(5)}<br />
      <span style={{ color: "#6B9EFF" }}>z</span> = {parseFloat(data.z).toFixed(5)}
    </div>
  </div>
);

Object.assign(window, { LatticeViewer3D, AtomTooltip, parseSymbol, fracToCart });
