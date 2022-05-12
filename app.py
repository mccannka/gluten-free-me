import os
from flask import Flask, render_template


app = Flask(__name__)


#-------- Login ---------
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user" in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in for this part of the site!")
            return redirect(url_for("login"))
    return wrap


#-------- Homepage ---------
@app.route("/")
def index():
    return render_template("index.html")

 #-------- About --------- 
@app.route("/about")
def about():
    return render_template("about.html")


#-------- Add Recipe ---------
@app.route("/recipe/add", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        recipe = display_recipes(request)
        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe is added successfully")
        return redirect(url_for("personal", username=session["user"]))
    return render_template("recipes/add_recipe.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)