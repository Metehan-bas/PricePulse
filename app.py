import hashlib
import logging
import math
import os
import secrets
import sqlite3
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from scrapper import MAX_QUERY_LENGTH, compare_price


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
logger = logging.getLogger(__name__)

DATABASE_PATH = Path(app.instance_path) / "pricepulse.db"
MAX_TITLE_LENGTH = 500
MAX_SITE_LENGTH = 50
MAX_URL_LENGTH = 2000


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_database():
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    with get_db_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_key TEXT NOT NULL,
                site TEXT NOT NULL,
                title TEXT NOT NULL,
                price REAL NOT NULL,
                currency TEXT NOT NULL DEFAULT 'TRY',
                url TEXT,
                image_url TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, product_key),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )


def wants_json_response():
    return request.is_json or request.path.startswith("/api/")


def login_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            if wants_json_response():
                return jsonify({"error": "Bu işlem için giriş yapmalısınız"}), 401
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


def request_data():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form


def normalize_email(value):
    return str(value or "").strip().casefold()


def product_key(site, url, title):
    source = f"{site.casefold()}|{url.strip() if url else title.casefold().strip()}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def format_price(price):
    return f"{price:,.2f} TL".replace(",", "_").replace(".", ",").replace("_", ".")


def serialize_favorite(row):
    return {
        "id": row["id"],
        "product_key": row["product_key"],
        "site": row["site"],
        "title": row["title"],
        "ad": row["title"],
        "price": row["price"],
        "fiyat": format_price(row["price"]),
        "currency": row["currency"],
        "url": row["url"],
        "image_url": row["image_url"],
        "created_at": row["created_at"],
    }


def current_user_favorite_keys():
    if "user_id" not in session:
        return set()
    with get_db_connection() as connection:
        rows = connection.execute(
            "SELECT product_key FROM favorites WHERE user_id = ?",
            (session["user_id"],),
        ).fetchall()
    return {row["product_key"] for row in rows}


@app.route("/")
def mainpage():
    return render_template("mainPage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("LogIn.html")

    data = request_data()
    email = normalize_email(data.get("email") or data.get("username"))
    password = str(data.get("password") or "")

    with get_db_connection() as connection:
        user = connection.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        error = "E-posta veya şifre hatalı"
        if wants_json_response():
            return jsonify({"error": error}), 401
        return render_template("LogIn.html", error=error), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_email"] = user["email"]

    if wants_json_response():
        return jsonify({"message": "Giriş başarılı", "email": user["email"]})
    return redirect(url_for("dashboard"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("dashboard"))
        return render_template("Signup.html")

    data = request_data()
    email = normalize_email(data.get("email") or data.get("username"))
    password = str(data.get("password") or "")

    if "@" not in email or len(email) > 254:
        error = "Geçerli bir e-posta adresi girin"
    elif len(password) < 8:
        error = "Şifre en az 8 karakter olmalıdır"
    else:
        error = None

    if error:
        if wants_json_response():
            return jsonify({"error": error}), 400
        return render_template("Signup.html", error=error), 400

    try:
        with get_db_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, generate_password_hash(password)),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        error = "Bu e-posta adresi zaten kayıtlı"
        if wants_json_response():
            return jsonify({"error": error}), 409
        return render_template("Signup.html", error=error), 409

    session.clear()
    session["user_id"] = user_id
    session["user_email"] = email

    if wants_json_response():
        return jsonify({"message": "Hesap oluşturuldu", "email": email}), 201
    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Çıkış yapıldı"})


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_email=session["user_email"])


@app.route("/search", methods=["POST"])
@login_required
def search():
    data = request.get_json(silent=True) or {}
    product_name = data.get("product")

    if not isinstance(product_name, str) or not product_name.strip():
        return jsonify({"error": "Ürün adı gerekli"}), 400

    product_name = " ".join(product_name.split())
    if len(product_name) > MAX_QUERY_LENGTH:
        return jsonify(
            {"error": f"Ürün adı en fazla {MAX_QUERY_LENGTH} karakter olabilir"}
        ), 400

    try:
        results = compare_price(product_name)
        favorite_keys = current_user_favorite_keys()
        for products in results.values():
            for product in products:
                key = product_key(
                    str(product.get("site") or ""),
                    str(product.get("url") or ""),
                    str(product.get("title") or product.get("ad") or ""),
                )
                product["product_key"] = key
                product["is_favorite"] = key in favorite_keys
        return jsonify(results)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        logger.exception("Fiyat karşılaştırması sırasında hata oluştu")
        return jsonify({"error": "Arama sırasında bir hata oluştu"}), 500


@app.route("/api/favorites", methods=["GET"])
@login_required
def list_favorites():
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, product_key, site, title, price, currency, url,
                   image_url, created_at
            FROM favorites
            WHERE user_id = ?
            ORDER BY updated_at DESC, id DESC
            """,
            (session["user_id"],),
        ).fetchall()
    return jsonify([serialize_favorite(row) for row in rows])


@app.route("/api/favorites", methods=["POST"])
@login_required
def add_favorite():
    data = request.get_json(silent=True) or {}
    site = str(data.get("site") or "").strip()
    title = str(data.get("title") or data.get("ad") or "").strip()
    currency = str(data.get("currency") or "TRY").strip().upper()
    url = str(data.get("url") or "").strip() or None
    image_url = str(data.get("image_url") or "").strip() or None

    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        price = math.nan

    if not site or len(site) > MAX_SITE_LENGTH:
        return jsonify({"error": "Geçersiz mağaza bilgisi"}), 400
    if not title or len(title) > MAX_TITLE_LENGTH:
        return jsonify({"error": "Geçersiz ürün adı"}), 400
    if not math.isfinite(price) or price <= 0:
        return jsonify({"error": "Geçersiz ürün fiyatı"}), 400
    if currency != "TRY":
        return jsonify({"error": "Yalnızca TRY para birimi destekleniyor"}), 400

    for candidate in (url, image_url):
        if candidate:
            parsed = urlparse(candidate)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                return jsonify({"error": "Geçersiz ürün bağlantısı"}), 400
            if len(candidate) > MAX_URL_LENGTH:
                return jsonify({"error": "Ürün bağlantısı çok uzun"}), 400

    key = product_key(site, url or "", title)
    with get_db_connection() as connection:
        connection.execute(
            """
            INSERT INTO favorites (
                user_id, product_key, site, title, price, currency, url, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, product_key) DO UPDATE SET
                title = excluded.title,
                price = excluded.price,
                currency = excluded.currency,
                url = excluded.url,
                image_url = excluded.image_url,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                session["user_id"],
                key,
                site,
                title,
                price,
                currency,
                url,
                image_url,
            ),
        )
        row = connection.execute(
            """
            SELECT id, product_key, site, title, price, currency, url,
                   image_url, created_at
            FROM favorites
            WHERE user_id = ? AND product_key = ?
            """,
            (session["user_id"], key),
        ).fetchone()

    return jsonify(serialize_favorite(row)), 201


@app.route("/api/favorites/<int:favorite_id>", methods=["DELETE"])
@login_required
def delete_favorite(favorite_id):
    with get_db_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM favorites WHERE id = ? AND user_id = ?",
            (favorite_id, session["user_id"]),
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Favori bulunamadı"}), 404
    return jsonify({"message": "Favorilerden kaldırıldı"})


init_database()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if not os.getenv("SECRET_KEY"):
        logger.warning("Canlı ortamda SECRET_KEY çevre değişkenini ayarlayın")
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
