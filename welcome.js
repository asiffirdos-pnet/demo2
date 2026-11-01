const express = require('express');

const app = express();

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

app.get('/welcome', (req, res) => {
  const user = escapeHtml(req.query.user ?? '');
  res.send('<h1>Welcome ' + user + '</h1>');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Listening on http://localhost:${PORT}`);
});
