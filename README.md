<a id="top"></a>

<div align="center">

  <h1>💜 PricePulse</h1>

  <p><strong>Compare prices. Find the right product. Save your favorites.</strong></p>

  <p>
    PricePulse is a lightweight price comparison and product-tracking application<br>
    built for Turkish e-commerce platforms.
  </p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
    <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-Web_App-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"></a>
    <a href="https://www.selenium.dev/"><img src="https://img.shields.io/badge/Selenium-Scraping-43B02A?style=for-the-badge&logo=selenium&logoColor=white" alt="Selenium"></a>
    <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite"></a>
  </p>

  <p>
    <a href="#features">Features</a> •
    <a href="#stores">Stores</a> •
    <a href="#getting-started">Installation</a> •
    <a href="#project-structure">Structure</a> •
    <a href="#security">Security</a>
  </p>

</div>

<hr>

<h2 id="about">📖 About PricePulse</h2>

<p>
  PricePulse searches multiple online stores, normalizes their prices, filters unrelated
  products, and presents the most relevant offers in a single dashboard. Users can create
  an account, compare products, open the original store page, and maintain a personal
  favorites list.
</p>

<p>
  Each store scraper runs independently. If one store fails or times out, PricePulse can
  continue returning results from the other stores.
</p>

<h2 id="features">✨ Features</h2>

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>🔎 Smart Search</h3>
      <p>Search several stores from one dashboard and receive ranked product results.</p>
    </td>
    <td width="33%" valign="top">
      <h3>💰 Price Comparison</h3>
      <p>Normalize Turkish Lira prices and compare the most relevant offers.</p>
    </td>
    <td width="33%" valign="top">
      <h3>⭐ Personal Favorites</h3>
      <p>Save products to a favorites list connected to the signed-in user.</p>
    </td>
  </tr>
  <tr>
    <td width="33%" valign="top">
      <h3>🎯 Product Matching</h3>
      <p>Reduce mismatches between storage sizes, accessories, and model variants.</p>
    </td>
    <td width="33%" valign="top">
      <h3>🔐 Secure Accounts</h3>
      <p>Protect user passwords with hashing and manage access through Flask sessions.</p>
    </td>
    <td width="33%" valign="top">
      <h3>🛡️ Failure Isolation</h3>
      <p>Keep other store results available when an individual scraper encounters an error.</p>
    </td>
  </tr>
</table>

<h3>Product matching checks</h3>

<ul>
  <li>Filters phone cases, cables, chargers, and other accessories when they are not requested.</li>
  <li>Detects storage differences such as <code>128 GB</code> and <code>256 GB</code>.</li>
  <li>Reduces mismatches between <code>Pro</code>, <code>Max</code>, <code>Plus</code>, and <code>Ultra</code> variants.</li>
  <li>Removes duplicate Amazon products by using their ASIN values.</li>
  <li>Avoids reading installment, list, or unit prices as the current Amazon price.</li>
</ul>

<h2 id="stores">🛍️ Supported Stores</h2>

<table>
  <thead>
    <tr>
      <th align="left">Store</th>
      <th align="center">Product Name</th>
      <th align="center">Price</th>
      <th align="center">Product Link</th>
      <th align="center">Image</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Trendyol</strong></td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
    </tr>
    <tr>
      <td><strong>Hepsiburada</strong></td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
    </tr>
    <tr>
      <td><strong>Amazon Türkiye</strong></td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
    </tr>
  </tbody>
</table>

<h2 id="workflow">⚙️ How It Works</h2>

<p align="center">
  <code>Search Request</code>
  &nbsp;➜&nbsp;
  <code>Store Scrapers</code>
  &nbsp;➜&nbsp;
  <code>Price Normalization</code>
  &nbsp;➜&nbsp;
  <code>Product Matching</code>
  &nbsp;➜&nbsp;
  <code>Ranked Results</code>
</p>

<ol>
  <li>The user enters a product name in the dashboard.</li>
  <li>Selenium opens the supported store search pages.</li>
  <li>Product names, prices, links, and images are extracted.</li>
  <li>Prices are converted into a consistent Turkish Lira format.</li>
  <li>Irrelevant products and incompatible variants are penalized or removed.</li>
  <li>The remaining results are ranked and displayed to the user.</li>
</ol>

<h2 id="technology">🧰 Technology Stack</h2>

<table>
  <thead>
    <tr>
      <th align="left">Layer</th>
      <th align="left">Technology</th>
      <th align="left">Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Backend</strong></td>
      <td>Python, Flask</td>
      <td>Routes, sessions, authentication, and APIs</td>
    </tr>
    <tr>
      <td><strong>Scraping</strong></td>
      <td>Selenium</td>
      <td>Browser automation and product extraction</td>
    </tr>
    <tr>
      <td><strong>Database</strong></td>
      <td>SQLite</td>
      <td>User accounts and favorite products</td>
    </tr>
    <tr>
      <td><strong>Frontend</strong></td>
      <td>HTML, Tailwind CSS, JavaScript</td>
      <td>Dashboard and user interactions</td>
    </tr>
    <tr>
      <td><strong>Security</strong></td>
      <td>Werkzeug</td>
      <td>Password hashing and verification</td>
    </tr>
  </tbody>
</table>

<h2 id="getting-started">🚀 Getting Started</h2>

<h3>Requirements</h3>

<ul>
  <li>Python 3.10 or newer</li>
  <li>Google Chrome</li>
  <li>Git</li>
</ul>

<details open>
  <summary><strong>1. Clone the repository</strong></summary>
  <br>
  <pre><code>git clone https://github.com/Metehan-bas/PricePulse.git
