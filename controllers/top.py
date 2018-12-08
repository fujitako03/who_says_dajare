from flask import render_template, Blueprint, request
from controllers.dajarewake import Dajarewake

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
    # フォームからダジャレを取得
    dajare_text = request.form.get('dajare_text')

    # ダジャレ判定
    dj = Dajarewake(dajare_text)
    is_dajare = dj.dajarewake()
    wake_ans = "だじゃれじゃ" if is_dajare else "だじゃれじゃない"

    return render_template("dajaresult.html", dajare_text=dajare_text, wake_ans=wake_ans)