// LogicCosmo UI Kit — Shared Components
// Nav, Footer, Button, Badge, Card primitives

const LC_MARK = () => (
  <svg width="32" height="32" viewBox="0 0 48 48" fill="none">
    <ellipse cx="24" cy="24" rx="20" ry="20" stroke="#C8922A" strokeWidth="1.5" fill="none" opacity="0.45"/>
    <ellipse cx="24" cy="24" rx="20" ry="8" stroke="#C8922A" strokeWidth="1.5" fill="none" transform="rotate(-20 24 24)"/>
    <circle cx="24" cy="24" r="4" fill="#C8922A"/>
    <circle cx="24" cy="24" r="1.8" fill="#F0C96A"/>
    <circle cx="41" cy="18" r="2.5" fill="#C8922A" opacity="0.85"/>
  </svg>
);

const Nav = ({ dark = false, onCTA }) => {
  const base = {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 32px', height: 56, position: 'fixed', top: 0, left: 0, right: 0, zIndex: 300,
  };
  const lightStyle = { background: 'rgba(250,250,248,0.96)', borderBottom: '1px solid #E2DED8', backdropFilter: 'blur(12px)' };
  const darkStyle  = { background: 'rgba(14,14,14,0.95)',   borderBottom: '1px solid rgba(255,255,255,0.07)', backdropFilter: 'blur(12px)' };

  const markStroke = dark ? 'rgba(250,250,248,0.55)' : '#0E0E0E';
  const wordColor  = dark ? '#FAFAF8' : '#0E0E0E';
  const linkColor  = dark ? 'rgba(250,250,248,0.55)' : '#3A3A3A';
  const ctaBg      = dark ? '#B8622A' : '#0E0E0E';

  return (
    <nav style={{ ...base, ...(dark ? darkStyle : lightStyle) }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
          <circle cx="14" cy="14" r="12" stroke={markStroke} strokeWidth="1.25"/>
          <circle cx="14" cy="14" r="2.5" fill="#B8622A"/>
          <line x1="14" y1="2" x2="14" y2="26" stroke={markStroke} strokeWidth="0.75" opacity="0.2"/>
          <line x1="2" y1="14" x2="26" y2="14" stroke={markStroke} strokeWidth="0.75" opacity="0.2"/>
        </svg>
        <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 16, fontWeight: 700, letterSpacing: '-0.04em', color: wordColor }}>
          Logicosmo
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
        {['How It Works', 'Readings', 'FAQ'].map(l => (
          <a key={l} href="#" style={{ fontSize: 13, fontWeight: 500, color: linkColor, textDecoration: 'none', fontFamily: "'Instrument Sans', sans-serif", letterSpacing: '-0.01em' }}
            onClick={e => e.preventDefault()}>{l}</a>
        ))}
        <button onClick={onCTA} style={{ background: ctaBg, color: '#FAFAF8', fontSize: 13, fontWeight: 600, padding: '8px 18px', borderRadius: 4, border: 'none', cursor: 'pointer', fontFamily: "'Instrument Sans', sans-serif", letterSpacing: '-0.01em' }}>
          Start Your Reading
        </button>
      </div>
    </nav>
  );
};

