from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_clé_secrète_ici'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.String(500))
    profile_pic = db.Column(db.String(255), default='default.jpg')
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    interests = db.Column(db.String(500))
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    followers = db.relationship('Follower',
                              foreign_keys='Follower.followed_id',
                              backref=db.backref('followed', lazy=True),
                              lazy=True)
    following = db.relationship('Follower',
                              foreign_keys='Follower.follower_id',
                              backref=db.backref('follower', lazy=True),
                              lazy=True)
    sent_messages = db.relationship('Message', 
                                    foreign_keys='Message.sender_id', 
                                    backref='sender', 
                                    lazy='dynamic')
    received_messages = db.relationship('Message', 
                                        foreign_keys='Message.receiver_id', 
                                        backref='receiver', 
                                        lazy='dynamic')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255))
    caption = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)
    likes = db.relationship('Like', backref='post', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Toujours montrer toutes les publications pour les utilisateurs connectés
    if current_user.is_authenticated:
        # Récupérer TOUTES les publications, pas seulement celles des utilisateurs suivis
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    else:
        # Pour les utilisateurs non connectés, montrer aussi toutes les publications
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        file = request.files['image']
        caption = request.form['caption']
        
        # Diagnostic logging
        print("DEBUG: Post Creation Started")
        print(f"Current User: {current_user.username}")
        print(f"Current User ID: {current_user.id}")
        
        if file:
            try:
                # Improved filename generation
                filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Ensure upload directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                file.save(file_path)
                
                # More detailed logging
                print(f"DEBUG: File saved at {file_path}")
                print(f"DEBUG: File size: {os.path.getsize(file_path)} bytes")
                
                # Create post with absolute path
                post = Post(
                    image_path=filename,  # Store relative path
                    caption=caption,
                    user_id=current_user.id
                )
                
                db.session.add(post)
                db.session.commit()
                
                # Comprehensive post creation logging
                print(f"DEBUG: Post created successfully")
                print(f"DEBUG: Post ID: {post.id}")
                print(f"DEBUG: Post User ID: {post.user_id}")
                print(f"DEBUG: Post Image Path: {post.image_path}")
                print(f"DEBUG: Post Caption: {post.caption}")
                
                flash('Publication créée avec succès!', 'success')
                return redirect(url_for('index'))
            
            except Exception as e:
                # Detailed error logging
                print(f"ERREUR lors de la création de la publication: {e}")
                print(f"Type d'erreur: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                
                db.session.rollback()
                flash(f'Erreur lors de la création: {str(e)}', 'error')
        else:
            flash('Aucun fichier image n\'a été téléchargé', 'warning')
    
    return render_template('create_post.html')

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
    
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    is_following = False
    if current_user.is_authenticated:
        is_following = Follower.query.filter_by(
            follower_id=current_user.id,
            followed_id=user.id
        ).first() is not None
    return render_template('profile.html', user=user, posts=posts, is_following=is_following)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user_to_follow = User.query.filter_by(username=username).first_or_404()
    if user_to_follow.id == current_user.id:
        flash('Vous ne pouvez pas vous suivre vous-même')
        return redirect(url_for('profile', username=username))
        
    follower = Follower.query.filter_by(
        follower_id=current_user.id,
        followed_id=user_to_follow.id
    ).first()
    
    if follower:
        db.session.delete(follower)
        flash(f'Vous ne suivez plus {username}')
    else:
        follower = Follower(follower_id=current_user.id, followed_id=user_to_follow.id)
        db.session.add(follower)
        flash(f'Vous suivez maintenant {username}')
        
    db.session.commit()
    return redirect(url_for('profile', username=username))

@app.route('/search_users', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
        query = request.form['username']
        # Recherche insensible à la casse et partielle
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        return render_template('search_results.html', users=users, query=query)
    return render_template('search_users.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.bio = request.form.get('bio')
        current_user.location = request.form.get('location')
        current_user.website = request.form.get('website')
        current_user.interests = request.form.get('interests')
        
        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.profile_pic = filename
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('profile', username=current_user.username))
    
    return render_template('edit_profile.html')

@app.route('/messages')
@login_required
def messages():
    # Get unique conversations
    sent_conversations = db.session.query(Message.receiver_id, User).join(User, Message.receiver_id == User.id)\
        .filter(Message.sender_id == current_user.id).distinct().all()
    received_conversations = db.session.query(Message.sender_id, User).join(User, Message.sender_id == User.id)\
        .filter(Message.receiver_id == current_user.id).distinct().all()
    
    # Combine and deduplicate conversations
    conversations = {}
    for user_id, user in sent_conversations + received_conversations:
        if user_id != current_user.id and user_id not in conversations:
            conversations[user_id] = user
    
    return render_template('messages.html', 
                           conversations=list(conversations.values()), 
                           Message=Message)

@app.route('/messages/<int:user_id>', methods=['GET', 'POST'])
@login_required
def conversation(user_id):
    other_user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            message = Message(
                sender_id=current_user.id, 
                receiver_id=user_id, 
                content=content
            )
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('conversation', user_id=user_id))
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        receiver_id=current_user.id, 
        sender_id=user_id, 
        is_read=False
    ).all()
    for msg in unread_messages:
        msg.is_read = True
    db.session.commit()
    
    # Get conversation messages
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            db.and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp).all()
    
    return render_template('conversation.html', 
                           other_user=other_user, 
                           messages=messages, 
                           Message=Message)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Supprimer la base de données existante si elle existe
    db_path = 'social.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    with app.app_context():
        db.create_all()
        print("Base de données créée avec succès!")
    
    app.run(debug=True)
