import random
from urllib.parse import urlparse
from flask import Flask, request, redirect, render_template, url_for, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shady_urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Keyword sections
top_keywords = [
    "facebook.com", "twitter.com", "nsa", "hijack", "gh424", "onclick", "ry5t",
    "leaked", "corpse", "Gh4k", "5GKdo1J", "56tb", "l4hf", "fpGMn1n", "KJHOy43",
    "s1nM45d", "zxa", "tSDfw4=="
]
middle_keywords = [
    "store", "darknet", "traffick", "dogs-being-eaten", "epstein", "terrorist",
    "leaks", "malicious", "phishing", "young-boys", "necro", "redroom", "gore",
    "abuse", "jumpscare", "kkk", "neonazi-88", "ip-stealer", "israel", "russian",
    "666", "69", "420", "88", "devil", "botnet", "pipe-bomb-instructions",
    "bomb", "dirty", "cocaine", "fentanyl", "ISIS", "passport", "dox", "dump",
    "ransom", "manifesto", "child", "klan", "malware", "organ-harvest", "crypto",
    "Skimmer", "Payload", "DAT", "mining", "bitcoin", "locker", "EVIL", "51nB",
    "spyware", "yaghbb8", "HJGFa", "J4asq4", "iranian", "136783l", "d157u4b3d",
    "31337", "lk1j14", "6672", "bj07", "45bEEv5"
]
bottom_keywords = [
    ".txt.exe", ".mp4", ".exe", ".zip", ".dmg", ".vbs", ".js", ".xyz", ".science", ".onion",
    "tor", "virus", "trustme", "grab", "redirect", "xxx", "live-murder"
]

# DB model
class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)

def normalize_url(url: str) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        return "http://" + url
    return url

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc and "." in parsed.netloc

def generate_slug() -> str:
    start = random.choice(top_keywords)
    # pick 2–5 middle keywords
    mids = random.sample(middle_keywords, k=random.randint(2, 5))
    end = random.choice(bottom_keywords)
    return "-".join([start, *mids, end])

@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        raw = request.form.get("url", "").strip()
        full = normalize_url(raw)

        if not is_valid_url(full):
            error = "❌ That doesn’t look like a valid URL."
        else:
            # generate unique slug
            while True:
                slug = generate_slug()
                if not URLMap.query.filter_by(slug=slug).first():
                    break
            db.session.add(URLMap(slug=slug, original_url=full))
            db.session.commit()
            return redirect(url_for("index", slug=slug))

    slug = request.args.get("slug")
    short_url = request.host_url + slug if slug else None
    return render_template("index.html", error=error, short_url=short_url)

@app.route("/<slug>")
def redirect_to_url(slug):
    entry = URLMap.query.filter_by(slug=slug).first()
    if not entry:
        abort(404)
    return redirect(entry.original_url)

if __name__ == "__main__":
    # Ensure DB file exists and tables are created
    if not os.path.exists("shady_urls.db"):
        open("shady_urls.db", "w").close()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
