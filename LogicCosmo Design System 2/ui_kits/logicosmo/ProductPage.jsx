// LogicCosmo — Birth Data Form + Product Page

const ProductPage = ({ onNavigate }) => {
  const includes = [
    'D1 / Rashi Chart (main birth chart)',
    'Current Mahadasha & Antardasha explained',
    'Atma Karaka — soul significator',
    'Amatya Karaka — career significator',
    'Bhava Chalit — house reality check',
    'Plain-language interpretation of every section',
    'PDF download included',
  ];
  return (
    <div style={{ background: '#FAF7F2', minHeight: '100vh', paddingTop: 64 }}>
      <div style={{ maxWidth: 1140, margin: '0 auto', padding: '64px 32px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: 64, alignItems: 'start' }}>
          {/* Left */}
          <div>
            <Label>Life Map Reading</Label>
            <h1 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(2.4rem, 4vw, 3.6rem)', fontWeight: 400, color: '#1B1F4A', lineHeight: 1.12, marginBottom: 20, textWrap: 'pretty' }}>
              Your complete Vedic astrology life map
            </h1>
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 17, color: '#5E7265', lineHeight: 1.7, marginBottom: 36, maxWidth: 520 }}>
              Based on your exact birth data, this reading covers your birth chart, planetary life periods, soul and career significators — all explained in plain language. No prior knowledge required.
            </p>

            {/* What's included */}
            <div style={{ marginBottom: 40 }}>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#7A8C7E', marginBottom: 14, fontFamily: "'DM Sans', sans-serif" }}>What's Included</div>
              {includes.map(item => (
                <div key={item} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 10 }}>
                  <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#E3F4EC', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 1 }}>
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 5l2 2 4-4" stroke="#2D7A4F" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </div>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#3A3D5C', lineHeight: 1.5 }}>{item}</span>
                </div>
              ))}
            </div>

            {/* Trust signals */}
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              {[['🔒', 'Secure checkout'], ['📄', 'PDF included'], ['✓', 'No subscription']].map(([icon, label]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ fontSize: 14 }}>{icon}</span>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E' }}>{label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right — purchase card */}
          <div style={{ background: 'white', borderRadius: 20, padding: 32, border: '1px solid #EAE2D5', boxShadow: '0 8px 32px rgba(0,0,0,0.08)', position: 'sticky', top: 84 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'white', background: '#C8922A', borderRadius: 6, padding: '3px 10px', display: 'inline-block', marginBottom: 16, fontFamily: "'DM Sans', sans-serif", letterSpacing: '0.08em', textTransform: 'uppercase' }}>Launch Price</div>
            <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 48, fontWeight: 600, color: '#1B1F4A', lineHeight: 1 }}>R$ 10,99</div>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#C8922A', marginTop: 4, marginBottom: 6 }}>62 spots remaining at this price</div>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0', marginBottom: 24, textDecoration: 'line-through' }}>Standard price: R$ 99,99</div>

            <Btn variant="primary" onClick={() => onNavigate('birth')} style={{ width: '100%', justifyContent: 'center', fontSize: 15, padding: '15px 0' }}>
              Start My Reading
            </Btn>
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0', textAlign: 'center', marginTop: 12, lineHeight: 1.5 }}>
              You'll enter your birth details on the next step
            </p>

            <div style={{ marginTop: 24, paddingTop: 24, borderTop: '1px solid #F3EFE8' }}>
              {[['Delivery', '~48 hours after purchase'], ['Format', 'Online reading + PDF'], ['Language', 'English / Português (BR)'], ['Validity', 'Yours forever, no expiry']].map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#9AA0D0' }}>{k}</span>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#3A3D5C', fontWeight: 500 }}>{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Step indicator helper
const Steps = ({ current }) => {
  const steps = ['Birth Data', 'Review', 'Payment', 'Reading'];
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0, marginBottom: 48 }}>
      {steps.map((s, i) => (
        <React.Fragment key={s}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700,
              background: i < current ? '#C8922A' : i === current ? '#1B1F4A' : '#EAE2D5',
              color: i <= current ? 'white' : '#9AA0D0' }}>
              {i < current ? '✓' : i + 1}
            </div>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: i === current ? 600 : 400, color: i === current ? '#1B1F4A' : '#9AA0D0', whiteSpace: 'nowrap' }}>{s}</span>
          </div>
          {i < steps.length - 1 && <div style={{ flex: 1, height: 1.5, background: i < current ? '#C8922A' : '#EAE2D5', margin: '0 8px', marginBottom: 20, minWidth: 32 }} />}
        </React.Fragment>
      ))}
    </div>
  );
};

