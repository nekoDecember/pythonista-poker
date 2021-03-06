from scene import *
import random


class MyScene(Scene):
    def setup(self):
        # 交換回数
        self.change_num = 3
        # オブジェクト初期設定
        self.setup_object()
        # カードゲーム初期設定
        self.reset_game()

    def touch_began(self, touch):
        # タップした位置の取得
        touch_loc = self.point_from_scene(touch.location)

        if touch_loc in self.button.frame:
            self.button.texture = Texture('pzl:Button2')
            if self.game == 'pause':
                self.reset_game()
            elif self.game == 'run':
                # カード交換
                for i, item in enumerate(self.items):
                    if item.reverse == True:
                        self.change_card(i)

                self.change_count += 1
                if self.change_count == self.change_num:
                    self.button_label.text = 'New Game'
                    self.game = 'pause'

                    # 役の更新
                    self.hand_label.text = 'GAME OVER\n結果:' + self.tg.check_poker_hand()
                    self.description_label.text = ''

                    self.hand_label.position = (self.size.w / 2, self.size.h - 270)
                else:
                    self.update_text()

            else:
                self.reset_draw_cards()
                self.game = 'run'
                self.button_label.text = 'Change'

                self.update_text()

        if self.game == 'run':
            # カードをひっくり返す
            for i, item in enumerate(self.items):
                if touch_loc in item.frame:
                    self.set_item(i, 'reverse')

    def touch_ended(self, touch):
        self.button.texture = Texture('pzl:Button1')

    # カードを画面表示するためのセットアップ
    def set_item(self, id, direction=None):
        item = self.items[id]
        card = self.tg.draw_cards[id]
        # 引数指定時は書き換え
        if direction is not None:
            # 表にする
            if direction == 'front':
                item.texture = Texture('card:' + card['string'])
                item.reverse = False
            # ひっくり返す
            elif direction == 'reverse':
                if item.reverse == True:
                    item.texture = Texture('card:' + card['string'])
                    item.reverse = False
                else:
                    item.texture = Texture('card:BackRed1')
                    item.reverse = True
            # 裏にする
            else:
                item.texture = Texture('card:BackRed1')
                item.reverse = True
        item.anchor_point = (0.5, 0)
        self.resize_item(item)

    def setup_object(self):
        # バックグラウンド設定
        self.background_color = '#004f82'
        ground = Node(parent=self)

        # 役の表示
        hand_font = ('Futura', 30)
        self.hand_label = LabelNode('', hand_font, parent=self)
        self.hand_label.position = (self.size.w / 2, self.size.h - 70)
        self.hand_label.z_position = 1

        # ボタン
        self.button = SpriteNode('pzl:Button1', position=(self.size.w / 2, 300))
        self.add_child(self.button)

        button_font = ('Futura', 30)
        self.button_label = LabelNode('Start', button_font, parent=self, color='black')
        self.button_label.position = (self.size.w / 2, 305)
        self.button_label.z_position = 1

        # 残り回数を表示する
        description_font = ('Futura', 30)
        self.description_label = LabelNode('', description_font, parent=self)
        self.description_label.position = (self.size.w / 2, 200)
        self.description_label.z_position = 1

        self.items = []
        self.tg = TrumpGame()
        # カードの初期設定
        for i in range(0, 5):
            item = SpriteNode()
            self.items.append(item)
            self.add_child(item)
            item.position = (50 + i * 70, 350)

    def reset_game(self, initial_setting=False):

        # 交換回数カウント
        self.change_count = 0

        self.game = 'standby'
        self.button_label.text = 'Start'

        # 役の更新
        self.hand_label.text = ''
        self.hand_label.position = (self.size.w / 2, self.size.h - 70)

        self.reset_draw_cards()
        for i in range(0, 5):
            self.set_item(i, 'back')

    def update_text(self):
        # 役の更新
        self.hand_label.text = self.tg.check_poker_hand()

        # 回数の更新
        remaining = self.change_num - self.change_count
        self.description_label.text = 'あと' + str(remaining) + '回交換できます。'

    # カードの交換処理の作成
    def change_card(self, id):
        self.tg.change_card(id)
        self.set_item(id, 'front')

    # カードを5枚引く処理
    def reset_draw_cards(self):
        self.tg.reset_draw_cards(5)
        for i, card in enumerate(self.tg.draw_cards):
            self.set_item(i, 'front')

    # サイズ調整
    def resize_item(self, item):
        item.size = (65, 87)


