// LogicCosmo — Checkout + Reading View

const CheckoutPage = ({ onNavigate }) => {
  const [agreed, setAgreed] = React.useState(false);
  return (
    <div style={{ background: '#FAF7F2', minHeight: '100vh', paddingTop: 64 }}>
      <div style={{ maxWidth: 700, margin: '0 auto', padding: '56px 24px' }}>
        <Steps current={1} />
        <h2 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 32, fontWeight: 400, color: '#1B1F4A', marginBottom: 8, textAlign: 'center' }}>Review your order</h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: '#7A8C7E', textAlign: 'center', marginBottom: 40 }}>Confirm your birth data and order details before proceeding to payment.</p>

        {/* Birth data summary */}
        <div style={{ background: 'white', borderRadius: 16, padding: 28, border: '1px solid #EAE2D5', marginBottom: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#7A8C7E' }}>Birth Data</div>
            <button onClick={() => onNavigate('birth')} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#C8922A', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}>Edit</button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[['Name', 'Priya Sharma'], ['Date of Birth', '12 August 1990'], ['Time of Birth', '14:35 (local)'], ['Place of Birth', 'Mumbai, India']].map(([k, v]) => (
              <div key={k}>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#9AA0D0', marginBottom: 3 }}>{k}</div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, color: '#1B1F4A', fontWeight: 500 }}>{v}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Order summary */}
        <div style={{ background: 'white', borderRadius: 16, padding: 28, border: '1px solid #EAE2D5', marginBottom: 16, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#7A8C7E', marginBottom: 20 }}>Order Summary</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', paddingBottom: 16, marginBottom: 16, borderBottom: '1px solid #F3EFE8' }}>
            <div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 15, color: '#1B1F4A', marginBottom: 4 }}>Life Map Reading</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E' }}>Full Vedic astrology reading · PDF included</div>
            </div>
            <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 22, fontWeight: 600, color: '#1B1F4A' }}>R$ 10,99</div>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 700, fontSize: 15, color: '#1B1F4A' }}>Total</span>
            <span style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 24, fontWeight: 700, color: '#1B1F4A' }}>R$ 10,99</span>
          </div>
          <div style={{ marginTop: 8, fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#C8922A' }}>Launch price — 62 spots remaining</div>
        </div>

        {/* Payment section */}
        <div style={{ background: 'white', borderRadius: 16, padding: 28, border: '1px solid #EAE2D5', marginBottom: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
          <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#7A8C7E', marginBottom: 20 }}>Payment</div>
          <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
            {['Credit Card', 'PIX', 'Boleto'].map((m, i) => (
              <div key={m} style={{ flex: 1, border: i === 0 ? '2px solid #1B1F4A' : '1.5px solid #EAE2D5', borderRadius: 10, padding: '10px 0', textAlign: 'center', cursor: 'pointer' }}>
                <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: i === 0 ? 600 : 400, color: i === 0 ? '#1B1F4A' : '#7A8C7E' }}>{m}</span>
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <input style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, color: '#3A3D5C', background: '#FDFBF7', border: '1.5px solid #EAE2D5', borderRadius: 10, padding: '12px 16px', outline: 'none', width: '100%' }} placeholder="Card number" />
            <div style={{ display: 'flex', gap: 12 }}>
              <input style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, color: '#3A3D5C', background: '#FDFBF7', border: '1.5px solid #EAE2D5', borderRadius: 10, padding: '12px 16px', outline: 'none', flex: 1 }} placeholder="MM / YY" />
              <input style={{ fontFamily: "'DM Mono', monospace", fontSize: 14, color: '#3A3D5C', background: '#FDFBF7', border: '1.5px solid #EAE2D5', borderRadius: 10, padding: '12px 16px', outline: 'none', flex: 1 }} placeholder="CVV" />
            </div>
          </div>
        </div>

        <label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 24, cursor: 'pointer' }}>
          <input type="checkbox" checked={agreed} onChange={e => setAgreed(e.target.checked)} style={{ marginTop: 2 }} />
          <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E', lineHeight: 1.5 }}>I understand this is a one-time purchase and agree to the Terms of Service and Privacy Policy.</span>
        </label>

        <Btn variant="primary" onClick={() => onNavigate('reading')} style={{ width: '100%', justifyContent: 'center', fontSize: 16, padding: '15px 0', opacity: agreed ? 1 : 0.5 }}>
          Complete Purchase — R$ 10,99
        </Btn>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, marginTop: 14 }}>
          <svg width="12" height="14" viewBox="0 0 12 14" fill="none"><rect x="1" y="5" width="10" height="8" rx="2" stroke="#9AA0D0" strokeWidth="1.2"/><path d="M4 5V3.5a2 2 0 114 0V5" stroke="#9AA0D0" strokeWidth="1.2"/></svg>
          <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0' }}>Secure payment · SSL encrypted</span>
        </div>
      </div>
    </div>
  );
};