const BirthDataForm = ({ onNavigate }) => {
  const [form, setForm] = React.useState({ name: '', date: '', time: '', place: '', timeKnown: true });
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const inputStyle = { fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: '#3A3D5C', background: 'white', border: '1.5px solid #EAE2D5', borderRadius: 10, padding: '12px 16px', outline: 'none', width: '100%', transition: 'border 200ms ease' };
  const labelStyle = { fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, color: '#1B1F4A', marginBottom: 6, display: 'block' };
  const hintStyle = { fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#7A8C7E', marginTop: 5, lineHeight: 1.5 };

  return (
    <div style={{ background: '#FAF7F2', minHeight: '100vh', paddingTop: 64 }}>
      <div style={{ maxWidth: 580, margin: '0 auto', padding: '56px 24px' }}>
        <Steps current={0} />
        <h2 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 32, fontWeight: 400, color: '#1B1F4A', marginBottom: 8, textAlign: 'center' }}>Your birth details</h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: '#7A8C7E', textAlign: 'center', marginBottom: 40, lineHeight: 1.6 }}>These details are used to calculate your Vedic birth chart. Accuracy — especially of birth time — improves your reading.</p>

        <div style={{ background: 'white', borderRadius: 20, padding: 32, border: '1px solid #EAE2D5', boxShadow: '0 4px 16px rgba(0,0,0,0.06)' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div>
              <label style={labelStyle}>Full Name</label>
              <input style={inputStyle} placeholder="Your name" value={form.name} onChange={e => set('name', e.target.value)} />
            </div>
            <div>
              <label style={labelStyle}>Date of Birth</label>
              <input style={{ ...inputStyle, fontFamily: "'DM Mono', monospace" }} placeholder="DD / MM / YYYY" value={form.date} onChange={e => set('date', e.target.value)} />
            </div>
            <div>
              <label style={labelStyle}>Time of Birth</label>
              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <div style={{ flex: 1 }}>
                  <input style={{ ...inputStyle, fontFamily: "'DM Mono', monospace", opacity: form.timeKnown ? 1 : 0.4 }} placeholder="HH : MM" value={form.time} onChange={e => set('time', e.target.value)} disabled={!form.timeKnown} />
                </div>
                <label style={{ display: 'flex', alignItems: 'center', gap: 8, paddingTop: 13, cursor: 'pointer', flexShrink: 0 }}>
                  <input type="checkbox" checked={!form.timeKnown} onChange={e => set('timeKnown', !e.target.checked)} />
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E' }}>I don't know</span>
                </label>
              </div>
              <p style={hintStyle}>Use the local time at your place of birth, not adjusted for time zones.</p>
            </div>
            <div>
              <label style={labelStyle}>Place of Birth</label>
              <input style={inputStyle} placeholder="City, Country" value={form.place} onChange={e => set('place', e.target.value)} />
              <p style={hintStyle}>Enter the city where you were born. We'll use its coordinates.</p>
            </div>
          </div>

          <div style={{ marginTop: 32, paddingTop: 24, borderTop: '1px solid #F3EFE8' }}>
            <div style={{ background: '#FBF5E6', border: '1px solid #F6EAC8', borderRadius: 10, padding: '12px 16px', marginBottom: 24 }}>
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#8A5A14', lineHeight: 1.5 }}>
                <strong>Why we need this:</strong> Your Vedic chart depends on your exact birth time and location. A 4-minute difference in birth time can shift your Ascendant.
              </p>
            </div>
            <Btn variant="primary" onClick={() => onNavigate('checkout')} style={{ width: '100%', justifyContent: 'center', fontSize: 15, padding: '15px 0' }}>
              Continue to Review →
            </Btn>
          </div>
        </div>
      </div>
    </div>
  );
};

Object.assign(window, { ProductPage, BirthDataForm, Steps });
