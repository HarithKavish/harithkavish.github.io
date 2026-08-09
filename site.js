(() => {
    const data = window.HarithSiteData;
    const h = React.createElement;
    const Fragment = React.Fragment;
    const page = document.body.dataset.page || 'home';
    const slug = document.body.dataset.slug || '';
    const rootUrl = window.location.origin || data.origin;
    const themeKey = 'harithkavish-theme';
    const productMap = new Map(data.products.map((product) => [product.slug, product]));
    let currentTheme = resolveTheme();

    function resolveTheme() {
        const stored = window.localStorage.getItem(themeKey);
        if (stored === 'dark' || stored === 'light') {
            return stored;
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function applyTheme(nextTheme, persist = true) {
        currentTheme = nextTheme === 'dark' ? 'dark' : 'light';
        document.documentElement.dataset.theme = currentTheme;
        if (persist) {
            window.localStorage.setItem(themeKey, currentTheme);
        }
        const themeButton = document.querySelector('[data-theme-toggle]');
        if (themeButton) {
            themeButton.textContent = currentTheme === 'dark' ? 'Light mode' : 'Dark mode';
            themeButton.setAttribute('aria-label', currentTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }

    function toggleTheme() {
        applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    }

    function link(path) {
        return path.startsWith('http') ? path : `${rootUrl}${path}`;
    }

    function statusTone(state) {
        const value = String(state).toLowerCase();
        if (value.includes('live') || value.includes('ready')) {
            return 'live';
        }
        if (value.includes('progress')) {
            return 'progress';
        }
        if (value.includes('planned')) {
            return 'planned';
        }
        return 'neutral';
    }

    function navIsActive(label) {
        const key = label.toLowerCase();
        const route = {
            home: '',
            products: 'products',
            updates: 'updates',
            'about us': 'about-us',
            'about me': 'about-me',
            contact: 'contact',
            legal: 'legal',
            status: 'status',
            'sign in': 'sign-in'
        }[key];

        if (page === 'home') {
            return false;
        }

        if (page === 'product') {
            return key === 'products';
        }

        return route === page;
    }

    function navItem(item) {
        const active = navIsActive(item.label);
        return h(
            'a',
            {
                key: item.label,
                className: `site-nav__link${active ? ' is-active' : ''}`,
                href: item.href,
                'aria-current': active ? 'page' : undefined
            },
            item.label
        );
    }

    function pill(text, tone = 'neutral') {
        return h('span', { className: `pill pill--${tone}` }, text);
    }

    function sectionHeader(eyebrow, title, lead) {
        return h(
            'div',
            { className: 'section-head' },
            eyebrow ? h('p', { className: 'section-head__eyebrow' }, eyebrow) : null,
            h('h2', { className: 'section-head__title' }, title),
            lead ? h('p', { className: 'section-head__lead' }, lead) : null
        );
    }

    function primaryButton(href, label) {
        return h('a', { className: 'button button--primary', href }, label);
    }

    function secondaryButton(href, label) {
        return h('a', { className: 'button button--secondary', href }, label);
    }

    function cardLink(href, label) {
        return h('a', { className: 'card__link', href }, label);
    }

    function hero(title, lead, eyebrow, actions) {
        return h(
            'section',
            { className: 'hero' },
            eyebrow ? h('p', { className: 'hero__eyebrow' }, eyebrow) : null,
            h('h1', { className: 'hero__title' }, title),
            h('p', { className: 'hero__lead' }, lead),
            actions ? h('div', { className: 'hero__actions' }, actions) : null
        );
    }

    function productCard(product) {
        return h(
            'article',
            { key: product.slug, className: 'card product-card' },
            h(
                'div',
                { className: 'card__topline' },
                pill(product.status, statusTone(product.status)),
                h('span', { className: 'card__route' }, `/${product.slug}.html`)
            ),
            h('h3', { className: 'card__title' }, product.name),
            h('p', { className: 'card__meta' }, product.purpose),
            h('p', { className: 'card__body' }, product.summary),
            h(
                'ul',
                { className: 'card__list' },
                product.details.map((detail) => h('li', { key: detail }, detail))
            ),
            cardLink(`/${product.slug}.html`, 'Open product page')
        );
    }

    function updateCard(update) {
        return h(
            'article',
            { key: `${update.date}-${update.title}`, className: 'card update-card' },
            h(
                'div',
                { className: 'card__topline' },
                pill(update.type, 'neutral'),
                h('span', { className: 'card__route' }, update.date)
            ),
            h('h3', { className: 'card__title' }, update.title),
            h('p', { className: 'card__body' }, update.summary)
        );
    }

    function ecosystemCard(entry) {
        return h(
            'article',
            { key: entry.slug, className: 'card ecosystem-card' },
            h(
                'div',
                { className: 'card__topline' },
                pill(entry.status, statusTone(entry.status)),
                h('span', { className: 'card__route' }, `${entry.slug}.harithkavish.com`)
            ),
            h('h3', { className: 'card__title' }, entry.name),
            h('p', { className: 'card__body' }, entry.summary),
            cardLink(entry.href, `Visit ${entry.slug}.harithkavish.com`)
        );
    }

    function contactCard(channel) {
        return h(
            'article',
            { key: channel.label, className: 'card contact-card' },
            h('h3', { className: 'card__title' }, channel.label),
            h('p', { className: 'card__body' }, channel.detail),
            cardLink(channel.href, channel.href.replace('mailto:', ''))
        );
    }

    function statusRow(item) {
        return h(
            'div',
            { key: item.label, className: 'status-row' },
            h('div', { className: 'status-row__label' }, item.label),
            h('div', { className: 'status-row__state' }, pill(item.state, statusTone(item.state))),
            h('p', { className: 'status-row__detail' }, item.detail)
        );
    }

    function renderHome() {
        return h(
            Fragment,
            null,
            hero(
                'Specialized software services.',
                'Designed independently. Built thoughtfully. Continuously improved. Harith Kavish is the public identity of an independent software business focused on calm, reliable online services that can evolve for years without losing their shape.',
                'Independent software business',
                [
                    primaryButton('/products.html', 'Explore Products'),
                    secondaryButton('/about-us.html#approach', 'Learn About the Approach')
                ]
            ),
            h(
                'section',
                { className: 'section', id: 'products' },
                sectionHeader('Products', 'The product catalog comes first.', 'Each product card is data-driven so new services can be added without redesigning the site.'),
                h('div', { className: 'card-grid' }, data.products.map(productCard))
            ),
            h(
                'section',
                { className: 'section', id: 'ecosystem' },
                sectionHeader('Ecosystem', 'A growing set of subdomains, each with one job.', 'Every subdomain is a focused, single-purpose service that shares the same design language and account layer.'),
                h('div', { className: 'card-grid card-grid--four' }, data.ecosystem.map(ecosystemCard))
            ),
            h(
                'section',
                { className: 'section', id: 'approach' },
                sectionHeader('Why this business exists', 'The work is built for long-term software stewardship.', 'The business is shaped around durable products, not one-off campaigns.'),
                h(
                    'div',
                    { className: 'split-grid' },
                    h(
                        'div',
                        { className: 'split-grid__primary' },
                        h(
                            'ul',
                            { className: 'principles-list' },
                            data.principles.map((point) => h('li', { key: point }, point))
                        )
                    ),
                    h(
                        'aside',
                        { className: 'split-grid__secondary note-panel' },
                        h('p', null, 'Software should get more useful over time. That means fewer forks, fewer distractions, and more attention on the parts that customers actually rely on.'),
                        h('p', null, 'The site and the products are built to share one design language so future subdomains can fit naturally into the same ecosystem.')
                    )
                )
            ),
            h(
                'section',
                { className: 'section', id: 'updates' },
                sectionHeader('Latest updates', 'Recent work, not a blog.', 'A short feed of releases, improvements, and important announcements keeps the ecosystem visibly alive.'),
                h('div', { className: 'stack stack--wide' }, data.updates.map(updateCard))
            ),
            h(
                'section',
                { className: 'section', id: 'about' },
                sectionHeader('About', 'A small independent software business.', 'Harith Kavish builds specialized online services with a careful pace and a practical view of maintenance.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'What this site is'),
                        h('p', { className: 'panel__body' }, 'A product-first public identity for an independent software business. The site avoids portfolio language, startup language, and unnecessary noise.'),
                        secondaryButton('/about-us.html', 'Read About Us')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Founder'),
                        h('p', { className: 'panel__body' }, 'Harith Kavish is the founder and sole creator. The business is intentionally faceless online and does not use a profile photograph.'),
                        secondaryButton('/about-me.html', 'Read About Me')
                    )
                )
            ),
            h(
                'section',
                { className: 'section', id: 'contact' },
                sectionHeader('Contact', 'Simple professional contact routes.', 'The site separates business, product, and security communication instead of forcing everything into one inbox.'),
                h('div', { className: 'card-grid card-grid--four' }, data.contactChannels.map(contactCard))
            )
        );
    }

    function renderProductsPage() {
        return h(
            Fragment,
            null,
            hero(
                'Products.',
                'The product catalog is the centre of the website. Each service gets a concise page, a current status, and a path that can later map cleanly to future subdomains.',
                'Product-first architecture',
                [
                    primaryButton('/contact.html', 'Contact the business'),
                    secondaryButton('/status.html', 'View status')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Current products', 'Additions should be straightforward: extend the data, create a page, and the shared layout stays intact.'),
                h('div', { className: 'card-grid' }, data.products.map(productCard))
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Future-ready by design', 'The site already assumes there may be more products, more documentation, and more customer surfaces later.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Add another product'),
                        h('p', { className: 'panel__body' }, 'Add one object to the product data, create a matching page, and the navigation, card styling, and metadata patterns stay consistent.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Keep the same language'),
                        h('p', { className: 'panel__body' }, 'Future services should feel like they belong to the same ecosystem even when they serve different audiences or live on different subdomains.')
                    )
                )
            )
        );
    }

    function renderUpdatesPage() {
        return h(
            Fragment,
            null,
            hero(
                'Updates.',
                'A short release feed is more useful than a traditional blog for a small software business. It keeps the public record focused on progress, maintenance, and important announcements.',
                'Recent changes',
                [
                    primaryButton('/products.html', 'Browse products'),
                    secondaryButton('/legal.html', 'View legal')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Latest changes', 'These updates are intentionally concise and product-oriented.'),
                h('div', { className: 'stack stack--wide' }, data.updates.map(updateCard))
            )
        );
    }

    function renderAboutUsPage() {
        return h(
            Fragment,
            null,
            hero(
                'About Us.',
                'Harith Kavish is an independent software business focused on building specialized online services with a long-term view. The goal is reliability, clarity, and steady improvement rather than marketing theater.',
                'Business identity',
                [
                    primaryButton('/products.html', 'Explore products'),
                    secondaryButton('/about-me.html', 'About the founder')
                ]
            ),
            h(
                'section',
                { className: 'section', id: 'approach' },
                sectionHeader(null, 'Approach', 'The business is designed around software stewardship, not one-off delivery.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Long-term vision'),
                        h('p', { className: 'panel__body' }, 'Products are expected to evolve over years. The architecture should make that easier instead of creating friction every time something changes.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'No custom forks'),
                        h('p', { className: 'panel__body' }, 'Shared improvements are preferred over fragmented code paths. That keeps maintenance predictable and user experience consistent.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Engineering over noise'),
                        h('p', { className: 'panel__body' }, 'The site should read as a careful software operation, not a startup pitch deck or a freelancer profile.')
                    )
                )
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Ecosystem', 'The public site, account layer, dashboard, and every subdomain should all feel like one system.'),
                h('div', { className: 'card-grid card-grid--four' }, data.ecosystem.map(ecosystemCard))
            )
        );
    }

    function renderAboutMePage() {
        return h(
            Fragment,
            null,
            hero(
                'About Me.',
                'Harith Kavish is the founder and sole creator. The business stays largely faceless online: no profile photograph, no performance, and no pressure to make the founder the main character.',
                'Founder',
                [
                    primaryButton('/contact.html', 'Contact'),
                    secondaryButton('/status.html', 'View status')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Working style', 'The emphasis is on careful engineering, clear ownership, and software that can keep improving without becoming brittle.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Quiet confidence'),
                        h('p', { className: 'panel__body' }, 'The site avoids exaggerated claims. It should feel steady, competent, and easy to trust.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Faceless by choice'),
                        h('p', { className: 'panel__body' }, 'A photograph is not needed for this business. The work, the product quality, and the consistency should do the talking.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Single-creator model'),
                        h('p', { className: 'panel__body' }, 'One person owns the direction, the build quality, and the operational standards. That makes the public identity straightforward and honest.')
                    )
                )
            )
        );
    }

    function renderContactPage() {
        return h(
            Fragment,
            null,
            hero(
                'Contact.',
                'Use the smallest possible path for the conversation you need. The contact section is separated by intent so questions reach the right place without unnecessary back-and-forth.',
                'Reach out',
                [
                    primaryButton('mailto:hello@harithkavish.com', 'General email'),
                    secondaryButton('/status.html', 'Status')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Contact routes', 'The categories are intentionally narrow and professional.'),
                h('div', { className: 'card-grid card-grid--four' }, data.contactChannels.map(contactCard))
            )
        );
    }

    function renderSignInPage() {
        return h(
            Fragment,
            null,
            hero(
                'Sign In.',
                'Account access is reserved for the future customer layer. The design is already prepared for account.harithkavish.com and the related dashboard surface, but the public site keeps this page simple for now.',
                'Reserved for account access',
                [
                    primaryButton('/contact.html', 'Contact support'),
                    secondaryButton('/products.html', 'Browse products')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'What comes next', 'The account surface will stay aligned with the same design language as the public site.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Customer identity'),
                        h('p', { className: 'panel__body' }, 'A single account layer will eventually connect the customer-facing services and keep the experience consistent across subdomains.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Dashboard access'),
                        h('p', { className: 'panel__body' }, 'The dashboard can later carry service status, usage summaries, and customer actions without changing the public design language.')
                    )
                )
            )
        );
    }

    function renderLegalPage() {
        return h(
            Fragment,
            null,
            hero(
                'Legal.',
                'This page keeps the legal position concise. There is no advertising tracker, no analytics integration, and no hidden profile collection on the public site.',
                'Privacy and terms',
                [
                    primaryButton('mailto:hello@harithkavish.com', 'Email the business'),
                    secondaryButton('/status.html', 'Status')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Privacy', 'The public site is intentionally light on data collection.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel panel--wide' },
                        h('p', { className: 'panel__body' }, 'The site does not use analytics scripts, tracking pixels, or advertising integrations. If you contact Harith Kavish by email, the information you send will be used only to respond, manage the conversation, and maintain business records as needed.'),
                        h('p', { className: 'panel__body' }, 'Future product pages may collect information necessary to operate those services, but any such collection should be described in the product itself and kept as small as practical.')
                    )
                )
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Terms', 'The site is provided as a public information surface for the business.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel panel--wide' },
                        h('p', { className: 'panel__body' }, 'Content may change without notice. The public pages are provided as-is, without warranty, and should be read in the context of the specific product or service they describe.'),
                        h('p', { className: 'panel__body' }, 'For product-specific terms, future services may publish their own pages. Security reports and urgent business issues should use the contact channels listed on the contact page.')
                    )
                )
            )
        );
    }

    function renderStatusPage() {
        return h(
            Fragment,
            null,
            hero(
                'Status.',
                'A simple operational view is better than a complex dashboard for a small software business. The goal is to show what is live now and where the ecosystem is heading next.',
                'Operational view',
                [
                    primaryButton('/updates.html', 'Latest updates'),
                    secondaryButton('/contact.html', 'Contact')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Current state', 'The site and its product surfaces are structured for gradual expansion.'),
                h('div', { className: 'status-list' }, data.statusItems.map(statusRow))
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Notes', 'The site is now prepared for future subdomains without redesigning the visual language.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Shared design language'),
                        h('p', { className: 'panel__body' }, 'The same spacing, typography, and card system can be reused across account, dashboard, documentation, pricing, and support surfaces.')
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Minimal surface area'),
                        h('p', { className: 'panel__body' }, 'Only the pages that are useful today are present. The site can grow without carrying the old portfolio or chatbot structure forward.')
                    )
                )
            )
        );
    }

    function renderProductPage(productSlug) {
        const product = productMap.get(productSlug);
        if (!product) {
            return h(
                Fragment,
                null,
                hero(
                    'Product not found.',
                    'The requested product page does not exist yet. Return to the product catalog to see the current set of services.',
                    '404',
                    [primaryButton('/products.html', 'Back to products')]
                )
            );
        }

        return h(
            Fragment,
            null,
            hero(
                product.name,
                `${product.purpose} ${product.summary}`,
                product.status,
                [
                    primaryButton('/products.html', 'Back to products'),
                    secondaryButton('/contact.html', 'Contact about this product')
                ]
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'What it does', 'Each product page is intentionally concise and future-proof.'),
                h(
                    'div',
                    { className: 'panel-grid' },
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Purpose'),
                        h('p', { className: 'panel__body' }, product.purpose)
                    ),
                    h(
                        'article',
                        { className: 'panel' },
                        h('h3', { className: 'panel__title' }, 'Current status'),
                        h('p', { className: 'panel__body' }, product.status)
                    ),
                    h(
                        'article',
                        { className: 'panel panel--wide' },
                        h('h3', { className: 'panel__title' }, 'Details'),
                        h(
                            'ul',
                            { className: 'principles-list principles-list--compact' },
                            product.details.map((detail) => h('li', { key: detail }, detail))
                        )
                    )
                )
            ),
            h(
                'section',
                { className: 'section' },
                sectionHeader(null, 'Why it exists', 'The product should become easier to use and easier to maintain over time.'),
                h(
                    'div',
                    { className: 'note-panel' },
                    h('p', null, 'This product is part of a larger ecosystem that shares one tone, one layout system, and one commitment to careful engineering.'),
                    h('p', null, 'When the corresponding subdomain exists, it should feel like the natural next step rather than a separate design experiment.')
                )
            )
        );
    }

    function renderPage() {
        switch (page) {
            case 'products':
                return renderProductsPage();
            case 'updates':
                return renderUpdatesPage();
            case 'about-us':
                return renderAboutUsPage();
            case 'about-me':
                return renderAboutMePage();
            case 'contact':
                return renderContactPage();
            case 'sign-in':
                return renderSignInPage();
            case 'legal':
                return renderLegalPage();
            case 'status':
                return renderStatusPage();
            case 'product':
                return renderProductPage(slug);
            case 'home':
            default:
                return renderHome();
        }
    }

    function injectSchema() {
        const existing = document.getElementById('harith-jsonld');
        if (existing) {
            existing.remove();
        }

        const schema = page === 'home'
            ? {
                '@context': 'https://schema.org',
                '@graph': [
                    {
                        '@type': 'Organization',
                        name: data.brand.name,
                        url: rootUrl,
                        description: data.brand.summary
                    },
                    {
                        '@type': 'WebSite',
                        name: data.brand.name,
                        url: rootUrl,
                        description: data.brand.summary
                    },
                    {
                        '@type': 'CollectionPage',
                        name: data.brand.name,
                        url: rootUrl,
                        description: data.brand.summary,
                        about: { '@id': rootUrl }
                    }
                ]
            }
            : page === 'product' && productMap.get(slug)
                ? {
                    '@context': 'https://schema.org',
                    '@type': 'Product',
                    name: productMap.get(slug).name,
                    description: productMap.get(slug).summary,
                    brand: { '@type': 'Brand', name: data.brand.name },
                    url: `${rootUrl}/${slug}.html`
                }
                : {
                    '@context': 'https://schema.org',
                    '@type': 'WebPage',
                    name: document.title,
                    url: window.location.href,
                    description: document.querySelector('meta[name="description"]')?.content || data.brand.summary
                };

        const node = document.createElement('script');
        node.type = 'application/ld+json';
        node.id = 'harith-jsonld';
        node.textContent = JSON.stringify(schema);
        document.head.appendChild(node);
    }

    function renderApp() {
        injectSchema();
        applyTheme(currentTheme, false);

        const root = document.getElementById('app');
        if (!root) {
            return;
        }

        ReactDOM.createRoot(root).render(
            h(
                'div',
                { className: 'site-shell' },
                h(
                    'header',
                    { className: 'site-header' },
                    h(
                        'div',
                        { className: 'site-header__inner' },
                        h(
                            'a',
                            { className: 'brand', href: '/index.html' },
                            h('img', { className: 'brand__mark', src: '/logo.png', alt: '', 'aria-hidden': 'true' }),
                            h(
                                'span',
                                { className: 'brand__text' },
                                h('span', { className: 'brand__name' }, data.brand.name),
                                h('span', { className: 'brand__descriptor' }, data.brand.descriptor)
                            )
                        ),
                        h(
                            'div',
                            { className: 'site-header__actions' },
                            h('nav', { className: 'site-nav', 'aria-label': 'Primary' }, data.navigation.map(navItem)),
                            h(
                                'button',
                                {
                                    type: 'button',
                                    className: 'theme-toggle',
                                    'data-theme-toggle': 'true',
                                    onClick: toggleTheme,
                                    'aria-label': currentTheme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
                                },
                                currentTheme === 'dark' ? 'Light mode' : 'Dark mode'
                            )
                        )
                    )
                ),
                h('main', { className: 'site-main' }, renderPage()),
                h(
                    'footer',
                    { className: 'site-footer' },
                    h(
                        'div',
                        { className: 'site-footer__inner' },
                        h('p', { className: 'site-footer__copy' }, `© ${new Date().getFullYear()} Harith Kavish`),
                        h('nav', { className: 'site-footer__nav', 'aria-label': 'Footer' }, data.footerLinks.map(navItem))
                    )
                )
            )
        );
    }

    renderApp();
})();