// ---- Reading View ----
const ReadingSection = ({ num, title, label, children }) => {
  const [open, setOpen] = React.useState(num === 1);
  return (
    <div style={{ background: 'white', borderRadius: 16, border: '1px solid #EAE2D5', overflow: 'hidden', marginBottom: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
      <button onClick={() => setOpen(!open)} style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 24px', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', gap: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 28, fontWeight: 300, color: '#EAE2D5', lineHeight: 1, flexShrink: 0, minWidth: 32 }}>{String(num).padStart(2, '0')}</div>
          <div>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#C8922A', marginBottom: 2 }}>{label}</div>
            <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 20, fontWeight: 500, color: '#1B1F4A', lineHeight: 1.2 }}>{title}</div>
          </div>
        </div>
        <div style={{ fontSize: 18, color: '#C8922A', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 200ms ease', flexShrink: 0 }}>↓</div>
      </button>
      {open && <div style={{ padding: '0 24px 24px', borderTop: '1px solid #F3EFE8' }}>{children}</div>}
    </div>
  );
};

const ReadingView = ({ onNavigate }) => {
  const bodyText = { fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: '#3A3D5C', lineHeight: 1.75 };
  const termStyle = { fontFamily: "'DM Mono', monospace", fontSize: 13, background: '#FBF5E6', color: '#8A5A14', padding: '2px 6px', borderRadius: 4, display: 'inline' };
  const highlight = { background: '#F3EFE8', borderRadius: 12, padding: '16px 20px', marginBottom: 16, marginTop: 16 };

  return (
    <div style={{ background: '#FAF7F2', minHeight: '100vh', paddingTop: 64 }}>
      {/* Reading header */}
      <div style={{ background: 'radial-gradient(ellipse at 70% 40%, #2A2E6E 0%, #0F1235 70%)', padding: '48px 32px 40px', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, opacity: 0.4 }}>
          <svg width="100%" height="100%" viewBox="0 0 1440 300" preserveAspectRatio="xMidYMid slice">
            {[[120,60,1,.5],[400,100,1.5,.3],[800,50,1,.6],[1100,90,2,.3],[1300,140,1,.5],[200,200,1,.3],[600,180,1.5,.25],[1000,160,1,.4]].map(([x,y,r,op],i)=>(
              <circle key={i} cx={x} cy={y} r={r} fill="white" opacity={op}/>
            ))}
          </svg>
        </div>
        <div style={{ maxWidth: 860, margin: '0 auto', position: 'relative', zIndex: 2 }}>
          <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#F0C96A', marginBottom: 10 }}>Life Map Reading</div>
          <h1 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(1.8rem, 3vw, 2.6rem)', fontWeight: 300, color: '#FAF7F2', marginBottom: 16, lineHeight: 1.2 }}>Priya Sharma's Life Map</h1>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            {[['12 August 1990', 'Date of Birth'], ['14:35 · Mumbai, India', 'Birth Data'], ['Saturn Mahadasha', 'Current Period']].map(([v, l]) => (
              <div key={l}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 13, color: '#FAF7F2', marginBottom: 2 }}>{v}</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, color: 'rgba(250,247,242,0.45)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{l}</div>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 24, display: 'flex', gap: 10 }}>
            <button style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, background: '#C8922A', color: 'white', border: 'none', borderRadius: 999, padding: '9px 20px', cursor: 'pointer' }}>
              Download PDF
            </button>
            <button style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, background: 'rgba(255,255,255,0.10)', color: 'rgba(250,247,242,0.75)', border: '1px solid rgba(255,255,255,0.15)', borderRadius: 999, padding: '9px 20px', cursor: 'pointer' }}>
              Share Reading
            </button>
          </div>
        </div>
      </div>

      {/* Reading content */}
      <div style={{ maxWidth: 860, margin: '0 auto', padding: '40px 24px 80px' }}>
        <ReadingSection num={1} label="Birth Chart" title="Your D1 / Rashi Chart">
          <div style={{ ...highlight, marginTop: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
              {[['Ascendant (Lagna)', 'Scorpio (Vrishchika)', 'Your rising sign — the lens through which the world sees you'], ['Sun Sign (Vedic)', 'Cancer (Karka)', 'Different from your Western sign — calculated using the sidereal zodiac'], ['Moon Sign', 'Taurus (Vrishabha)', 'Your emotional nature and inner world']].map(([k, v, desc]) => (
                <div key={k}>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, color: '#9AA0D0', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k}</div>
                  <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 17, fontWeight: 500, color: '#1B1F4A', marginBottom: 3 }}>{v}</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#7A8C7E', lineHeight: 1.5 }}>{desc}</div>
                </div>
              ))}
            </div>
          </div>
          <p style={bodyText}>Your <span style={termStyle}>Ascendant (Lagna)</span> is Scorpio — a Mars-ruled sign known for intensity, depth, and a drive to understand hidden truth. Scorpio rising often indicates a life path tied to transformation, research, or healing.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Your <span style={termStyle}>Sun</span> sits in Cancer in the 9th house, a powerful placement for spiritual inquiry and long-distance connections. The 9th house governs dharma — your higher purpose — making this a chart naturally oriented toward teaching, wisdom, and far travel.</p>
        </ReadingSection>

        <ReadingSection num={2} label="Mahadasha" title="Your Current Planetary Period">
          <div style={{ ...highlight, marginTop: 20, background: '#ECEEF7', borderLeft: '3px solid #1B1F4A' }}>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#7A8C7E', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Current Period</div>
            <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 24, fontWeight: 500, color: '#1B1F4A' }}>Saturn Mahadasha</div>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#5E7265', marginTop: 4 }}>2021 – 2040 · 19-year arc · Currently in Mercury Antardasha</div>
          </div>
          <p style={bodyText}>You are in a <span style={termStyle}>Saturn Mahadasha</span> — your major planetary life period — which began in 2021 and will last until 2040. A Mahadasha is a 6–20 year window governed by a single planet, shaping the dominant theme of that phase of your life.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Saturn's Mahadasha is a period of seriousness, discipline, and karmic accounting. It rewards sustained effort and punishes shortcuts. For a Scorpio Ascendant, Saturn rules the 3rd and 4th houses — this period often brings lessons around communication, home, and inner security.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Within this major period, you are currently in a <span style={termStyle}>Mercury Antardasha</span> (sub-period) lasting from March 2024 to December 2026. Mercury activates intellect, communication, and commerce — a useful counterbalance to Saturn's weight.</p>
        </ReadingSection>

        <ReadingSection num={3} label="Soul Significator" title="Your Atma Karaka">
          <p style={{ ...bodyText, marginTop: 20 }}>Your <span style={termStyle}>Atma Karaka</span> — the soul significator — is <strong style={{ color: '#1B1F4A' }}>Jupiter</strong>. The Atma Karaka is the planet with the highest degree in your birth chart, and in Vedic astrology it represents the deepest purpose your soul came to pursue in this lifetime.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Jupiter as Atma Karaka points to a soul oriented around wisdom, teaching, expansion, and truth. Your life's deepest fulfillment will come through learning, sharing knowledge, and growth — whether in formal education, spiritual inquiry, mentorship, or cultural exchange.</p>
        </ReadingSection>

        <ReadingSection num={4} label="Career Significator" title="Your Amatya Karaka">
          <p style={{ ...bodyText, marginTop: 20 }}>Your <span style={termStyle}>Amatya Karaka</span> — your career and work significator — is <strong style={{ color: '#1B1F4A' }}>Mercury</strong>. This planet represents the area of life where you are naturally equipped to contribute and be recognized.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Mercury as Amatya Karaka suggests a path involving communication, analysis, writing, trade, or technology. You likely thrive in environments where information flows — whether that is media, education, consulting, finance, or research.</p>
        </ReadingSection>

        <ReadingSection num={5} label="Bhava Chalit" title="Your House Reality Check">
          <p style={{ ...bodyText, marginTop: 20 }}>The <span style={termStyle}>Bhava Chalit</span> chart adjusts planetary positions to show how their energy is actually experienced in your lived reality — as opposed to the theoretical position in the D1 chart.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>In your Bhava Chalit, Venus shifts from the 12th to the 11th house. This is significant: in the D1 chart, Venus in the 12th can indicate withdrawal or isolation in relationships, but the Bhava Chalit placement in the 11th suggests Venus's actual expression is through social networks, friendships, and group aspirations.</p>
        </ReadingSection>

        <ReadingSection num={6} label="Summary" title="Your Life Arc">
          <p style={{ ...bodyText, marginTop: 20 }}>Taken together, your chart tells the story of a life built around transformation and wisdom. A Scorpio Ascendant, Jupiter Atma Karaka, and Saturn Mahadasha create an arc of depth: early years of intensity and searching, a middle phase of discipline and construction, and a later phase of recognized wisdom and influence.</p>
          <p style={{ ...bodyText, marginTop: 14 }}>Your current Saturn–Mercury period (2024–2026) is a time to do serious intellectual work: write, study, build systems, and communicate with precision. The effort you put in now will compound significantly by the time Jupiter's Antardasha begins in 2028.</p>
          <div style={{ ...highlight, marginTop: 20, background: '#0F1235', borderRadius: 14 }}>
            <p style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 20, fontWeight: 300, color: '#FAF7F2', lineHeight: 1.5, fontStyle: 'italic' }}>
              "This is not a prediction. It is a map. What you do with the terrain is yours to choose."
            </p>
          </div>
        </ReadingSection>

        <div style={{ textAlign: 'center', marginTop: 32 }}>
          <button style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 600, background: '#C8922A', color: 'white', border: 'none', borderRadius: 999, padding: '12px 28px', cursor: 'pointer', boxShadow: '0 4px 20px rgba(200,146,42,0.28)' }}>
            Download Full Reading PDF
          </button>
        </div>
      </div>
    </div>
  );
};

Object.assign(window, { CheckoutPage, ReadingView });
