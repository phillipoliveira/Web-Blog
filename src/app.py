from flask import Flask, render_template, request, session, make_response
from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User
import hashlib
import re

app = Flask(__name__)
app.secret_key = "jose"

@app.route('/')
# Returns the home page
def home_template():
    return render_template('home.html')

@app.route('/login')
# Returns the login page
def login_template():
    return render_template('login.html')

@app.route('/register')
# Returns the registration page
def register_template():
    return render_template('register.html')

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/auth/login', methods=['POST'])
# Login endpoint - this endpoint only accepts POST requests
def login_user():
    email = request.form['email']
    password = request.form['password']
    hash_pass = hashlib.sha256(password.encode()).hexdigest()
    # this will get the info submitted into the base.html page.
    if User.login_valid(email, hash_pass):
        User.login(email)
        return make_response(user_blogs())
    else:
        session['email'] = None
        return render_template('login.html')


@app.route('/auth/register', methods=['POST'])
# Register endpoint:
def register_user():
    email = request.form['email']
    password = request.form['password']
    if not all([(re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email)),(len(password) > 7)]):
        msg = "All users must have a valid email,\nand a password with a minimum of 8 characters."
        session['email'] = None
        return render_template('register.html', msg=msg)
    else:
        hash_pass = hashlib.sha256(password.encode()).hexdigest()
        # Get the user's credentials
        User.register(email, hash_pass)
        # Register the user using the method in the User object. This sets the session email, and saves the user to Mongo.
        return make_response(user_blogs())


@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
# Either of these links will reach this endpoint
def user_blogs(user_id=None):
    # We've set the default value of user_id to none,
    # because the first time we hit this endpoint, we won't have a user_id yet
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])
    # If we haven't set the user ID yet, we'll get the user object from the session email.
    blogs = user.get_blogs()
    # First this endpoint will receive the user_id. It will then create a blogs object, based on the user ID.
    return render_template('user_blogs.html', blogs=blogs, email=user.email)
# It'll then set a blogs variable as the blogs object we created,
# and pass it back to the page, along with the user's email.


@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    user = User.get_by_email(session['email'])
    blogs = user.get_blogs()
    return render_template('posts.html', posts=posts, blog_title=blog.title, blog_id=blog_id, blogs=blogs)


@app.route('/blogs/new', methods=['POST', 'GET'])
def create_new_blog():
    # If the method is 'POST' - the user hit the submit button,
    # and we need to create their blog
    # If the method is 'GET' - the user just arrived at the end point,
    # and we need to give them a way to create a blog.
    # To determine what type of request they've made, we'll use an if statement:
    if request.method == 'GET':
        user = User.get_by_email(session['email'])
        blogs = user.get_blogs()
        return render_template('new_blog.html', blogs=blogs)
    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        if not all([(len(title) > 0), (len(description) > 0)]):
            msg = "Blogs require both a title and description."
            return render_template('new_blog.html', msg=msg)
        else:
            user = User.get_by_email(session['email'])
            # We'll use the session email to determine author and author ID.

            new_blog = Blog(user.email, title, description, user._id)
            new_blog.save_to_mongo()
            return make_response(user_blogs(user._id))
            # make_response is a Flask function that allows us to redirect the user to another function.


@app.route("/posts/new/<string:blog_id>", methods=['POST', 'GET'])
def create_new_post(blog_id):
    # If the method is 'POST' - the user hit the submit button,
    # and we need to create their post
    # If the method is 'GET' - the user just arrived at the end point,
    # and we need to give them a way to create a post
    # To determine what type of request they've made, we'll use an if statement:
    if request.method == 'GET':
        user = User.get_by_email(session['email'])
        blogs = user.get_blogs()
        return render_template('new_post.html', blog_id=blog_id, blogs=blogs)
    elif request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not all([(len(title) > 0), (len(content) > 0)]):
            msg = "Posts require both a title and content."
            return render_template('new_post.html', blog_id=blog_id, msg=msg)
        else:
            user = User.get_by_email(session['email'])
            # We'll use the session email to determine author and author ID.
            new_post = Post(blog_id, title, content, user.email)
            new_post.save_to_mongo()
            return make_response(blog_posts(blog_id))
            # make_response is a Flask function that allows us to redirect the user to another function.


if __name__ == '__main__':
    app.run()