# Imports & Config 
import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env  

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# Login required
# Requires login for enhanced functionality 
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user" in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged to proceed!")
            return redirect(url_for("login"))
    return wrap


# Define homepage / login option 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = existing_user()

        if user:
            if password_is_valid(user):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back to the community, {}".format(request.form.get("username")))
                return redirect(url_for("personal", username=session["user"]))

            flash("Sorry, this Username and/or Password is incorrect")
            return redirect(url_for("login"))

        flash("Oops, this Username and/or Password is incorrect")
        return redirect(url_for("login"))
        
    return render_template("user/login.html")

# Define homepage / index option 
@app.route("/")
def index():
    return render_template("index.html")


# Define homepage / about option 
@app.route("/about")
def about():
    return render_template("about.html")


#  Define homepage / recipes option 
@app.route("/recipes")
def recipes():
    recipes = list(mongo.db.recipes.find().sort("id"), -1)
    return render_template("recipe/recipes.html")


# Standalone recipe page 
@app.route("/recipe/<recipe_id>")
def specific_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipes/single_recipe.html", recipe=recipe)


# Define homepage / register option 
@app.route("/register")
def register():
    return render_template("user/register.html")



# Recipe search functionality
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipes/recipes.html", recipes=recipes)


@app.route("/recipe/<recipe_id>")
def single_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template("recipes/single_recipe.html", recipe=recipe)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)