const Footer = () => (
  <footer style={{ background: '#0E0E0E', padding: '56px 32px 32px' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 48, flexWrap: 'wrap', gap: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 14 }}>
            <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
              <circle cx="14" cy="14" r="12" stroke="rgba(250,250,248,0.45)" strokeWidth="1.25"/>
              <circle cx="14" cy="14" r="2.5" fill="#B8622A"/>
              <line x1="14" y1="2" x2="14" y2="26" stroke="rgba(250,250,248,0.45)" strokeWidth="0.75" opacity="0.3"/>
              <line x1="2" y1="14" x2="26" y2="14" stroke="rgba(250,250,248,0.45)" strokeWidth="0.75" opacity="0.3"/>
            </svg>
            <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 16, fontWeight: 700, letterSpacing: '-0.04em', color: '#FAFAF8' }}>Logicosmo</span>
          </div>
          <p style={{ fontSize: 13, color: 'rgba(250,250,248,0.35)', maxWidth: 220, lineHeight: 1.65, fontFamily: "'Instrument Sans', sans-serif" }}>
            Life path readings for people who want to understand themselves.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 56, flexWrap: 'wrap' }}>
          {[['Product', ['Life Path Reading', 'How It Works', 'Pricing', 'FAQ']], ['Company', ['About', 'Methodology', 'Privacy', 'Terms']]].map(([title, links]) => (
            <div key={title}>
              <div style={{ fontSize: 10, fontWeight: 600, letterSpacing: '0.10em', textTransform: 'uppercase', color: 'rgba(250,250,248,0.25)', marginBottom: 14, fontFamily: "'Instrument Sans', sans-serif" }}>{title}</div>
              {links.map(l => <div key={l} style={{ fontSize: 13, color: 'rgba(250,250,248,0.45)', marginBottom: 10, fontFamily: "'Instrument Sans', sans-serif", cursor: 'pointer', letterSpacing: '-0.01em' }}>{l}</div>)}
            </div>
          ))}
        </div>
      </div>
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: 'rgba(250,250,248,0.20)', fontFamily: "'Instrument Sans', sans-serif" }}>© 2026 Logicosmo</span>
        <span style={{ fontSize: 12, color: 'rgba(250,250,248,0.20)', fontFamily: "'Instrument Sans', sans-serif" }}>EN · PT</span>
      </div>
    </div>
  </footer>
);

const Btn = ({ children, variant = 'primary', onClick, style = {} }) => {
  const base = { display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: "'Instrument Sans', sans-serif", fontWeight: 600, letterSpacing: '-0.01em', border: 'none', cursor: 'pointer', borderRadius: 4, transition: 'all 150ms ease', textDecoration: 'none' };
  const variants = {
    primary:  { background: '#0E0E0E', color: '#FAFAF8', fontSize: 14, padding: '12px 24px' },
    copper:   { background: '#B8622A', color: '#FAFAF8', fontSize: 14, padding: '12px 24px' },
    secondary:{ background: 'transparent', color: '#0E0E0E', fontSize: 14, padding: '11px 22px', border: '1.5px solid #0E0E0E' },
    ghost:    { background: 'transparent', color: '#5C5958', fontSize: 13, padding: '0', textDecoration: 'underline', textUnderlineOffset: 4, textDecorationColor: '#C8C4BC', borderRadius: 0 },
    inverse:  { background: '#FAFAF8', color: '#0E0E0E', fontSize: 14, padding: '12px 24px', fontWeight: 700 },
  };
  return <button style={{ ...base, ...variants[variant], ...style }} onClick={onClick}>{children}</button>;
};

const Label = ({ children, inverse = false }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
    <div style={{ width: 24, height: 1.5, background: inverse ? '#B8622A' : '#B8622A' }} />
    <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 11, fontWeight: 600, letterSpacing: '0.10em', textTransform: 'uppercase', color: inverse ? '#B8622A' : '#B8622A' }}>{children}</span>
  </div>
);

const SectionHeading = ({ label, title, subtitle, inverse = false, center = false }) => (
  <div style={{ textAlign: center ? 'center' : 'left', marginBottom: 48 }}>
    {label && <Label inverse={inverse}>{label}</Label>}
    <h2 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 'clamp(1.6rem, 2.8vw, 2.2rem)', fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.03em', color: inverse ? '#FAFAF8' : '#0E0E0E', margin: '0 0 14px', textWrap: 'pretty' }}>{title}</h2>
    {subtitle && <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 16, color: inverse ? 'rgba(250,250,248,0.55)' : '#5C5958', lineHeight: 1.65, maxWidth: center ? 520 : 460, margin: center ? '0 auto' : 0, textWrap: 'pretty' }}>{subtitle}</p>}
  </div>
);

Object.assign(window, { Nav, Footer, Btn, Label, SectionHeading, LC_MARK });
