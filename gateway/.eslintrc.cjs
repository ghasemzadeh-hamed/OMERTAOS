module.exports = {
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'simple-import-sort'],
  extends: ['eslint:recommended', 'plugin:@typescript-eslint/recommended', 'plugin:import/errors', 'plugin:import/warnings', 'plugin:import/typescript', 'prettier'],
  env: {
    es2021: true,
    node: true
  },
  rules: {
    'simple-import-sort/imports': 'error',
    'simple-import-sort/exports': 'error'
  }
};
