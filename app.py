from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import CreateEventForm, RegisterForm, LoginForm, CommentForm, LostFoundForm, GrievanceForm, CanteenForm
from flask_gravatar import Gravatar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_email = "yahoo mail id goes here"
password = "yahoo app password"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLES

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    lostfoundcomments = relationship("LostFoundComment", back_populates="comment_author")
    lostfound = relationship("LostFound", back_populates="author")
    order = relationship("Order", back_populates="author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    comment = db.Column(db.Text, nullable=False)
    comment_author = relationship("User", back_populates="comments")
    parent_post = relationship("BlogPost", back_populates="comments")


class LostFoundComment(db.Model):
    __tablename__ = "lostfoundcomments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("lostfound.id"))
    comment = db.Column(db.Text, nullable=False)
    comment_author = relationship("User", back_populates="lostfoundcomments")
    parent_post = relationship("LostFound", back_populates="comments")


class LostFound(db.Model):
    __tablename__ = "lostfound"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(100), nullable=False)
    user_choice = db.Column(db.Text, nullable=False)
    item_desc = db.Column(db.Text, nullable=False)
    image = db.Column(db.String)
    author = relationship("User", back_populates="lostfound")
    comments = relationship("LostFoundComment", back_populates="parent_post")


class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    order_desc = db.Column(db.Text, nullable=False)
    author = relationship("User", back_populates="order")
    order_id = db.Column(db.Integer, nullable=False)


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash("You've already signed up with that email, log in instead!", "error")
            return redirect(url_for('login'))
        hashed_salted_psw = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=email,
            password=hashed_salted_psw,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", "error")
            return redirect(url_for('login', form=form))
        elif user and not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'error')
            return redirect(url_for('login', form=form))
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            comment = form.comment.data
            new_comment = Comment(
                comment=comment,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
        return render_template("post.html", post=requested_post, form=form)
    return render_template("post.html", post=requested_post, form=form)


@app.route("/grievance", methods=["GET", "POST"])
def contact():
    if current_user.is_authenticated:
        form = GrievanceForm()
        if form.validate_on_submit():
            user_choice = form.user_choice.data
            email = form.email.data
            phone_no = form.phone_no.data
            grievance = form.grievance.data
            if user_choice == "Cleanliness":
                reciever = "aniruddha.fale@gmail.com"
            else:
                reciever = "sidsinghcs@gmail.com"
            with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                connection.starttls()
                connection.ehlo()
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=reciever,
                    msg=f"Subject:{user_choice} Issue\n\nMy name is {current_user.name} and my issue is {grievance}\nYou can contact me"
                        f" through the below given details:\nPhone No- {phone_no}\nEmail- {email}"
                )
            flash("Response has been submitted successfully!", "success")
    else:
        flash("You need to login first!")
        return redirect("/login")
    return render_template("contact.html", form=form)


