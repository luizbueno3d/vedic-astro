// LogicCosmo — Landing Page (v2: editorial, grounded, premium)

const HeroSection = ({ onStart }) => (
  <section style={{ background: '#FAF7F2', minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: 64, borderBottom: '1px solid #EAE2D5' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto', padding: '80px 32px', width: '100%' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: 80, alignItems: 'center' }}>
        {/* Left: headline */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 28 }}>
            <div style={{ width: 32, height: 1.5, background: '#C8922A' }} />
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#C8922A' }}>Life Map Reading</span>
          </div>
          <h1 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(3rem, 5.5vw, 4.8rem)', fontWeight: 400, lineHeight: 1.06, color: '#1B1F4A', margin: '0 0 28px', letterSpacing: '-0.02em', textWrap: 'pretty' }}>
            A complete Vedic<br />astrology reading,<br />
            <span style={{ fontWeight: 300, color: '#5E7265', fontStyle: 'italic' }}>in plain language.</span>
          </h1>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 17, color: '#5E7265', lineHeight: 1.75, marginBottom: 40, maxWidth: 480, textWrap: 'pretty' }}>
            Based on your exact birth data — date, time, and place — your Life Map covers your birth chart, planetary periods, and key life themes, written so anyone can understand them.
          </p>
          <div style={{ display: 'flex', gap: 14, alignItems: 'center', flexWrap: 'wrap' }}>
            <Btn variant="primary" onClick={onStart} style={{ fontSize: 15, padding: '14px 34px' }}>Start Your Reading</Btn>
            <Btn variant="ghost" style={{ fontSize: 14 }}>See what's included →</Btn>
          </div>
          <div style={{ display: 'flex', gap: 32, marginTop: 44, paddingTop: 32, borderTop: '1px solid #EAE2D5', flexWrap: 'wrap' }}>
            {[['R$ 10,99', 'Launch price'], ['~48h', 'Delivery'], ['PDF', 'Included']].map(([val, desc]) => (
              <div key={val}>
                <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 22, fontWeight: 500, color: '#1B1F4A', lineHeight: 1 }}>{val}</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#9AA0D0', letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: 4 }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: document preview card */}
        <div style={{ background: 'white', borderRadius: 20, border: '1px solid #EAE2D5', boxShadow: '0 16px 48px rgba(0,0,0,0.09)', overflow: 'hidden' }}>
          {/* Card header */}
          <div style={{ background: '#1B1F4A', padding: '24px 28px' }}>
            <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: 'rgba(240,201,106,0.80)', marginBottom: 8 }}>Life Map Reading</div>
            <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 22, fontWeight: 400, color: '#FAF7F2', lineHeight: 1.2, marginBottom: 12 }}>Priya Sharma</div>
            <div style={{ display: 'flex', gap: 16 }}>
              {[['12 Aug 1990', 'Date'], ['14:35', 'Time'], ['Mumbai', 'Place']].map(([v, l]) => (
                <div key={l}>
                  <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 12, color: '#FAF7F2', lineHeight: 1 }}>{v}</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 9, color: 'rgba(250,247,242,0.40)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: 3 }}>{l}</div>
                </div>
              ))}
            </div>
          </div>
          {/* Card sections */}
          <div style={{ padding: '20px 28px', display: 'flex', flexDirection: 'column', gap: 14 }}>
            {[
              ['01', 'Birth Chart (D1)', 'Scorpio Ascendant · Cancer Sun · Taurus Moon'],
              ['02', 'Planetary Period', 'Saturn Mahadasha · 2021–2040'],
              ['03', 'Soul Significator', 'Jupiter — wisdom and expansion'],
              ['04', 'Career Significator', 'Mercury — communication and analysis'],
              ['05', 'House Chart', 'Bhava Chalit adjustments explained'],
              ['06', 'Life Arc Summary', 'Your reading in context'],
            ].map(([num, title, sub]) => (
              <div key={num} style={{ display: 'flex', alignItems: 'flex-start', gap: 14, paddingBottom: 14, borderBottom: '1px solid #F3EFE8' }}>
                <span style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 18, fontWeight: 300, color: '#DDD1BF', lineHeight: 1, minWidth: 22 }}>{num}</span>
                <div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, color: '#1B1F4A', marginBottom: 2 }}>{title}</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0' }}>{sub}</div>
                </div>
              </div>
            ))}
            <div style={{ background: '#C8922A', borderRadius: 999, padding: '10px 0', textAlign: 'center', fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 700, color: 'white', marginTop: 4 }}>
              Download PDF
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
);

