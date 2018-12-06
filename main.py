from flask import Flask, render_template, request, jsonify
from flask_restful import Resource, Api, reqparse

# アプリケーションを作成
app = Flask(__name__)
api = Api(app)


@app.route('/', methods=['GET', 'POST'])
def top():
    return render_template("index.html")


class Dajare(object):
    def check_dajare(self, text):
        if len(text) > 3:
            res = "dajare"
        else:
            res = "dareja"
        return res


class DajareCheck(Resource):
    def get(self):
        # getを取得
        dajare = Dajare()
        data = request.json
        text = data.get("text")

        if text == "" or text is None:
            is_dajare = "unknown"

        else:
            # ダジャレ評価
            is_dajare = dajare.check_dajare(text)

        # 出力を整形
        res = {'is_dajare':is_dajare}

        return jsonify(res)

    def post(self):
        pass


api.add_resource(DajareCheck, '/isdajare')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)