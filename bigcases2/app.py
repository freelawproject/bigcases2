from flask import Flask, request, Response, render_template

# from courtlistener import cl_webhook

app = Flask(__name__)


@app.route("/")
def hello_world():
    app.logger.debug("Visitor to /.")
    num_cases = 234
    # return "<p>Nothing to see here. Move along!</p>"
    return render_template("home.html", num_cases=num_cases)


@app.route("/test/post", methods=["POST"])
def post_test():
    if request.method == "POST":
        return {"is_post": True}
    else:
        return "Nope"