const WhatYouReceive = () => {
  const items = [
    { num: '01', title: 'Birth Chart', body: 'Your D1 / Rashi Chart placed in the sidereal Vedic zodiac — the actual star positions, not the Western seasonal system.' },
    { num: '02', title: 'Planetary Period', body: 'Your current Mahadasha (major period) and Antardasha (sub-period) — what they mean, how long they last, what to expect.' },
    { num: '03', title: 'Soul Significator', body: 'Your Atma Karaka — the planet that indicates your deepest life purpose — identified and interpreted in plain terms.' },
    { num: '04', title: 'Career Significator', body: 'Your Amatya Karaka — natural work and career path — and how it shows up in your chart.' },
    { num: '05', title: 'House Reality Check', body: 'The Bhava Chalit chart adjusts planetary positions to reflect how their energy actually plays out in lived experience.' },
    { num: '06', title: 'PDF Document', body: 'A clean, formatted reading you can return to, share, or print. No expiry, no subscription.' },
  ];
  return (
    <section style={{ background: 'white', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: 64, alignItems: 'start' }}>
          <div>
            <SectionHeading label="What You Receive" title="Six sections. One complete reading." />
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#7A8C7E', lineHeight: 1.7 }}>
              Every section is written so someone with no background in Vedic astrology can follow it. Terms are explained the first time they appear.
            </p>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: '#EAE2D5', border: '1px solid #EAE2D5', borderRadius: 16, overflow: 'hidden' }}>
            {items.map(({ num, title, body }) => (
              <div key={num} style={{ background: '#FDFBF7', padding: 28 }}>
                <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 30, fontWeight: 300, color: '#EAE2D5', lineHeight: 1, marginBottom: 10 }}>{num}</div>
                <h3 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 700, color: '#1B1F4A', marginBottom: 8, letterSpacing: '-0.01em' }}>{title}</h3>
                <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E', lineHeight: 1.65 }}>{body}</p>
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
    { n: 3, title: 'Your reading is written', body: 'All six sections are generated from your chart data, typically within 48 hours.' },
    { n: 4, title: 'Read and download', body: 'Access your reading at any time. Download as PDF. One-time purchase, no subscription.' },
  ];
  return (
    <section style={{ background: '#F3EFE8', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <SectionHeading label="How It Works" title="Four steps to your reading" />
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 2, background: '#DDD1BF', borderRadius: 16, overflow: 'hidden' }}>
          {steps.map(({ n, title, body }) => (
            <div key={n} style={{ background: '#F3EFE8', padding: '32px 28px' }}>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, color: '#C8922A', letterSpacing: '0.08em', marginBottom: 16 }}>Step {n}</div>
              <h4 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 20, fontWeight: 500, color: '#1B1F4A', marginBottom: 10, lineHeight: 1.3 }}>{title}</h4>
              <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: '#7A8C7E', lineHeight: 1.65 }}>{body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const WhyVedic = () => (
  <section style={{ background: '#1B1F4A', padding: '96px 32px' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 80, alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
            <div style={{ width: 32, height: 1.5, background: '#C8922A' }} />
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#C8922A' }}>Why Vedic Astrology</span>
          </div>
          <h2 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(2rem, 3vw, 2.6rem)', fontWeight: 400, lineHeight: 1.2, color: '#FAF7F2', marginBottom: 20, textWrap: 'pretty' }}>
            Older than Western astrology. More precise.
          </h2>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: 'rgba(250,247,242,0.60)', lineHeight: 1.75, marginBottom: 36 }}>
            Vedic astrology (Jyotish) uses the sidereal zodiac — aligned to actual star positions — not the seasonal tropical zodiac used in Western sun-sign astrology. The results are measurably different.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {[
              ['Sidereal zodiac', 'Based on actual star positions. Your Vedic signs likely differ from your Western signs.'],
              ['Planetary periods', 'Unique to Vedic: your life is divided into mahadashas — planetary arcs lasting 6–20 years each.'],
              ['Divisional charts', 'Separate charts for career, relationships, and spirituality give layered precision.'],
            ].map(([t, b]) => (
              <div key={t} style={{ display: 'flex', gap: 16 }}>
                <div style={{ width: 1.5, flexShrink: 0, background: 'rgba(200,146,42,0.35)', borderRadius: 1, alignSelf: 'stretch' }} />
                <div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontWeight: 600, fontSize: 14, color: '#FAF7F2', marginBottom: 4 }}>{t}</div>
                  <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, color: 'rgba(250,247,242,0.50)', lineHeight: 1.65 }}>{b}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1, background: 'rgba(255,255,255,0.06)', borderRadius: 16, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.07)' }}>
          {[['5,000+', 'Years of tradition'], ['12', 'Sidereal signs'], ['9', 'Planets charted'], ['120', 'Year life cycle'], ['2,700+', 'Years of written texts'], ['27', 'Lunar mansions (Nakshatras)']].map(([v, l]) => (
            <div key={l} style={{ padding: '28px 24px', background: 'rgba(15,18,53,0.50)' }}>
              <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 32, fontWeight: 500, color: '#C8922A', lineHeight: 1, marginBottom: 6 }}>{v}</div>
              <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: 'rgba(250,247,242,0.40)', lineHeight: 1.4 }}>{l}</div>
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
          <SectionHeading label="Launch Pricing" title="We started low. The price goes up as spots fill." subtitle="This is a campaign pricing model — once each tier of readings is sold, the price moves to the next level." />
          <Btn variant="primary" onClick={onStart} style={{ fontSize: 15, padding: '14px 32px' }}>Get Your Reading — R$ 10,99</Btn>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: '#EAE2D5', borderRadius: 16, overflow: 'hidden', border: '1px solid #EAE2D5' }}>
          {[
            { tier: 'First 100 Readings', price: 'R$ 10,99', note: '62 spots remaining', active: true },
            { tier: 'Next 100 Readings', price: 'R$ 59,99', note: 'Available after first tier', active: false },
            { tier: 'Standard Price', price: 'R$ 99,99', note: 'After first 200 readings', active: false },
          ].map(({ tier, price, note, active }) => (
            <div key={tier} style={{ background: active ? '#FDFBF7' : 'white', padding: '24px 28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', opacity: active ? 1 : 0.55 }}>
              <div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, fontWeight: 600, color: active ? '#C8922A' : '#9AA0D0', marginBottom: 4 }}>{tier}</div>
                <div style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0' }}>{note}</div>
              </div>
              <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 28, fontWeight: 500, color: active ? '#1B1F4A' : '#C0CECC' }}>{price}</div>
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
    ['Do I need to know Vedic astrology?', 'Not at all. The reading is written in plain language. Every term is explained the first time it appears. This is designed for beginners.'],
    ['How accurate is the birth time?', 'The more precise your birth time, the more accurate your Ascendant and house placements. Even without an exact time, the planetary positions and Mahadasha period remain meaningful.'],
    ['How is this different from Western astrology?', 'Vedic astrology uses the sidereal zodiac (actual star positions) vs. the Western tropical zodiac (seasonal). Your signs will likely differ. It also uses Mahadasha periods, which Western astrology does not.'],
    ['When will I receive my reading?', 'Most readings are delivered within 48 hours. You\'ll receive an email and can check your account at any time.'],
    ['Is there a subscription?', 'No. One-time purchase. You own your reading with no expiry.'],
    ['Can I download a PDF?', 'Yes. A formatted PDF is included with every reading.'],
  ];
  return (
    <section style={{ background: '#FAF7F2', padding: '96px 32px' }}>
      <div style={{ maxWidth: 1140, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 80 }}>
          <SectionHeading label="FAQ" title="Common questions" />
          <div>
            {faqs.map(([q, a], i) => (
              <div key={i} style={{ borderBottom: '1px solid #EAE2D5' }}>
                <button onClick={() => setOpen(open === i ? -1 : i)} style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 0', background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', gap: 16 }}>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 15, fontWeight: 600, color: '#1B1F4A' }}>{q}</span>
                  <span style={{ fontSize: 16, color: '#C8922A', flexShrink: 0, transform: open === i ? 'rotate(45deg)' : 'none', transition: 'transform 200ms ease', fontWeight: 300 }}>+</span>
                </button>
                {open === i && <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#7A8C7E', lineHeight: 1.7, paddingBottom: 20 }}>{a}</p>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

const CTABanner = ({ onStart }) => (
  <section style={{ background: '#F3EFE8', padding: '80px 32px', borderTop: '1px solid #EAE2D5' }}>
    <div style={{ maxWidth: 1140, margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 32 }}>
      <div style={{ maxWidth: 560 }}>
        <h2 style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(1.8rem, 3vw, 2.8rem)', fontWeight: 400, color: '#1B1F4A', marginBottom: 12, lineHeight: 1.2, textWrap: 'pretty' }}>
          Your reading is waiting.
        </h2>
        <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 15, color: '#7A8C7E', lineHeight: 1.7 }}>
          Enter your birth data and receive a complete Vedic astrology reading — clear, precise, and written for people who are new to Vedic astrology.
        </p>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 10 }}>
        <Btn variant="primary" onClick={onStart} style={{ fontSize: 15, padding: '14px 36px' }}>Start Your Reading — R$ 10,99</Btn>
        <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#9AA0D0' }}>Launch price · 62 spots remaining</span>
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
