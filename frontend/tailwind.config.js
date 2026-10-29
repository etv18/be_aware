/** Tailwind scans the templates and the page scripts for class names. After adding a class, run `npm run build:css`. */
const withAlpha = (name) => `rgb(var(--${name}) / <alpha-value>)`;

module.exports = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['../app/templates/**/*.html', '../app/static/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        canvas: withAlpha('canvas'),      // the page background
        surface: withAlpha('surface'),    // cards, tables, dialogs
        sunken: withAlpha('sunken'),      // table headers, hovers, tags
        line: withAlpha('line'),          // borders
        ink: withAlpha('ink'),            // main text and the primary button
        'ink-inverse': withAlpha('ink-inverse'),
        muted: withAlpha('muted'),        // secondary text
        faint: withAlpha('faint'),        // placeholders
        positive: withAlpha('positive'),
        negative: withAlpha('negative'),
        warning: withAlpha('warning'),
        info: withAlpha('info'),
        // the color of the module being shown (set by <body data-module>) and the text color on top of it
        module: withAlpha('module'),
        'on-module': withAlpha('on-module'),
        // one hue per kind of record, used for small dots and tags only
        expenses: withAlpha('c-expenses'),
        incomes: withAlpha('c-incomes'),
        loans: withAlpha('c-loans'),
        debts: withAlpha('c-debts'),
        withdrawals: withAlpha('c-withdrawals'),
        deposits: withAlpha('c-deposits'),
      },
      fontFamily: {
        sans: ['ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
      fontSize: { base: ['0.875rem', '1.35rem'] },
      borderRadius: { xl: '0.875rem' },
      spacing: { rail: '4.25rem' },
    },
  },
  plugins: [],
};
