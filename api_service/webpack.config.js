const path = require('path');

module.exports = {
  entry: './frontend/js/index.js',
  output: {
    filename: 'main.js',
    path: path.resolve("./static", 'js'),
  },
};