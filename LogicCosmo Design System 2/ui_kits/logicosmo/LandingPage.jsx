// LogicCosmo — Landing Page (v3: Instrument Sans, ink/paper/copper)

const HeroSection = ({ onStart }) => (
  <section style={{ background: '#FAFAF8', minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: 56, borderBottom: '1px solid #E2DED8' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '72px 32px', width: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 64, alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 24, height: 1.5, background: '#B8622A' }} />
            <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 11, fontWeight: 600, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#B8622A' }}>Life Path Reading</span>
          </div>
          <h1 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 'clamp(1.9rem, 3.2vw, 2.8rem)', fontWeight: 700, lineHeight: 1.08, letterSpacing: '-0.035em', color: '#0E0E0E', margin: '0 0 20px', textWrap: 'pretty' }}>
            Your complete Vedic<br />astrology reading,<br />
            <span style={{ color: '#8A8785', fontWeight: 400 }}>in plain language.</span>
          </h1>
          <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 15, color: '#5C5958', lineHeight: 1.75, marginBottom: 32, maxWidth: 420, textWrap: 'pretty' }}>
            Based on your birth date, time, and place — covers your chart, planetary periods, and key life themes. No prior knowledge required.
          </p>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <button onClick={onStart} style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 14, fontWeight: 600, letterSpacing: '-0.01em', background: '#0E0E0E', color: '#FAFAF8', padding: '12px 24px', borderRadius: 4, border: 'none', cursor: 'pointer' }}>Start Your Reading</button>
            <button onClick={onStart} style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, fontWeight: 500, background: 'transparent', color: '#5C5958', border: 'none', cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: 4, textDecorationColor: '#C8C4BC' }}>See what's included →</button>
          </div>
          <div style={{ display: 'flex', gap: 32, marginTop: 36, paddingTop: 28, borderTop: '1px solid #E2DED8' }}>
            {[['R$ 10,99','Launch price'],['~48h','Delivery'],['PDF','Included']].map(([val,desc]) => (
              <div key={val}>
                <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 17, fontWeight: 700, color: '#0E0E0E', letterSpacing: '-0.03em', lineHeight: 1 }}>{val}</div>
                <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 10, color: '#B2B0AC', letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: 4 }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Document preview */}
        <div style={{ background: 'white', borderRadius: 4, border: '1px solid #E2DED8', overflow: 'hidden', boxShadow: '0 8px 32px rgba(0,0,0,0.07)' }}>
          <div style={{ background: '#0E0E0E', padding: '20px 22px' }}>
            <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 10, fontWeight: 600, letterSpacing: '0.10em', textTransform: 'uppercase', color: 'rgba(250,250,248,0.30)', marginBottom: 10 }}>Life Path Reading</div>
            <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 17, fontWeight: 700, letterSpacing: '-0.03em', color: '#FAFAF8', marginBottom: 14 }}>Priya Sharma</div>
            <div style={{ display: 'flex', gap: 16 }}>
              {[['12 Aug 1990','Date'],['14:35','Time'],['Mumbai','Place']].map(([v,l]) => (
                <div key={l}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: '#FAFAF8', lineHeight: 1 }}>{v}</div>
                  <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 9, color: 'rgba(250,250,248,0.28)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 3 }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
          <div style={{ padding: '16px 22px 20px', display: 'flex', flexDirection: 'column' }}>
            {[
              ['01','Birth Chart (D1)','Scorpio rising · Cancer sun'],
              ['02','Planetary Period','Saturn Mahadasha · 2021–2040'],
              ['03','Soul Significator','Jupiter'],
              ['04','Career Significator','Mercury'],
              ['05','House Chart','Bhava Chalit adjustments'],
              ['06','Life Arc Summary','Full written interpretation'],
            ].map(([num,title,sub],i,arr) => (
              <div key={num} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '10px 0', borderBottom: i < arr.length-1 ? '1px solid #F0EDE8' : 'none' }}>
                <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: '#C8C4BC', minWidth: 18 }}>{num}</span>
                <div>
                  <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 12, fontWeight: 600, color: '#0E0E0E', letterSpacing: '-0.01em' }}>{title}</div>
                  <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 11, color: '#8A8785', marginTop: 1 }}>{sub}</div>
                </div>
              </div>
            ))}
            <button onClick={onStart} style={{ marginTop: 14, background: '#B8622A', color: '#FAFAF8', border: 'none', borderRadius: 4, padding: '10px 0', width: '100%', fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, fontWeight: 600, letterSpacing: '-0.01em', cursor: 'pointer' }}>
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
);

