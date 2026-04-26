const translations = {
  en: {
    navProduct: 'Reading', navHow: 'How it works', navFaq: 'FAQ', navAccount: 'Account', navBegin: 'Begin reading',
    landingEyebrow: 'LogicCosmo', landingTitle: 'Your Vedic life map, explained clearly.', landingLead: 'A guided astrology reading that turns your birth data into a grounded, human-readable map of identity, timing, work, strengths, and life direction.', landingPrimary: 'Get the Life Map Reading', landingSecondary: 'See what is included',
    pillLanguage: 'English + Brazilian Portuguese', pillPrivate: 'Private account flow', pillPaid: 'Paid reading delivery',
    priceLabel: 'Launch price', launchNote: 'First 100 readings during launch campaign.',
    miniOneTitle: 'Birth chart foundation', miniOneText: 'D1/Rashi is treated as the main map, not replaced by secondary layers.', miniTwoTitle: 'Timing and direction', miniTwoText: 'Mahadasha, Antardasha, Atma Karaka, and Amatya Karaka shape the story.', miniThreeTitle: 'Human reading', miniThreeText: 'Technical Vedic terms are explained in plain language.',
    includedEyebrow: 'What you receive', includedTitle: 'Not a dashboard. A finished reading.', includedLead: 'The public product hides the expert cockpit and gives the customer a polished, structured interpretation.',
    includedOneTitle: 'Life pattern', includedOneText: 'Core identity, recurring themes, strengths, tensions, and the direction suggested by the chart.', includedTwoTitle: 'Current period', includedTwoText: 'A clear explanation of the active Mahadasha and Antardasha in practical life language.', includedThreeTitle: 'Soul and work', includedThreeText: 'Atma Karaka for life direction and Amatya Karaka for vocation, execution, and contribution.',
    processEyebrow: 'Guided flow', processTitle: 'A simple purchase path for normal customers.', processLead: 'The user should never need to understand vargas, KP, or dashboard mechanics to receive value.', stepOneTitle: 'Create account', stepOneText: 'Sign up or log in with a normal customer account.', stepTwoTitle: 'Confirm birth data', stepTwoText: 'Enter date, time, place, and reading language.', stepThreeTitle: 'Checkout', stepThreeText: 'Pay through Stripe using server-side pricing.', stepFourTitle: 'Receive reading', stepFourText: 'View the stored reading and download PDF when available.',
    productEyebrow: 'First product', productTitle: 'Life Map Reading', productLead: 'A complete Vedic astrology life map designed for people who want insight, not raw calculation tables.', productCta: 'Start birth profile',
    faqTitle: 'Beginner-safe by design', faqText: 'LogicCosmo explains terms like Rashi chart, Bhava Chalit, Mahadasha, Atma Karaka, and Amatya Karaka where they appear. The goal is specificity without jargon overload.',
    footerNote: 'LogicCosmo public product prototype. Internal astrology engine remains separate.',
    productPageTitle: 'Life Map Reading', productPageLead: 'A structured Vedic reading for identity, timing, karmic direction, work, and practical guidance.', productSectionsTitle: 'Core reading sections', orderSummary: 'Order summary', orderLanguage: 'Reading language', orderDelivery: 'Stored web reading + future PDF', orderButton: 'Continue to birth profile',
    birthTitle: 'Confirm birth data', birthLead: 'These details determine the calculation snapshot used for the paid reading. In production, this step saves to your secure account.', birthButton: 'Review order', prototypeNote: 'Prototype only: this form does not save data yet.',
    checkoutTitle: 'Review checkout', checkoutLead: 'Price is shown for the launch campaign. In production, the backend creates the order and Stripe Checkout session.', checkoutButton: 'Continue to order status', stripeNote: 'No live Stripe call is made in this static prototype.',
    orderTitle: 'Order status', orderLead: 'The production app will update this from Stripe webhooks. Paid orders can generate readings; unpaid orders cannot.', generateButton: 'View generated reading', statusPending: 'Order created', statusPaid: 'Paid', statusGenerated: 'Generated',
    readingTitle: 'Your Life Map Reading', readingLead: 'This sample page models the stored reading view. Production reads from stored generated content, not live recalculation.', pdfComing: 'PDF download coming next',
    readBirth: 'Birth data confirmation', readD1: 'D1 foundation', readTiming: 'Current life period', readJaimini: 'Soul and work indicators', readSummary: 'Life map summary'
  },
  'pt-BR': {
    navProduct: 'Leitura', navHow: 'Como funciona', navFaq: 'FAQ', navAccount: 'Conta', navBegin: 'Começar leitura',
    landingEyebrow: 'LogicCosmo', landingTitle: 'Seu mapa de vida védico, explicado com clareza.', landingLead: 'Uma leitura guiada que transforma seus dados de nascimento em um mapa humano e compreensível sobre identidade, timing, trabalho, forças e direção de vida.', landingPrimary: 'Comprar Mapa de Vida Védico', landingSecondary: 'Ver o que inclui',
    pillLanguage: 'Inglês + português do Brasil', pillPrivate: 'Fluxo com conta privada', pillPaid: 'Entrega de leitura paga',
    priceLabel: 'Preço de lançamento', launchNote: 'Primeiras 100 leituras da campanha de lançamento.',
    miniOneTitle: 'Base do mapa natal', miniOneText: 'D1/Rashi é tratado como o mapa principal, sem ser substituído por camadas secundárias.', miniTwoTitle: 'Tempo e direção', miniTwoText: 'Mahadasha, Antardasha, Atma Karaka e Amatya Karaka organizam a narrativa.', miniThreeTitle: 'Leitura humana', miniThreeText: 'Termos védicos técnicos são explicados em linguagem simples.',
    includedEyebrow: 'O que você recebe', includedTitle: 'Não é um painel técnico. É uma leitura finalizada.', includedLead: 'O produto público esconde o cockpit especialista e entrega uma interpretação polida e estruturada.',
    includedOneTitle: 'Padrão de vida', includedOneText: 'Identidade central, temas recorrentes, forças, tensões e a direção sugerida pelo mapa.', includedTwoTitle: 'Período atual', includedTwoText: 'Uma explicação clara do Mahadasha e Antardasha ativos em linguagem prática.', includedThreeTitle: 'Alma e trabalho', includedThreeText: 'Atma Karaka para direção de vida e Amatya Karaka para vocação, execução e contribuição.',
    processEyebrow: 'Fluxo guiado', processTitle: 'Um caminho simples de compra para clientes normais.', processLead: 'A pessoa não precisa entender vargas, KP ou painéis técnicos para receber valor.', stepOneTitle: 'Criar conta', stepOneText: 'Entrar ou criar uma conta comum de cliente.', stepTwoTitle: 'Confirmar nascimento', stepTwoText: 'Informar data, hora, local e idioma da leitura.', stepThreeTitle: 'Checkout', stepThreeText: 'Pagar pelo Stripe com preço definido pelo servidor.', stepFourTitle: 'Receber leitura', stepFourText: 'Ver a leitura armazenada e baixar PDF quando disponível.',
    productEyebrow: 'Primeiro produto', productTitle: 'Mapa de Vida Védico', productLead: 'Uma leitura védica completa para quem quer entendimento, não tabelas técnicas soltas.', productCta: 'Preencher dados de nascimento',
    faqTitle: 'Pensado para iniciantes', faqText: 'LogicCosmo explica termos como mapa Rashi, Bhava Chalit, Mahadasha, Atma Karaka e Amatya Karaka no momento certo. A meta é ser específico sem sobrecarregar com jargão.',
    footerNote: 'Protótipo do produto público LogicCosmo. O motor astrológico interno permanece separado.',
    productPageTitle: 'Mapa de Vida Védico', productPageLead: 'Uma leitura védica estruturada sobre identidade, timing, direção kármica, trabalho e orientação prática.', productSectionsTitle: 'Seções centrais da leitura', orderSummary: 'Resumo do pedido', orderLanguage: 'Idioma da leitura', orderDelivery: 'Leitura web armazenada + PDF futuro', orderButton: 'Continuar para dados de nascimento',
    birthTitle: 'Confirme seus dados de nascimento', birthLead: 'Esses dados determinam o snapshot de cálculo usado na leitura paga. Em produção, esta etapa salva na sua conta segura.', birthButton: 'Revisar pedido', prototypeNote: 'Protótipo: este formulário ainda não salva dados.',
    checkoutTitle: 'Revisar checkout', checkoutLead: 'O preço exibido é da campanha de lançamento. Em produção, o backend cria o pedido e a sessão do Stripe Checkout.', checkoutButton: 'Continuar para status do pedido', stripeNote: 'Nenhuma chamada real ao Stripe é feita neste protótipo estático.',
    orderTitle: 'Status do pedido', orderLead: 'O app de produção atualizará isto pelos webhooks do Stripe. Pedidos pagos podem gerar leituras; pedidos não pagos não podem.', generateButton: 'Ver leitura gerada', statusPending: 'Pedido criado', statusPaid: 'Pago', statusGenerated: 'Gerado',
    readingTitle: 'Seu Mapa de Vida Védico', readingLead: 'Esta página de exemplo modela a visualização da leitura armazenada. Em produção, ela lê conteúdo gerado salvo, não recalcula ao vivo.', pdfComing: 'Download em PDF em breve',
    readBirth: 'Confirmação dos dados', readD1: 'Fundação D1', readTiming: 'Período atual de vida', readJaimini: 'Indicadores de alma e trabalho', readSummary: 'Resumo do mapa de vida'
  }
};