@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreateEventForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreateEventForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/canteen_admin/<int:order_id>")
def delete_order(order_id):
    order_to_delete = Order.query.get(order_id)
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        message = """\
        <html>
        	<head>
        		<meta charset="utf-8" />
        		<title></title>
        		<style>
        			.invoice-box {
        				max-width: 800px;
        				margin: auto;
        				padding: 30px;
        				border: 1px solid #eee;
        				box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
        				font-size: 16px;
        				line-height: 24px;
        				font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        				color: #555;
        			}
        			.invoice-box table {
        				width: 100%;
        				line-height: inherit;
        				text-align: left;
        			}
        			.invoice-box table td {
        				padding: 5px;
        				vertical-align: top;
        			}
        			.invoice-box table tr td:nth-child(2) {
        				text-align: right;
        			}
        			.invoice-box table tr.top table td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.top table td.title {
        				font-size: 45px;
        				line-height: 45px;
        				color: #333;
        			}
        			.invoice-box table tr.information table td {
        				padding-bottom: 40px;
        			}
                  .idno{
                  	font-weight: bold;
                    font-size: 60px;
                    padding-top:70px;
                    text-align: center;
                  }
                  .invoiceid{
                  	text-align: center;
                  }
        			.invoice-box table tr.heading td {
        				background: #eee;
        				border-bottom: 1px solid #ddd;
        				font-weight: bold;
        			}
        			.invoice-box table tr.details td {
        				padding-bottom: 20px;
        			}
        			.invoice-box table tr.item td {
        				border-bottom: 1px solid #eee;
        			}
        			.invoice-box table tr.item.last td {
        				border-bottom: none;
        			}
        			.invoice-box table tr.total td:nth-child(2) {
        				border-top: 2px solid #eee;
        				font-weight: bold;
        			}
        			@media only screen and (max-width: 600px) {
        				.invoice-box table tr.top table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        				.invoice-box table tr.information table td {
        					width: 100%;
        					display: block;
        					text-align: center;
        				}
        			}
        			/** RTL **/
        			.invoice-box.rtl {
        				direction: rtl;
        				font-family: Tahoma, 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        			}
        			.invoice-box.rtl table {
        				text-align: right;
        			}
        			.invoice-box.rtl table tr td:nth-child(2) {
        				text-align: left;
        			}
        		</style>
        	</head>
        	<body>
        		<div class="invoice-box">
        			<table cellpadding="0" cellspacing="0">
        				<tr class="top">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td class="title">
        									<img src="https://png.pngtree.com/png-vector/20190830/ourmid/pngtree-crossed-spoon-and-fork-restaurant-and-food-logo-design-png-image_1716397.jpg" style="width: 100%; max-width: 300px" />
        								</td>
        								<td>
                                          <table>
                                            <tr class>
                                              <td class="invoiceid">Invoice ID</td>
                                            </tr>
                                            <tr>
                                              <td class="idno">""" + str(order_to_delete.order_id) + """</td>
                                            </tr>
                                          </table>
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>
        				<tr class="information">
        					<td colspan="2">
        						<table>
        							<tr>
        								<td>
        									Canteen<br />
        									e-Campus<br />
        									Thane 400607
        								</td>
        							<td>
        									<br />
        									<br />
        									9372642011
        								</td>
        							</tr>
        						</table>
        					</td>
        				</tr>
        				<tr class="heading">
        					<td>Payment Method</td>
        				</tr>
        				<tr class="details">
        					<td>Offline</td>
        				</tr>
        				<tr class="heading">
        					<td>Item</td>
        				</tr>
        				<tr class="items">
        					<td>""" + order_to_delete.order_desc + """</td>
        				</tr>
        			</table>
        		</div>
        	</body>
        </html>
        """
        connection.starttls()
        connection.ehlo()
        connection.login(user=my_email, password=password)
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(message, 'html'))
        msg['Subject'] = f'Order id {order_to_delete.order_id} has been prepared'
        msg['From'] = my_email
        msg['To'] = order_to_delete.author.email
        connection.sendmail(
            from_addr=my_email,
            to_addrs=order_to_delete.author.email,
            msg=msg.as_string()
        )
    db.session.delete(order_to_delete)
    db.session.commit()
    return redirect(url_for('view_orders'))


@app.route("/canteen", methods=["GET", "POST"])
def canteen():
    with open("order.txt", "r") as file:
        order_id = int(file.read())
    if current_user.is_authenticated:
        form = CanteenForm()
        if form.validate_on_submit():
            new_order = Order(
                order_id=order_id,
                author_id=current_user.id,
                order_desc=form.order.data
            )
            db.session.add(new_order)
            db.session.commit()
            order_id += 1
            with open("order.txt", "w") as file:
                file.write(str(order_id))
            flash(f"Your order id {new_order.order_id} has been received and will be prepared soon!", "success")
            return redirect(url_for("canteen"))
    else:
        flash("You need to login first!")
        return redirect("/login")
    return render_template("canteen.html", form=form)


@app.route("/canteen_admin", methods=["GET", "POST"])
def view_orders():
    orders = Order.query.all()
    return render_template("canteen_orders.html", orders=orders)


@app.route("/new-lostfound", methods=["GET", "POST"])
def add_lostfound():
    form = LostFoundForm()
    if form.validate_on_submit():
        new_post = LostFound(
            title=form.title.data,
            user_choice=form.user_choice.data,
            author_id=current_user.id,
            item_desc=form.item_desc.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_items"))
    return render_template("lost_found.html", form=form)


@app.route('/lostfound')
def get_all_items():
    posts = LostFound.query.all()
    return render_template("indexlostfound.html", all_posts=posts)


@app.route("/lost_found/<int:item_id>", methods=["GET", "POST"])
def lost_found(item_id):
    if current_user.is_authenticated:
        items = LostFound.query.get(item_id)
        form = CommentForm()
        if form.validate_on_submit():
            new_comment = LostFoundComment(
                comment=form.comment.data,
                author_id=current_user.id,
                post_id=items.id
            )
            db.session.add(new_comment)
            db.session.commit()
        return render_template("show_lostfound.html", post=items, form=form)

    return redirect("/login")


@app.route("/del_lost_found/<int:item_id>")
def delete_item(item_id):
    item_to_delete = LostFound.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_items'))


if __name__ == "__main__":
    app.run(debug=True)