class TrumpGame:
    def make_card_list(self):
        # マークのリスト
        symbol_list = ['Clubs', 'Hearts', 'Spades', 'Diamonds']
        # カードリスト
        card_list = []

        # カードのデータを作成
        for symbol in symbol_list:
            for number in range(1, 14):
                card = {
                    'number': number,
                    'symbol': symbol
                }
                # マークと数字を合体させる
                # 11以上と1は置き換え
                if number == 1:
                    card['string'] = symbol + 'A'
                elif number == 11:
                    card['string'] = symbol + 'J'
                elif number == 12:
                    card['string'] = symbol + 'Q'
                elif number == 13:
                    card['string'] = symbol + 'K'
                else:
                    # 10以下ならそのまま
                    card['string'] = symbol + str(number)

                # カードをリストに追加
                card_list.append(card)

        # ジョーカーの追加
        joker = {
            'number': 99,
            'symbol': 'Joker',
            'string': 'Joker'
        }
        card_list.append(joker)

        self.card_list = card_list

    def shuffle(self):
        # カードをシャッフルする
        random.shuffle(self.card_list)

    # 手札を作成する
    def reset_draw_cards(self, number):
        card_list = self.make_card_list()
        self.shuffle()
        self.draw_cards = []

        for i in range(0, number):
            self.draw_cards.append(
                self.card_list.pop(0)
            )

    # カード交換
    def change_card(self, id):
        self.draw_cards[id] = self.card_list.pop(0)

    # 役のチェック処理
    def check_poker_hand(self):
        # ペア数
        pair_count = 0
        # 同じ数字のカウント
        match_count = 0
        # 同じ数字の枚数(3カード,4カードチェック用)
        match_number = 0
        # フラッシュカウント
        flash_count = 0
        # ストレートカウント
        straight_count = 0

        royal_flg = False

        # 数字の昇順に並び替える
        cards = sorted(self.draw_cards, key=lambda x: x['number'])

        # チェックループ
        for i in range(1, 5):
            # 前の数字が同じかチェック
            if cards[i]['number'] == cards[i - 1]['number']:
                match_count += 1
                # 最終ループチェック
                if i == 4:
                    if match_count == 1:
                        pair_count += 1
                    # 3カード以上の場合
                    elif match_count > 1:
                        match_number = match_count + 1
            else:
                # 違う数字の場合
                if match_count == 1:
                    pair_count += 1
                # 3カード以上の場合
                elif match_count > 1:
                    match_number = match_count + 1
                match_count = 0
            # 同じマークが続いているかチェック
            if cards[i]['symbol'] == cards[i - 1]['symbol']:
                flash_count += 1
            # 数字が連続しているかチェック
            if cards[i]['number'] == cards[i - 1]['number'] + 1:
                straight_count += 1
            else:
                if cards[i]['number'] == 10 and cards[i - 1]['number'] == 1:
                    straight_count += 1

        # ジョーカーチェック
        joker_flg = cards[4]['string'] == 'Joker'
        if joker_flg:
            # フラッシュは一律カウントアップ
            flash_count += 1
            # 3カード,4カードの場合
            if match_number >= 3:
                # 3カードを4カード、4カードを5カードへ
                match_number += 1
            # ペアのチェック(ストレートより先にチェックする)
            elif pair_count > 0:
                # ペアを3カードに昇格
                pair_count -= 1
                match_number = 3
            # ストレートチェック1
            elif straight_count == 3:
                straight_count += 1
                # このパターンは必ず10,J,Q,Kなのでジョーカーを加えるとロイヤルフラグ確定
                if cards[0]['number'] == 10:
                    straight_count = 4
                    royal_flg = True
                # 13がないケース
                elif cards[0]['number'] == 1 and cards[1]['number'] == 10 and cards[3]['number'] == 12:
                    straight_count = 4
                    royal_flg = True
            # ストレートチェック2
            elif straight_count == 2:
                # 4以下ならストレートが成立
                if cards[3]['number'] - cards[0]['number'] <= 4:
                    straight_count = 4

                # ロイヤルの並びのチェック
                elif cards[0]['number'] == 1 and cards[1]['number'] == 10 and cards[3]['number'] == 13:
                    straight_count = 4
                    royal_flg = True
                # 10がない場合
                elif cards[0]['number'] == 1 and cards[1]['number'] == 11 and cards[3]['number'] == 13:
                    straight_count = 4
                    royal_flg = True

        # 最終手札チェック
        if straight_count == 4 and flash_count == 4:
            if cards[0]['number'] == 1 and cards[4]['number'] == 13 or royal_flg == True:
                # ロイヤルストレートフラッシュ
                hand = 'ロイヤル\nストレートフラッシュ'
            else:
                # ストレートフラッシュ
                hand = 'ストレートフラッシュ'
        elif match_number > 2:
            if match_number == 5:
                # 5カード
                hand = '5カード'
            elif match_number == 4:
                # 4カード
                hand = '4カード'
            else:
                if pair_count > 0:
                    # フルハウス
                    hand = 'フルハウス'
                else:
                    # 3カード
                    hand = '3カード'
        elif flash_count == 4:
            # フラッシュ
            hand = 'フラッシュ'
        elif straight_count == 4:
            # ストレート
            hand = 'ストレート'
        elif pair_count > 0:
            if pair_count > 1:
                # 2ペア
                hand = '2ペア'
            else:
                # 1ペア
                hand = '1ペア'
        elif joker_flg:
            hand = 'ジョーカー'
        else:
            # なし
            hand = 'ぶた'

        return hand


if __name__ == '__main__':
    run(MyScene(), show_fps=False)