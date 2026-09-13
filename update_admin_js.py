import re

with open('frontend/admin.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add adminFetch utility
admin_fetch_code = """const API_URL = "http://127.0.0.1:8000";

async function adminFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['X-Admin-Token'] = "vista_admin_2026";
  return fetch(url, options);
}
"""
content = content.replace('const API_URL = "http://127.0.0.1:8000";', admin_fetch_code)

# Replace all fetch calls that hit /api/admin
content = re.sub(r'fetch\(`\$\{API_URL\}/api/admin', r'adminFetch(`${API_URL}/api/admin', content)

with open('frontend/admin.js', 'w', encoding='utf-8') as f:
    f.write(content)
