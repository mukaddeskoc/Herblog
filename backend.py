from flask import Flask,render_template,flash,redirect,url_for,session,request,logging
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)
app.secret_key="blog"

class RegisterForm(Form):
    name=StringField("İsim Soyisim",validators=[validators.Length(min=6, max=30)])
    username = StringField("Kullanıcı adı",validators=[validators.Length(min=6, max=30)])
    email = StringField("E posta",validators=[validators.email(message="Geçerli bir email adresi giriniz")])
    password = PasswordField("Parola",validators=[
        validators.DataRequired("Lütfen bir parola belileyin"),
        validators.length(min=6),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor")    
    ])
    confirm=PasswordField("Parola Doğrula")

class LoginForm(Form):
    username=StringField("Kullanıcı adı")
    password=PasswordField("Parola")

class ArticleForm(Form):
    title=StringField("Başlık",validators=[validators.Length(min=6, max=75)])
    category=SelectField('Kategori',choices=[('Teknoloji','Teknoloji'),('Bilim','Bilim'),('Programlama','Programlama'),('Haber','Haber'),('Spor','Spor'),('Sağlık','Sağlık'),('Ekonomi','Ekonomi')])
    content=TextAreaField("İçerik",validators=[validators.Length(min=8)])

def login_required(f):
    @wraps(f)
    def decorator_function(*args,**kwargs):
        if "logged_in" in session:
            return f(*args,**kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapmanız lazım...","danger")
            return redirect(url_for("login"))
    return decorator_function

#Db bağlantı konfigürasyonu başladı
app.config["MYSQL_HOST"] ="localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "blog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)
#Db bağlantı konfigürasyonu bitti

@app.route("/")
def index():

    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article/<string:id>")
def article(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from makale where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article=article)
    else:
        return render_template("article.html")

@app.route("/technology")
def technology():
    cursor=mysql.connection.cursor()
    sorgu="Select * from makale where category='Teknoloji'"
    result = cursor.execute(sorgu)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("technology.html",articles=articles)
    else:
        return render_template("technology.html")

@app.route("/science")
def science():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM makale WHERE category='Bilim'"
    result = cursor.execute(sorgu)
    print(result)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("science.html",articles=articles)
    else:
        return render_template("science.html")
@app.route("/programming")
def programming():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM makale WHERE category='Programlama'"
    result = cursor.execute(sorgu)
    print(result)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("programming.html",articles=articles)
    else:
        return render_template("programming.html")

@app.route("/news")
def news():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM makale WHERE category='Haber'"
    result = cursor.execute(sorgu)
    print(result)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("news.html",articles=articles)
    else:
        return render_template("news.html")

@app.route("/sport")
def sport():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM makale WHERE category='Spor'"
    result = cursor.execute(sorgu)
    print(result)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("sport.html",articles=articles)
    else:
        return render_template("sport.html")

@app.route("/health")
def health():
    cursor=mysql.connection.cursor()
    sorgu="SELECT * FROM makale WHERE category='Sağlık'"
    result = cursor.execute(sorgu)
    print(result)
    if result > 0:
        articles = cursor.fetchall()
        return render_template("health.html",articles=articles)
    else:
        return render_template("health.html")



@app.route("/register",methods=["GET","POST"])
def register():
    form = RegisterForm(request.form)
    if(request.method=="POST" and form.validate()):
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        sorgu= "Insert into user(name,email,username,password) VALUES(%s,%s,%s,%s) "
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("Artık ailemizin bir parçasısınız","success")
        return redirect(url_for("login"))

    else:
        return render_template("register.html",form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm(request.form)
    if(request.method=="POST"):
        username=form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        sorgu= "Select * from user where username = %s"
        result=cursor.execute(sorgu,(username,))

        if result>0:
            data=cursor.fetchone()
            real_passw=data["password"]
            if sha256_crypt.verify(password,real_passw):
                flash("Başarılı giriş yaptınız.","success")
                session["logged_in"] = True
                session["username"] = username

                return redirect(url_for("index"))
            else:
                flash("Parola eksik veya hatalı.","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmamaktadır.","danger")
            return redirect(url_for("login"))

    return render_template("login.html",form=form)
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "Select * from makale"
    result=cursor.execute(sorgu)
    if result >0:
        articles=cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")
@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu= "Select * from makale where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result>0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")

@app.route("/addarticle",methods=["GET","POST"])
@login_required
def addarticle():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate:
        title = form.title.data
        category=form.category.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        sorgu="Insert into makale (title,author,category,content) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],category,content))
        mysql.connection.commit()
        cursor.close()
        flash("Makele Başarılı bir şekilde kaydedildi","success")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form=form)

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    sorgu="Select * from makale where author = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))
    if result > 0:
        sorgu2="Delete from makale where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işlem için yetkiniz yok.","danger")
        return redirect(url_for("dashboard"))
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
# Yazılan makalelerin id değerine göre veritabanından bilgilerin çekilmesi ve sonrasında yapılan güncellemeler sonucu veri tabanına tekrar işlenmesi sağlanır.
def edit(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from makale where  id = %s and author = %s "
        result = cursor.execute(sorgu,(id,session["username"]))
        if result == 0:
            flash("Böyle bir makale yok veya bu işlem için yetkiniz yok.","danger")
            session.clear()
            return redirect(url_for("index"))
        else:
            article=cursor.fetchone()
            form =ArticleForm()

            form.title.data = article["title"]
            form.category.data = article["category"]
            form.content.data = article["content"]
            return render_template("update.html",form = form)
    else:
        form = ArticleForm(request.form)
        newtitle=form.title.data
        newcategory=form.category.data
        newcontent = form.content.data
        sorgu2="Update makale Set title = %s, category=%s, content = %s where id=%s"
        cursor= mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle,newcategory,newcontent,id))
        mysql.connection.commit()
        flash("Makale Başarılı bir şekilde güncellendi.","success")
        return redirect(url_for("dashboard"))
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ =="__main__":
    app.run(debug = True)