const WhatYouReceive = () => {
  const items = [
    { num: '01', title: 'Birth Chart', body: 'Your D1 / Rashi Chart in the sidereal Vedic zodiac — actual star positions, not the Western seasonal system.' },
    { num: '02', title: 'Planetary Period', body: 'Your current Mahadasha and Antardasha — what they mean, how long they last, what to expect.' },
    { num: '03', title: 'Soul Significator', body: 'Your Atma Karaka — the planet indicating your deepest life purpose — identified and interpreted.' },
    { num: '04', title: 'Career Significator', body: 'Your Amatya Karaka — natural work path — and how it shows up in your chart.' },
    { num: '05', title: 'House Reality Check', body: 'The Bhava Chalit chart adjusts positions to reflect how energy actually plays out in lived experience.' },
    { num: '06', title: 'PDF Document', body: 'A clean formatted reading you can return to, share, or print. No expiry, no subscription.' },
  ];
  return (
    <section style={{ background: 'white', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: 64, alignItems: 'start' }}>
          <div>
            <SectionHeading label="What You Receive" title="Six sections. One complete reading." />
            <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 14, color: '#5C5958', lineHeight: 1.7 }}>Every section written so someone with no background in Vedic astrology can follow it.</p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: '#E2DED8', borderRadius: 4, overflow: 'hidden' }}>
            {items.map(({ num, title, body }) => (
              <div key={num} style={{ background: '#FAFAF8', padding: 24 }}>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: '#C8C4BC', lineHeight: 1, marginBottom: 10 }}>{num}</div>
                <h3 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, fontWeight: 700, color: '#0E0E0E', marginBottom: 6, letterSpacing: '-0.01em' }}>{title}</h3>
                <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 12, color: '#5C5958', lineHeight: 1.65 }}>{body}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const HowItWorks = () => {
  const steps = [
    { n: 1, title: 'Enter your birth data', body: 'Date, time, and place of birth. The more precise the time, the more accurate the reading.' },
    { n: 2, title: 'We calculate your chart', body: 'Using the sidereal zodiac and Lahiri ayanamsa — the traditional Vedic method, not Western tropical.' },
    { n: 3, title: 'Your reading is written', body: 'All six sections generated from your chart data, typically within 48 hours.' },
    { n: 4, title: 'Read and download', body: 'Access your reading at any time. Download as PDF. One-time purchase, no subscription.' },
  ];
  return (
    <section style={{ background: '#F5F2EC', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <SectionHeading label="How It Works" title="Four steps to your reading" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1, background: '#C8C4BC', borderRadius: 4, overflow: 'hidden' }}>
          {steps.map(({ n, title, body }) => (
            <div key={n} style={{ background: '#F5F2EC', padding: '28px 24px' }}>
              <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 10, color: '#B8622A', letterSpacing: '0.08em', marginBottom: 14 }}>Step {n}</div>
              <h4 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 15, fontWeight: 700, color: '#0E0E0E', marginBottom: 8, lineHeight: 1.25, letterSpacing: '-0.02em' }}>{title}</h4>
              <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, color: '#5C5958', lineHeight: 1.65 }}>{body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const WhyVedic = () => (
  <section style={{ background: '#0E0E0E', padding: '96px 32px' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 24, height: 1.5, background: '#B8622A' }} />
            <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 11, fontWeight: 600, letterSpacing: '0.10em', textTransform: 'uppercase', color: '#B8622A' }}>Why Vedic Astrology</span>
          </div>
          <h2 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 'clamp(1.6rem, 2.5vw, 2.2rem)', fontWeight: 700, lineHeight: 1.1, letterSpacing: '-0.03em', color: '#FAFAF8', marginBottom: 18, textWrap: 'pretty' }}>
            Older than Western astrology. More precise.
          </h2>
          <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 15, color: 'rgba(250,250,248,0.45)', lineHeight: 1.75, marginBottom: 36 }}>
            Vedic astrology (Jyotish) uses the sidereal zodiac — aligned to actual star positions — not the seasonal tropical zodiac used in Western sun-sign astrology.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {[
              ['Sidereal zodiac','Based on actual star positions. Your Vedic signs likely differ from your Western signs.'],
              ['Planetary periods','Your life is divided into mahadashas — planetary arcs lasting 6–20 years each.'],
              ['Divisional charts','Separate charts for career, relationships, and spirituality give layered precision.'],
            ].map(([t,b]) => (
              <div key={t} style={{ display: 'flex', gap: 16 }}>
                <div style={{ width: 1.5, flexShrink: 0, background: 'rgba(184,98,42,0.45)', alignSelf: 'stretch' }} />
                <div>
                  <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontWeight: 600, fontSize: 13, color: '#FAFAF8', marginBottom: 3, letterSpacing: '-0.01em' }}>{t}</div>
                  <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, color: 'rgba(250,250,248,0.38)', lineHeight: 1.65 }}>{b}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: '#1A1A1A', borderRadius: 4, overflow: 'hidden' }}>
          {[['5,000+','Years of tradition'],['12','Sidereal signs'],['9','Planets charted'],['120','Year life cycle'],['2,700+','Years of texts'],['27','Lunar mansions']].map(([v,l]) => (
            <div key={l} style={{ padding: '24px 20px', background: '#141414' }}>
              <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 26, fontWeight: 700, color: '#FAFAF8', lineHeight: 1, letterSpacing: '-0.03em', marginBottom: 5 }}>{v}</div>
              <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 12, color: 'rgba(250,250,248,0.25)' }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

