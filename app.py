import os
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/recipes")
def recipes():
    return render_template("recipe/recipes.html")


@app.route("/register")
def register():
    return render_template("user/register.html")


@app.route("/login")
def login():
    return render_template("user/login.html")


@app.route("/recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find().sort("_id", -1))
    return render_template("recipes/recipes.html", recipes=recipes)


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