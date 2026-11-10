import tkinter as tk
import random


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


class Particle(GameObject):
    """Efek partikel kecil saat brick hancur"""
    def __init__(self, canvas, x, y, color):
        size = random.randint(3, 6)
        item = canvas.create_oval(x, y, x + size, y + size, fill=color, outline='')
        super(Particle, self).__init__(canvas, item)
        self.dx = random.uniform(-4, 4)
        self.dy = random.uniform(-4, 4)
        self.lifetime = 15

    def update(self):
        self.move(self.dx, self.dy)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.delete()
            return False
        return True


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 9
        self.direction = [1, -1]
        self.speed = 7  # Disesuaikan agar lebih smooth dengan frame rate cepat
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='#ffffff', outline='#800020', width=2)
        super(Ball, self).__init__(canvas, item)
        self.trail_coords = []

    def update(self):
        coords = self.get_position()
        if not coords:
            return
            
        # Simpan jejak untuk efek trail tipis
        self.trail_coords.append((coords[0], coords[1], coords[2], coords[3]))
        if len(self.trail_coords) > 5:
            self.trail_coords.pop(0)

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
        if not coords:
            return
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            obj_coords = game_object.get_position()
            if obj_coords:
                if x > obj_coords[2]:
                    self.direction[0] = 1
                elif x < obj_coords[0]:
                    self.direction[0] = -1
                else:
                    self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 90
        self.height = 12
        self.ball = None
        # Warna Maroon elegan dengan outline putih
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#800020', outline='#ffffff', width=1)
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        if not coords:
            return
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    # Palet tema Maroon, Merah Hati, dan Putih
    COLORS = {1: '#5a0015', 2: '#800020', 3: '#b3002d'}

    def __init__(self, canvas, x, y, hits, game_instance):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.game_instance = game_instance
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline='#ffffff', width=1, tags='brick')
        super(Brick, self).__init__(canvas, item)
        self.x_center = x
        self.y_center = y

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            # Spawn efek partikel saat hancur
            for _ in range(6):
                p = Particle(self.canvas, self.x_center, self.y_center, '#ff4d4d')
                self.game_instance.particles.append(p)
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.level = 1
        self.width = 610
        self.height = 400
        
        # Background Hitam Pekat (#0a0a0a) khas aksen gelap
        self.canvas = tk.Canvas(self, bg='#0a0a0a',
                                width=self.width,
                                height=self.height,
                                highlightthickness=0)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.particles = []
        self.trail_items = []
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()

        self.hud_score = None
        self.hud_lives = None
        self.hud_level = None
        
        self.setup_game()
        self.canvas.focus_set()
        
        # Kontrol Responsif (Panah & A/D)
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-15))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(15))
        self.canvas.bind('a', lambda _: self.paddle.move(-15))
        self.canvas.bind('d', lambda _: self.paddle.move(15))

    def create_bricks(self):
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 75, 2)
            self.add_brick(x + 37.5, 100, 1)

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(300, 200, 'Press Space to Start', 22, '#ffffff')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        if paddle_coords:
            x = (paddle_coords[0] + paddle_coords[2]) * 0.5
            self.ball = Ball(self.canvas, x, 345)
            self.ball.speed = 6 + (self.level - 1) * 1.5
            self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits, self)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size=40, color='white'):
        font = ('Helvetica', size, 'bold')
        return self.canvas.create_text(x, y, text=text, font=font, fill=color)

    def update_hud(self):
        score_text = f'Score: {self.score}'
        lives_text = f'Lives: {self.lives}'
        level_text = f'Level: {self.level}'
        
        if self.hud_score is None:
            self.hud_score = self.draw_text(65, 20, score_text, 12, '#ffffff')
            self.hud_level = self.draw_text(self.width / 2, 20, level_text, 12, '#b3002d')
            self.hud_lives = self.draw_text(self.width - 65, 20, lives_text, 12, '#ffffff')
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
        
        # Update partikel hancur
        self.particles = [p for p in self.particles if p.update()]
        
        # Render efek trail bola tipis-tipis
        for t in self.trail_items:
            self.canvas.delete(t)
        self.trail_items = []
        if self.ball:
            for coords in self.ball.trail_coords[:-1]:
                t_item = self.canvas.create_oval(coords[0], coords[1], coords[2], coords[3],
                                                 fill='#33000d', outline='')
                self.trail_items.append(t_item)

        num_bricks = len(self.canvas.find_withtag('brick'))
        
        if num_bricks == 0:
            if self.ball:
                self.ball.speed = 0
            self.level += 1
            self.score += 250
            self.draw_text(300, 200, f'LEVEL {self.level} READY', 28, '#ffffff')
            self.after(2000, self.next_level)
            
        elif self.ball and self.ball.get_position() and self.ball.get_position()[3] >= self.height:
            self.ball.speed = 0
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'GAME OVER', 36, '#b3002d')
            else:
                self.after(1000, self.setup_game)
        else:
            if self.ball:
                self.ball.update()
            # Diubah ke 20ms agar animasi pergerakan jauh lebih fluid dan smooth
            self.after(20, self.game_loop)

    def next_level(self):
        self.canvas.delete('all')
        self.items = {}
        self.particles = []
        self.trail_items = []
        self.paddle = Paddle(self.canvas, self.width / 2, 360)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()
        self.hud_score = None
        self.hud_lives = None
        self.hud_level = None
        self.setup_game()

    def check_collisions(self):
        if not self.ball:
            return
        ball_coords = self.ball.get_position()
        if not ball_coords:
            return
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 15
                
        self.ball.collide(objects)
        self.update_hud()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Modified Brick Breaker - Dark Maroon Edition')
    game = Game(root)
    game.mainloop()