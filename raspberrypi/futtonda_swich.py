import RPi.GPIO as GPIO
import time
from janome.tokenizer import Tokenizer
import collections


# SG92Rをコントロールするための
class SG90_92R_Class:
    # コンストラクタ
    def __init__(self, pin, zero_offset_duty):
        self.mPin = pin
        self.m_ZeroOffsetDuty = zero_offset_duty

        # GPIOをPWMモードにする
        GPIO.setup(self.mPin, GPIO.OUT)
        self.mPwm = GPIO.PWM(self.mPin, 50) # set 20ms / 50 Hz

    # 位置セット
    def SetPos(self, pos):
        # Duty ratio = 2.5%〜12.0% : 0.5ms〜2.4ms : 0 ～ 180deg
        duty = (12-2.5)/180*pos+2.5 + self.m_ZeroOffsetDuty
        self.mPwm.start(duty)

    # 終了処理
    def Cleanup(self):
        # サーボを10degにセットしてから、インプットモードにしておく
        self.SetPos(90)
        time.sleep(1)
        GPIO.setup(self.mPin, GPIO.IN)

def identity_num(str):
    str_list = []
    for i in range(len(str)):
        str_list.append(str[i])
    num = len(collections.Counter(str_list))
    return num




# コントロール
if __name__ == '__main__':
    # Using GPIO No.  to identify channel
    GPIO.setmode(GPIO.BCM)
    Servo = SG90_92R_Class(pin=4, zero_offset_duty=0)

    # mecab = MeCab.Tagger("-Oyomi")
    t = Tokenizer()
    sentence = input("ダジャレを言いなしゃれ\n")


    try:
        while True:
            print('ダジャレをいいなしゃれ')
            dajare = input('>> ')
            '''独断と偏見の前処理'''
            tokens = t.tokenize(dajare)
            yomi = "".join([token.reading for token in tokens])
            # yomi = mecab.parse(dajare)
            yomi = yomi.replace('。、,.', '')
            yomi = yomi.replace('ッ', '')
            yomi = yomi.replace('ー', '')
            yomi = yomi.replace('ャ', 'ヤ')
            yomi = yomi.replace('ュ', 'ユ')
            yomi = yomi.replace('ョ', 'ヨ')

            '''n文字以上被っていたらダジャレ扱い'''
            n = 3

            '''だじゃれ文を1文字ずつずらしてn文字のパーツに分解してリスト化'''
            word_list = []
            repeat_num = len(yomi) - 1 - (n - 1)

            for i in range(repeat_num):
                word_list.append(yomi[i:i + n])

            '''自身以外の要素と一致する要素があればだじゃれと認定'''
            judgement = False

            for i, element in enumerate(word_list):
                for j in range(len(word_list)):
                    if i == j:
                        continue
                    elif element == word_list[j] and identity_num(element) != 1:
                        judgement = True
                    else:
                        continue

            if judgement:
                time.sleep(2)
                Servo.SetPos(0)
                time.sleep(0.5)
                Servo.SetPos(60)
                print("しゃれてんなぁ")
            else:
                print('なんて？')
    except KeyboardInterrupt: # Ctl+Cが押されたらループを終了
        print("\nCtl+C")
    except Exception as e:
        print(str(e))
    finally:
        Servo.Cleanup()
        GPIO.cleanup()
        print("\nexit program")