cd PricePulse</code></pre>
</details>

<details>
  <summary><strong>2. Create and activate a virtual environment</strong></summary>
  <br>
  <p><strong>Windows PowerShell</strong></p>
  <pre><code>python -m venv .venv
.\.venv\Scripts\Activate.ps1</code></pre>
  <p><strong>macOS or Linux</strong></p>
  <pre><code>python3 -m venv .venv
source .venv/bin/activate</code></pre>
</details>

<details>
  <summary><strong>3. Install the dependencies</strong></summary>
  <br>
  <pre><code>pip install -r requirements.txt</code></pre>
  <p>If a requirements file is not available yet:</p>
  <pre><code>pip install flask selenium</code></pre>
</details>

<details>
  <summary><strong>4. Configure the application secret</strong></summary>
  <br>
  <p><strong>Windows PowerShell</strong></p>
  <pre><code>$env:SECRET_KEY="replace-this-with-a-long-random-value"</code></pre>
  <p><strong>macOS or Linux</strong></p>
  <pre><code>export SECRET_KEY="replace-this-with-a-long-random-value"</code></pre>
</details>

<details open>
  <summary><strong>5. Start PricePulse</strong></summary>
  <br>
  <pre><code>python app.py</code></pre>
  <p>Open <a href="http://127.0.0.1:5000"><code>http://127.0.0.1:5000</code></a> in your browser.</p>
</details>

<h2 id="project-structure">📁 Project Structure</h2>

<pre><code>PricePulse/
├── app.py                 # Flask routes, authentication, and favorites
├── scrapper.py            # Scraping and product-matching logic
├── requirements.txt       # Python dependencies
├── .gitignore             # Files excluded from Git
├── templates/
│   ├── mainPage.html      # Landing page
│   ├── LogIn.html         # Login page
│   ├── Signup.html        # Registration page
│   └── dashboard.html     # Search results and favorites
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── instance/
    └── pricepulse.db      # Local database; excluded from Git</code></pre>

<blockquote>
  The <code>instance</code> directory and SQLite database are created automatically when the application starts.
</blockquote>

<h2 id="routes">🔌 Application Routes</h2>

<table>
  <thead>
    <tr>
      <th align="left">Method</th>
      <th align="left">Route</th>
      <th align="left">Description</th>
      <th align="center">Login</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>GET</code></td><td><code>/</code></td><td>Landing page</td><td align="center">—</td></tr>
    <tr><td><code>GET / POST</code></td><td><code>/signup</code></td><td>Create an account</td><td align="center">—</td></tr>
    <tr><td><code>GET / POST</code></td><td><code>/login</code></td><td>Sign in</td><td align="center">—</td></tr>
    <tr><td><code>POST</code></td><td><code>/logout</code></td><td>End the current session</td><td align="center">—</td></tr>
    <tr><td><code>GET</code></td><td><code>/dashboard</code></td><td>Open the dashboard</td><td align="center">✅</td></tr>
    <tr><td><code>POST</code></td><td><code>/search</code></td><td>Search and compare products</td><td align="center">✅</td></tr>
    <tr><td><code>GET / POST</code></td><td><code>/api/favorites</code></td><td>List or add favorites</td><td align="center">✅</td></tr>
    <tr><td><code>DELETE</code></td><td><code>/api/favorites/&lt;id&gt;</code></td><td>Remove a favorite</td><td align="center">✅</td></tr>
  </tbody>
</table>

<h2 id="data">🗄️ Data Storage</h2>

<p>PricePulse stores local development data in:</p>

<pre><code>instance/pricepulse.db</code></pre>

<table>
  <thead>
    <tr>
      <th align="left">Table</th>
      <th align="left">Stored Data</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>users</code></td>
      <td>Email addresses, password hashes, and creation dates</td>
    </tr>
    <tr>
      <td><code>favorites</code></td>
      <td>User-specific products, stores, prices, links, and images</td>
    </tr>
  </tbody>
</table>

<p>
  SQLite is suitable for local development. PostgreSQL or Supabase is recommended
  before deploying the application for multiple users.
</p>

<h2 id="security">🔐 Security</h2>

<table>
  <tr>
    <td>✅ Passwords are stored as hashes, never as plain text.</td>
  </tr>
  <tr>
    <td>✅ The application secret is loaded from the <code>SECRET_KEY</code> environment variable.</td>
  </tr>
  <tr>
    <td>✅ Database files, virtual environments, and secret files are excluded through <code>.gitignore</code>.</td>
  </tr>
  <tr>
    <td>⚠️ API keys and credentials must never be committed to the repository.</td>
  </tr>
</table>

<h2 id="limitations">⚠️ Known Limitations</h2>

<ul>
  <li>Store page structures may change and require scraper selector updates.</li>
  <li>Amazon may occasionally display a robot verification page.</li>
  <li>Search speed depends on store response times and network conditions.</li>
  <li>Prices and availability should be confirmed on the original product page.</li>
</ul>

<h2 id="roadmap">🗺️ Roadmap</h2>

<ul>
  <li>⬜ Price history charts</li>
  <li>⬜ Price-drop notifications</li>
  <li>⬜ PostgreSQL or Supabase integration</li>
  <li>⬜ Background scraping jobs</li>
  <li>⬜ Product category filters</li>
  <li>⬜ Automated scraper tests</li>
</ul>

<hr>

<div align="center">
  <p>Built as a learning project for web scraping, Flask, authentication, and price comparison.</p>
  <p><a href="#top">Back to top ↑</a></p>
</div>
