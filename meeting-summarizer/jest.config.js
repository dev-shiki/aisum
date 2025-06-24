module.exports = {
  moduleFileExtensions: ['js', 'json', 'vue'],
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.js$': 'babel-jest'
  },
  testMatch: [
    '**/src/components/__tests__/**/*.spec.js'
  ],
  testEnvironment: 'jsdom'
} 