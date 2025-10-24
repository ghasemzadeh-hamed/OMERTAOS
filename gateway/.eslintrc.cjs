module.exports = {
  root: true,
  parserOptions: {
    project: './tsconfig.json'
  },
  extends: [
    'standard-with-typescript'
  ],
  env: {
    node: true,
    es2021: true
  },
  rules: {
    '@typescript-eslint/strict-boolean-expressions': 'off',
    '@typescript-eslint/restrict-template-expressions': 'off'
  }
}