const PricingSection = ({ onStart }) => (
  <section style={{ background: 'white', padding: '96px 32px' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
        <div>
          <SectionHeading label="Launch Pricing" title="We started low. The price goes up as spots fill." subtitle="Campaign pricing — once each tier fills, the price moves to the next level." />
          <button onClick={onStart} style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 14, fontWeight: 600, letterSpacing: '-0.01em', background: '#B8622A', color: '#FAFAF8', padding: '12px 24px', borderRadius: 4, border: 'none', cursor: 'pointer' }}>Get Your Reading — R$ 10,99</button>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: '#E2DED8', borderRadius: 4, overflow: 'hidden' }}>
          {[
            { tier: 'First 100 Readings', price: 'R$ 10,99', note: '62 spots remaining', active: true },
            { tier: 'Next 100 Readings', price: 'R$ 59,99', note: 'Available after first tier', active: false },
            { tier: 'Standard Price', price: 'R$ 99,99', note: 'After first 200 readings', active: false },
          ].map(({ tier, price, note, active }) => (
            <div key={tier} style={{ background: active ? '#FAFAF8' : 'white', padding: '20px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: active ? 1 : 0.42 }}>
              <div>
                <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 11, fontWeight: 600, color: active ? '#B8622A' : '#8A8785', marginBottom: 3 }}>{tier}</div>
                <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: '#8A8785' }}>{note}</div>
              </div>
              <div style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 22, fontWeight: 700, letterSpacing: '-0.03em', color: active ? '#0E0E0E' : '#C8C4BC' }}>{price}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

const FAQSection = () => {
  const [open, setOpen] = React.useState(0);
  const faqs = [
    ['Do I need to know Vedic astrology?', 'Not at all. The reading is written in plain language. Every term is explained the first time it appears.'],
    ['How accurate is the birth time?', 'The more precise your birth time, the more accurate your Ascendant and house placements. Even without an exact time, the planetary positions and Mahadasha period remain meaningful.'],
    ['How is this different from Western astrology?', 'Vedic uses the sidereal zodiac (actual star positions) vs. Western tropical (seasonal). Your signs will likely differ. It also uses Mahadasha periods, which Western astrology does not.'],
    ['When will I receive my reading?', "Most readings are delivered within 48 hours. You'll receive an email and can check your account at any time."],
    ['Is there a subscription?', 'No. One-time purchase. You own your reading with no expiry.'],
    ['Can I download a PDF?', 'Yes. A formatted PDF is included with every reading.'],
  ];
  return (
    <section style={{ background: '#F5F2EC', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 80 }}>
          <SectionHeading label="FAQ" title="Common questions" />
          <div>
            {faqs.map(([q,a],i) => (
              <div key={i} style={{ borderBottom: '1px solid #E2DED8' }}>
                <button onClick={() => setOpen(open === i ? -1 : i)} style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '18px 0', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', gap: 16 }}>
                  <span style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 14, fontWeight: 600, color: '#0E0E0E', letterSpacing: '-0.01em' }}>{q}</span>
                  <span style={{ fontSize: 18, color: '#B8622A', flexShrink: 0, transform: open === i ? 'rotate(45deg)' : 'none', transition: 'transform 150ms ease', fontWeight: 300, lineHeight: 1 }}>+</span>
                </button>
                {open === i && <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 13, color: '#5C5958', lineHeight: 1.7, paddingBottom: 18 }}>{a}</p>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const CTABanner = ({ onStart }) => (
  <section style={{ background: '#0E0E0E', padding: '80px 32px' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 32 }}>
      <div style={{ maxWidth: 500 }}>
        <h2 style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 'clamp(1.5rem, 2.4vw, 2rem)', fontWeight: 700, letterSpacing: '-0.03em', color: '#FAFAF8', marginBottom: 10, lineHeight: 1.1, textWrap: 'pretty' }}>Your reading is waiting.</h2>
        <p style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 15, color: 'rgba(250,250,248,0.38)', lineHeight: 1.7 }}>Enter your birth data and receive a complete Vedic astrology reading — clear, precise, written for people new to this.</p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
        <button onClick={onStart} style={{ fontFamily: "'Instrument Sans', sans-serif", fontSize: 14, fontWeight: 600, letterSpacing: '-0.01em', background: '#B8622A', color: '#FAFAF8', padding: '12px 24px', borderRadius: 4, border: 'none', cursor: 'pointer' }}>Start Your Reading — R$ 10,99</button>
        <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 11, color: 'rgba(250,250,248,0.20)' }}>62 spots at launch price</span>
      </div>
    </div>
  </section>
);

const LandingPage = ({ onNavigate }) => (
  <div>
    <HeroSection onStart={() => onNavigate('product')} />
    <WhatYouReceive />
    <HowItWorks />
    <WhyVedic />
    <PricingSection onStart={() => onNavigate('product')} />
    <FAQSection />
    <CTABanner onStart={() => onNavigate('product')} />
    <Footer />
  </div>
);

Object.assign(window, { LandingPage });