function getInitialLocale() {
  const path = window.location.pathname.toLowerCase();
  if (path === '/en' || path.startsWith('/en/')) return 'en';
  if (path.includes('/pt-br')) return 'pt-BR';
  const saved = localStorage.getItem('lc-locale');
  if (saved && translations[saved]) return saved;
  const nav = navigator.language || '';
  if (nav.toLowerCase().startsWith('pt')) return 'pt-BR';
  return 'en';
}

function setLocale(locale) {
  const dict = translations[locale] || translations.en;
  document.documentElement.lang = locale === 'pt-BR' ? 'pt-BR' : 'en';
  document.body.dataset.locale = locale;
  localStorage.setItem('lc-locale', locale);
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const key = node.dataset.i18n;
    if (dict[key]) node.textContent = dict[key];
  });
  document.querySelectorAll('[data-locale-label]').forEach((node) => {
    node.textContent = locale === 'pt-BR' ? 'Português' : 'English';
  });
  document.querySelectorAll('[data-lang-button]').forEach((button) => {
    button.setAttribute('aria-pressed', button.dataset.langButton === locale ? 'true' : 'false');
  });
}

function wireMenu() {
  const button = document.querySelector('[data-menu-button]');
  if (!button) return;
  button.addEventListener('click', () => {
    const open = document.body.dataset.menuOpen === 'true';
    document.body.dataset.menuOpen = open ? 'false' : 'true';
    button.setAttribute('aria-expanded', open ? 'false' : 'true');
  });
}

function wireLocaleButtons() {
  document.querySelectorAll('[data-lang-button]').forEach((button) => {
    button.addEventListener('click', () => setLocale(button.dataset.langButton));
  });
}

function hydrateYear() {
  document.querySelectorAll('[data-year]').forEach((node) => {
    node.textContent = new Date().getFullYear();
  });
}

wireMenu();
wireLocaleButtons();
hydrateYear();
setLocale(getInitialLocale());
