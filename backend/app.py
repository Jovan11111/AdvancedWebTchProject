import os
import shutil
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

db = SQLAlchemy()
MAX_BOOK_IMAGE_SIZE = 5 * 1024 * 1024


def password_error(password):
    if len(password) < 8:
        return "Lozinka mora imati najmanje 8 karaktera."
    if not any(character.isupper() for character in password):
        return "Lozinka mora sadržati veliko slovo."
    if not any(character.isdigit() for character in password):
        return "Lozinka mora sadržati broj."
    return None


def create_app():
    app = Flask(__name__)
    app.instance_path = os.path.join(os.path.dirname(__file__), "instance")
    app.config["BOOK_COVERS_DIR"] = os.path.join(app.static_folder, "book-covers")
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["BOOK_COVERS_DIR"], exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///library.db",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:4200", "http://127.0.0.1:4200"]}})
    db.init_app(app)

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        first_name = db.Column(db.String(80), nullable=False)
        last_name = db.Column(db.String(80), nullable=False)
        email = db.Column(db.String(160), unique=True, nullable=False)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        role = db.Column(db.String(20), nullable=False, default="user")

    class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(200), nullable=False)
        author = db.Column(db.String(160), nullable=False)
        description = db.Column(db.Text, nullable=False)
        isbn = db.Column(db.String(40), nullable=False)
        image_filename = db.Column(db.String(255), nullable=False, default="placeholder_book_cover.jpeg")

    class ReadingStatus(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
        book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
        status = db.Column(db.String(30), nullable=False, default="not_read")
        updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        __table_args__ = (db.UniqueConstraint("user_id", "book_id"),)

    class Friendship(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        follower_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
        following_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        __table_args__ = (db.UniqueConstraint("follower_id", "following_id"),)

    def current_user():
        user_id = request.headers.get("X-User-Id", type=int)
        return db.session.get(User, user_id) if user_id else None

    def user_json(user):
        return {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email,
            "username": user.username,
            "role": user.role,
        }

    def book_json(book, status="not_read"):
        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "description": book.description,
            "isbn": book.isbn,
            "imageUrl": f"http://127.0.0.1:5000/static/book-covers/{book.image_filename}",
            "status": status,
        }

    def friend_json(user):
        return {"id": user.id, "username": user.username, "firstName": user.first_name, "lastName": user.last_name}

    @app.post("/api/register")
    def register():
        data = request.get_json() or {}
        required = ["firstName", "lastName", "email", "username", "password"]
        if any(not data.get(field) for field in required):
            return jsonify({"message": "Sva polja su obavezna."}), 400
        if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
            return jsonify({"message": "Username ili email već postoji."}), 409
        password_message = password_error(data["password"])
        if password_message:
            return jsonify({"message": password_message}), 400
        user = User(
            first_name=data["firstName"], last_name=data["lastName"],
            email=data["email"], username=data["username"],
            password_hash=generate_password_hash(data["password"]), role="user",
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"user": user_json(user)}), 201

    @app.post("/api/login")
    def login():
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()
        if not user:
            return jsonify({"message": "Username ne postoji."}), 401
        if not check_password_hash(user.password_hash, data.get("password", "")):
            return jsonify({"message": "Lozinka nije tačna."}), 401
        return jsonify({"user": user_json(user)})

    @app.get("/api/books")
    def books():
        user = current_user()
        statuses = {item.book_id: item.status for item in ReadingStatus.query.filter_by(user_id=user.id).all()} if user else {}
        return jsonify([book_json(book, statuses.get(book.id, "not_read")) for book in Book.query.order_by(Book.title).all()])

    @app.get("/api/books/<int:book_id>")
    def book_details(book_id):
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"message": "Knjiga nije pronađena."}), 404
        user = current_user()
        reading_status = ReadingStatus.query.filter_by(user_id=user.id, book_id=book.id).first() if user else None
        return jsonify(book_json(book, reading_status.status if reading_status else "not_read"))

    @app.put("/api/books/<int:book_id>/status")
    def update_status(book_id):
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        if not db.session.get(Book, book_id):
            return jsonify({"message": "Knjiga nije pronađena."}), 404
        status = (request.get_json() or {}).get("status")
        if status not in ["not_read", "read", "want_to_read"]:
            return jsonify({"message": "Nepoznat status."}), 400
        relation = ReadingStatus.query.filter_by(user_id=user.id, book_id=book_id).first()
        if not relation:
            relation = ReadingStatus(user_id=user.id, book_id=book_id)
            db.session.add(relation)
        relation.status = status
        relation.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"status": relation.status})

    @app.get("/api/profile")
    def profile():
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        relations = ReadingStatus.query.filter_by(user_id=user.id).all()
        books_by_id = {book.id: book for book in Book.query.all()}
        friends = User.query.join(Friendship, Friendship.following_id == User.id).filter(Friendship.follower_id == user.id).order_by(User.username).all()
        return jsonify({
            "user": user_json(user),
            "readBooks": [book_json(books_by_id[item.book_id], item.status) for item in relations if item.status == "read"],
            "wantedBooks": [book_json(books_by_id[item.book_id], item.status) for item in relations if item.status == "want_to_read"],
            "friends": [friend_json(friend) for friend in friends],
        })

    @app.put("/api/profile/password")
    def change_password():
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        data = request.get_json() or {}
        if not check_password_hash(user.password_hash, data.get("oldPassword", "")):
            return jsonify({"message": "Stara lozinka nije tačna."}), 400
        password_message = password_error(data.get("newPassword", ""))
        if password_message:
            return jsonify({"message": password_message}), 400
        if data.get("newPassword") != data.get("confirmPassword"):
            return jsonify({"message": "Nove lozinke se ne poklapaju."}), 400
        user.password_hash = generate_password_hash(data["newPassword"])
        db.session.commit()
        return jsonify({"message": "Lozinka je uspešno promenjena."})

    @app.post("/api/friends")
    def add_friend():
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        username = (request.get_json() or {}).get("username", "").strip()
        friend = User.query.filter_by(username=username).first()
        if not friend:
            return jsonify({"message": "Korisnik sa tim username-om ne postoji."}), 404
        if friend.id == user.id:
            return jsonify({"message": "Ne možete zapratiti sami sebe."}), 400
        relation = Friendship.query.filter_by(follower_id=user.id, following_id=friend.id).first()
        if relation:
            return jsonify({"message": "Već pratite ovog korisnika."}), 409
        db.session.add(Friendship(follower_id=user.id, following_id=friend.id))
        db.session.commit()
        return jsonify({"friend": friend_json(friend)}), 201

    @app.get("/api/friends")
    def friends():
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        followed = User.query.join(Friendship, Friendship.following_id == User.id).filter(Friendship.follower_id == user.id).order_by(User.username).all()
        return jsonify([friend_json(friend) for friend in followed])

    @app.get("/api/friends/activities")
    def friend_activities():
        user = current_user()
        if not user:
            return jsonify({"message": "Morate biti ulogovani."}), 401
        followed_ids = db.session.query(Friendship.following_id).filter_by(follower_id=user.id).scalar_subquery()
        activities = ReadingStatus.query.filter(ReadingStatus.user_id.in_(followed_ids), ReadingStatus.status.in_(["read", "want_to_read"])).order_by(ReadingStatus.updated_at.desc()).all()
        users = {item.id: item for item in User.query.filter(User.id.in_(followed_ids)).all()}
        books = {item.id: item for item in Book.query.all()}
        return jsonify([{
            "username": users[item.user_id].username,
            "bookTitle": books[item.book_id].title,
            "status": item.status,
            "updatedAt": item.updated_at.isoformat() if item.updated_at else None,
        } for item in activities])

    @app.get("/api/users/<int:user_id>/profile")
    def public_profile(user_id):
        target = db.session.get(User, user_id)
        if not target:
            return jsonify({"message": "Korisnik nije pronađen."}), 404
        relations = ReadingStatus.query.filter_by(user_id=target.id).all()
        books_by_id = {book.id: book for book in Book.query.all()}
        friends = User.query.join(Friendship, Friendship.following_id == User.id).filter(Friendship.follower_id == target.id).order_by(User.username).all()
        return jsonify({
            "user": friend_json(target),
            "readBooks": [book_json(books_by_id[item.book_id], item.status) for item in relations if item.status == "read"],
            "wantedBooks": [book_json(books_by_id[item.book_id], item.status) for item in relations if item.status == "want_to_read"],
            "friends": [friend_json(friend) for friend in friends],
        })

    @app.post("/api/admin/books")
    def add_book():
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"message": "Samo admin može da menja knjige."}), 403
        data = request.form if request.form else (request.get_json() or {})
        required = ["title", "author", "description", "isbn"]
        if any(not data.get(field) for field in required):
            return jsonify({"message": "Sva polja knjige su obavezna."}), 400
        if Book.query.filter(db.func.lower(Book.title) == data["title"].strip().lower()).first():
            return jsonify({"message": "Knjiga sa tim naslovom već postoji."}), 409
        image = request.files.get("image")
        image_filename = "placeholder_book_cover.jpeg"
        if image and image.filename:
            image.seek(0, os.SEEK_END)
            image_size = image.tell()
            image.seek(0)
            if image_size > MAX_BOOK_IMAGE_SIZE:
                return jsonify({"message": "Slika je prevelika. Maksimalna veličina je 5 MB."}), 400
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["BOOK_COVERS_DIR"], image_filename))
        book = Book(**{field: data[field] for field in required}, image_filename=image_filename)
        db.session.add(book)
        db.session.commit()
        return jsonify(book_json(book)), 201

    @app.delete("/api/admin/books/<int:book_id>")
    def delete_book(book_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"message": "Samo admin može da menja knjige."}), 403
        book = db.session.get(Book, book_id)
        if not book:
            return jsonify({"message": "Knjiga nije pronađena."}), 404
        ReadingStatus.query.filter_by(book_id=book_id).delete()
        db.session.delete(book)
        db.session.commit()
        return jsonify({"message": "Knjiga je obrisana."})

    @app.get("/api/admin/users")
    def admin_users():
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"message": "Samo admin može da vidi korisnike."}), 403
        return jsonify([user_json(item) for item in User.query.order_by(User.username).all()])

    @app.delete("/api/admin/users/<int:user_id>")
    def delete_user(user_id):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"message": "Samo admin može da briše korisnike."}), 403
        target = db.session.get(User, user_id)
        if not target:
            return jsonify({"message": "Korisnik nije pronađen."}), 404
        if target.id == user.id:
            return jsonify({"message": "Admin ne može obrisati samog sebe."}), 400
        ReadingStatus.query.filter_by(user_id=target.id).delete()
        Friendship.query.filter((Friendship.follower_id == target.id) | (Friendship.following_id == target.id)).delete(synchronize_session=False)
        db.session.delete(target)
        db.session.commit()
        return jsonify({"message": "Korisnik je obrisan."})

    @app.get("/static/book-covers/<path:filename>")
    def book_cover(filename):
        return send_from_directory(app.config["BOOK_COVERS_DIR"], filename)

    @app.get("/api/health")
    def health_check():
        return jsonify({"status": "ok", "message": "Flask backend radi"})

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            db.session.add(User(
                first_name="System", last_name="Admin", email="admin@library.local",
                username="admin", password_hash=generate_password_hash("admin123"), role="admin",
            ))
        if Book.query.count() == 0:
            db.session.add_all([
                Book(title="Na Drini ćuprija", author="Ivo Andrić", description="Roman o mostu i ljudima oko njega.", isbn="978-86-10-00001-1", image_filename="placeholder_book_cover.jpeg"),
                Book(title="Mali princ", author="Antoine de Saint-Exupéry", description="Kratka priča o prijateljstvu, ljubavi i odgovornosti.", isbn="978-86-10-00002-8", image_filename="placeholder_book_cover.jpeg"),
                Book(title="1984", author="George Orwell", description="Distopijski roman o nadzoru i slobodi.", isbn="978-86-10-00003-5", image_filename="placeholder_book_cover.jpeg"),
                Book(title="Zločin i kazna", author="Fjodor Dostojevski", description="Roman o krivici, kazni i iskupljenju.", isbn="978-86-10-00004-2", image_filename="placeholder_book_cover.jpeg"),
                Book(title="Gospodar prstenova", author="J. R. R. Tolkien", description="Epska avantura o putovanju i hrabrosti.", isbn="978-86-10-00005-9", image_filename="placeholder_book_cover.jpeg"),
            ])
        db.session.commit()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)