const path = require('path');

const i18nConfig = {
  i18n: {
    defaultLocale: 'fr',
    locales: ['en', 'fr'],
    fallbackLng: 'fr',
  },
  localePath: path.resolve('./public/locales'),
  ns: ['common', 'forms', 'errors', 'quotes', 'clients', 'admin', 'modals', 'currency'],
  defaultNS: 'common',
};

module.exports = i18nConfig;
