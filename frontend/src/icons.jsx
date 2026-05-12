/* ============================================================
   CRIS — Icons (Lucide-style, stroke 1.75)
   Exposed on window so all Babel scripts can use them.
   ============================================================ */
const Icon = ({ d, children, size = 18, className = "", strokeWidth = 1.75, viewBox = "0 0 24 24" }) =>
  React.createElement(
    "svg",
    {
      width: size, height: size, viewBox, fill: "none",
      stroke: "currentColor", strokeWidth, strokeLinecap: "round",
      strokeLinejoin: "round", className,
    },
    children || (d && React.createElement("path", { d }))
  );

const IconArrowRight = (p) => <Icon {...p}><path d="M5 12h14M13 6l6 6-6 6" /></Icon>;
const IconArrowUpRight = (p) => <Icon {...p}><path d="M7 17L17 7M8 7h9v9" /></Icon>;
const IconArrowDown = (p) => <Icon {...p}><path d="M12 5v14M5 12l7 7 7-7" /></Icon>;
const IconUpload = (p) => <Icon {...p}><path d="M12 3v12M8 7l4-4 4 4M5 21h14" /></Icon>;
const IconCheck = (p) => <Icon {...p}><path d="M5 13l4 4L19 7" /></Icon>;
const IconClose = (p) => <Icon {...p}><path d="M6 6l12 12M18 6L6 18" /></Icon>;
const IconMenu = (p) => <Icon {...p}><path d="M4 6h16M4 12h16M4 18h16" /></Icon>;
const IconGithub = (p) => (
  <Icon {...p}>
    <path d="M9 19c-4 1.5-4-2-6-2.5M15 22v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 19 5.77 5.07 5.07 0 0 0 18.91 2S17.73 1.65 15 3.48a13.38 13.38 0 0 0-7 0C5.27 1.65 4.09 2 4.09 2A5.07 5.07 0 0 0 4 5.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 8 19.13V22" />
  </Icon>
);
const IconCopy = (p) => <Icon {...p}><rect x="9" y="9" width="11" height="11" rx="2" /><path d="M5 15V5a2 2 0 0 1 2-2h10" /></Icon>;
const IconDownload = (p) => <Icon {...p}><path d="M12 3v12m0 0l-4-4m4 4l4-4M5 21h14" /></Icon>;
const IconCamera = (p) => <Icon {...p}><path d="M3 7h4l2-2h6l2 2h4v12H3z" /><circle cx="12" cy="13" r="3.5" /></Icon>;
const IconRotate = (p) => <Icon {...p}><path d="M3 12a9 9 0 1 1 3 6.7M3 21v-6h6" /></Icon>;
const IconHelp = (p) => <Icon {...p}><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 1-1 1.7v.5" /><circle cx="12" cy="17" r=".5" /></Icon>;
const IconInfo = (p) => <Icon {...p}><circle cx="12" cy="12" r="9" /><path d="M12 16v-5" /><circle cx="12" cy="8" r=".5" /></Icon>;
const IconSend = (p) => <Icon {...p}><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" /></Icon>;
const IconSparkles = (p) => <Icon {...p}><path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6z" /><path d="M19 14v3M21 15.5h-3M5 5v2M6 6H4" /></Icon>;
const IconMail = (p) => <Icon {...p}><rect x="3" y="5" width="18" height="14" rx="2" /><path d="M3 7l9 6 9-6" /></Icon>;
const IconBook = (p) => <Icon {...p}><path d="M4 4h12a3 3 0 0 1 3 3v13H7a3 3 0 0 1-3-3z" /><path d="M19 17H7a3 3 0 0 0-3 3" /></Icon>;
const IconCube = (p) => <Icon {...p}><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z" /><path d="M4 7.5L12 12l8-4.5M12 12v9" /></Icon>;
const IconAtom = (p) => <Icon {...p}><circle cx="12" cy="12" r="2" /><path d="M3.5 12a8.5 8.5 0 0 1 17 0 8.5 8.5 0 0 1-17 0z" transform="rotate(45 12 12)" /><path d="M3.5 12a8.5 8.5 0 0 1 17 0 8.5 8.5 0 0 1-17 0z" transform="rotate(-45 12 12)" /></Icon>;
const IconPlay = (p) => <Icon {...p}><polygon points="6 4 20 12 6 20" fill="currentColor" stroke="none" /></Icon>;
const IconChart = (p) => <Icon {...p}><path d="M3 20V5M3 20h17" /><path d="M7 16l3-5 3 3 5-8" /></Icon>;
const IconLayers = (p) => <Icon {...p}><path d="M12 3l9 5-9 5-9-5z" /><path d="M3 13l9 5 9-5M3 18l9 5 9-5" /></Icon>;
const IconPlus = (p) => <Icon {...p}><path d="M12 5v14M5 12h14" /></Icon>;
const IconMinus = (p) => <Icon {...p}><path d="M5 12h14" /></Icon>;

Object.assign(window, {
  Icon, IconArrowRight, IconArrowUpRight, IconArrowDown, IconUpload, IconCheck,
  IconClose, IconMenu, IconGithub, IconCopy, IconDownload, IconCamera, IconRotate,
  IconHelp, IconInfo, IconSend, IconSparkles, IconMail, IconBook, IconCube, IconAtom,
  IconPlay, IconChart, IconLayers, IconPlus, IconMinus,
});
