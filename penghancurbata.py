import tkinter as tk


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#00ffcc', outline='#ffffff')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#ff007f', outline='#ffffff')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#ff4757', 2: '#2ed573', 3: '#ffa502'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline='#2f3542', tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.level = 1  # <--- TAHAP 5: Variabel Level Game
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#1e1e2f',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()

        self.hud_score = None
        self.hud_lives = None
        self.hud_level = None  # <--- TAHAP 5
        
        self.setup_game()
        self.canvas.focus_set()
        
        # Kontrol Panah & A/D
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-12))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(12))
        self.canvas.bind('a', lambda _: self.paddle.move(-12))
        self.canvas.bind('d', lambda _: self.paddle.move(12))

    def create_bricks(self):
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(300, 200, 'Press Space to start', 25, '#00ffcc')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.ball.speed = 9 + (self.level - 1) * 2  # <--- TAHAP 5: Bola makin cepat tiap level naik
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=40, color='white'):
        font = ('Helvetica', size, 'bold')
        return self.canvas.create_text(x, y, text=text, font=font, fill=color)

    def update_hud(self):
        score_text = f'Score: {self.score}'
        lives_text = f'Lives: {self.lives}'
        level_text = f'Level: {self.level}'  # <--- TAHAP 5
        
        if self.hud_score is None:
            self.hud_score = self.draw_text(60, 20, score_text, 12, '#ffffff')
            self.hud_level = self.draw_text(self.width / 2, 20, level_text, 12, '#ffa502')
            self.hud_lives = self.draw_text(self.width - 60, 20, lives_text, 12, '#ffffff')
        else:
            self.canvas.itemconfig(self.hud_score, text=score_text)
            self.canvas.itemconfig(self.hud_level, text=level_text)
            self.canvas.itemconfig(self.hud_lives, text=lives_text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        
        # TAHAP 5: Logika Naik Level jika semua brick habis
        if num_bricks == 0:
            self.ball.speed = 0
            self.level += 1
            self.score += 200  # Bonus clear level
            self.draw_text(300, 200, f'LEVEL {self.level} START!', 30, '#2ed573')
            self.after(2000, self.next_level)
            
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = 0
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'Game Over!', 40, '#ff4757')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(40, self.game_loop)

    def next_level(self):  # <--- TAHAP 5: Reset arena untuk level berikutnya
        self.canvas.delete('all')
        self.items = {}
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()
        self.hud_score = None
        self.hud_lives = None
        self.hud_level = None
        self.setup_game()

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        if not ball_coords:
            return
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 10
                
        self.ball.clone = objects
        self.ball.collide(objects)
        self.update_hud()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modified Brick Breaker - Arcade')
    game = Game(root)
    game.mainloop()