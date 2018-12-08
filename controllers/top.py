from flask import render_template, Blueprint, request

# lueprintオブジェクトを生成します
app = Blueprint('top', __name__)

@app.route('/', methods=['GET', 'POST'])
def top():
    return render_template("index.html")


@app.route('/dajare_post', methods=['POST'])
def post():
    """
    ダジャレを入力
    :return:
    """
    dajare_text = request.form.get('dajare_text')

    return render_template("dajaresult.html", dajare_text=dajare_text)