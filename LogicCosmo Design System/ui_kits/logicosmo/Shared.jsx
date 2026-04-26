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
  const navSharedStyles = {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    padding: '0 32px', height: 64, position: 'fixed', top: 0, left: 0, right: 0, zIndex: 300,
    backdropFilter: 'blur(14px)',
    transition: 'background 300ms ease',
  };
  const lightStyle = { background: 'rgba(250,247,242,0.92)', borderBottom: '1px solid #EAE2D5' };
  const darkStyle = { background: 'rgba(15,18,53,0.90)', borderBottom: '1px solid rgba(255,255,255,0.08)' };

  return (
    <nav style={{ ...navSharedStyles, ...(dark ? darkStyle : lightStyle) }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <LC_MARK />
        <span style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 20, fontWeight: 500, color: dark ? '#FAF7F2' : '#1B1F4A' }}>
          Logic<span style={{ fontWeight: 300, color: '#C8922A' }}>Cosmo</span>
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 28 }}>
        {['How It Works', 'Readings', 'FAQ'].map(l => (
          <a key={l} href="#" style={{ fontSize: 14, fontWeight: 500, color: dark ? 'rgba(250,247,242,0.75)' : '#3A3D5C', textDecoration: 'none', fontFamily: "'DM Sans', sans-serif" }}
            onClick={e => e.preventDefault()}>{l}</a>
        ))}
        <button onClick={onCTA} style={{ background: '#C8922A', color: 'white', fontSize: 13, fontWeight: 700, padding: '9px 22px', borderRadius: 999, border: 'none', cursor: 'pointer', fontFamily: "'DM Sans', sans-serif", boxShadow: '0 4px 16px rgba(200,146,42,0.30)' }}>
          Start Your Reading
        </button>
      </div>
    </nav>
  );
};

const Footer = () => (
  <footer style={{ background: '#0A0D2A', padding: '56px 32px 32px', marginTop: 0 }}>
    <div style={{ maxWidth: 1140, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40, flexWrap: 'wrap', gap: 32 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <LC_MARK />
            <span style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 20, fontWeight: 500, color: '#FAF7F2' }}>
              Logic<span style={{ fontWeight: 300, color: '#C8922A' }}>Cosmo</span>
            </span>
          </div>
          <p style={{ fontSize: 13, color: 'rgba(250,247,242,0.45)', maxWidth: 240, lineHeight: 1.6, fontFamily: "'DM Sans', sans-serif" }}>
            Vedic astrology readings for the modern seeker. Precise, personal, plain-language.
          </p>
        </div>
        <div style={{ display: 'flex', gap: 56, flexWrap: 'wrap' }}>
          {[['Product', ['Life Map Reading', 'How It Works', 'Pricing', 'FAQ']], ['Company', ['About', 'Methodology', 'Privacy', 'Terms']]].map(([title, links]) => (
            <div key={title}>
              <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: 'rgba(250,247,242,0.35)', marginBottom: 14, fontFamily: "'DM Sans', sans-serif" }}>{title}</div>
              {links.map(l => <div key={l} style={{ fontSize: 13, color: 'rgba(250,247,242,0.55)', marginBottom: 8, fontFamily: "'DM Sans', sans-serif", cursor: 'pointer' }}>{l}</div>)}
            </div>
          ))}
        </div>
      </div>
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', paddingTop: 20, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: 'rgba(250,247,242,0.30)', fontFamily: "'DM Sans', sans-serif" }}>© 2025 LogicCosmo · All rights reserved</span>
        <span style={{ fontSize: 12, color: 'rgba(250,247,242,0.30)', fontFamily: "'DM Sans', sans-serif" }}>English · Português (BR)</span>
      </div>
    </div>
  </footer>
);

const Btn = ({ children, variant = 'primary', onClick, style = {} }) => {
  const base = { display: 'inline-flex', alignItems: 'center', gap: 6, fontFamily: "'DM Sans', sans-serif", fontWeight: 700, border: 'none', cursor: 'pointer', borderRadius: 999, transition: 'all 200ms ease', textDecoration: 'none' };
  const variants = {
    primary: { background: '#C8922A', color: 'white', fontSize: 15, padding: '14px 32px', boxShadow: '0 4px 24px rgba(200,146,42,0.30)' },
    secondary: { background: 'transparent', color: '#1B1F4A', fontSize: 15, padding: '13px 30px', border: '1.5px solid #9AA0D0' },
    ghost: { background: 'transparent', color: '#C8922A', fontSize: 14, padding: '8px 0', textDecoration: 'underline', textUnderlineOffset: 3, borderRadius: 0 },
    dark: { background: '#1B1F4A', color: 'white', fontSize: 15, padding: '14px 32px' },
    inverse: { background: 'white', color: '#1B1F4A', fontSize: 15, padding: '14px 32px', fontWeight: 700 },
  };
  return <button style={{ ...base, ...variants[variant], ...style }} onClick={onClick}>{children}</button>;
};

const Label = ({ children, inverse = false }) => (
  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: inverse ? '#F0C96A' : '#C8922A', display: 'block', marginBottom: 10 }}>{children}</span>
);

const SectionHeading = ({ label, title, subtitle, inverse = false, center = false }) => (
  <div style={{ textAlign: center ? 'center' : 'left', marginBottom: 48 }}>
    {label && <Label inverse={inverse}>{label}</Label>}
    <h2 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(2rem, 3.5vw, 2.8rem)', fontWeight: 400, lineHeight: 1.2, color: inverse ? '#FAF7F2' : '#1B1F4A', margin: '0 0 16px', textWrap: 'pretty' }}>{title}</h2>
    {subtitle && <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 17, color: inverse ? 'rgba(250,247,242,0.65)' : '#7A8C7E', lineHeight: 1.65, maxWidth: center ? 560 : 480, margin: center ? '0 auto' : 0, textWrap: 'pretty' }}>{subtitle}</p>}
  </div>
);

Object.assign(window, { Nav, Footer, Btn, Label, SectionHeading, LC_MARK });
