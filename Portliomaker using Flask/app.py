from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/portfolio", methods=["POST"])
def portfolio():
    user_data = {
        "name": request.form["name"],
        "bio": request.form["bio"],
        "school": request.form["school"],
        "college": request.form["college"],
        "github": request.form["github"],
        "instagram": request.form["instagram"],
        "youtube": request.form["youtube"],
    }
    return render_template("portfolio.html", user=user_data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    success_message = None
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        print(f"New Message from {name} ({email}): {message}")
        success_message = "Thank you! Your message has been sent."
    return render_template("contact.html", success_message=success_message)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
