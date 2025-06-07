import tkinter as tk
import random

WIDTH = 400
HEIGHT = 600
CAR_WIDTH = 50
CAR_HEIGHT = 90
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 90
SPEED_INCREMENT = 2

class CarRacingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Racing Game")

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="gray")
        self.canvas.pack()

        self.car = self.canvas.create_rectangle(
            WIDTH//2 - CAR_WIDTH//2, HEIGHT - CAR_HEIGHT - 10,
            WIDTH//2 + CAR_WIDTH//2, HEIGHT - 10,
            fill="blue"
        )

        self.obstacles = []
        self.running = True
        self.score = 0
        self.speed = 10

        self.score_text = self.canvas.create_text(10, 10, anchor="nw", fill="white",
                                                  font=("Arial", 16), text="Score: 0")
        self.restart_button = tk.Button(root, text="Restart", font=("Arial", 14), command=self.restart_game)
        self.restart_window_button = self.canvas.create_window(WIDTH//2, HEIGHT//2 + 50, window=self.restart_button)
        self.canvas.itemconfigure(self.restart_window_button, state='hidden')

        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<Up>", self.speed_up)
        self.root.bind("<Down>", self.speed_down)

        self.spawn_obstacle()
        self.update()

    def spawn_obstacle(self):
        x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
        obs = self.canvas.create_rectangle(
            x, -OBSTACLE_HEIGHT, x + OBSTACLE_WIDTH, 0, fill="red"
        )
        self.obstacles.append(obs)

    def move_left(self, event):
        if self.running:
            self.canvas.move(self.car, -20, 0)

    def move_right(self, event):
        if self.running:
            self.canvas.move(self.car, 20, 0)

    def speed_up(self, event):
        if self.running:
            self.speed += SPEED_INCREMENT

    def speed_down(self, event):
        if self.running and self.speed > 2:
            self.speed -= SPEED_INCREMENT

    def update(self):
        if not self.running:
            return

        for obs in self.obstacles:
            self.canvas.move(obs, 0, self.speed)
            if self.canvas.coords(obs)[1] > HEIGHT:
                self.canvas.delete(obs)
                self.obstacles.remove(obs)
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        if random.randint(1, 30) == 1:
            self.spawn_obstacle()

        self.check_collision()

        if self.running:
            self.root.after(50, self.update)

    def check_collision(self):
        car_coords = self.canvas.coords(self.car)
        for obs in self.obstacles:
            if self.intersect(car_coords, self.canvas.coords(obs)):
                self.running = False
                self.canvas.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER", fill="white", font=("Arial", 24))
                self.canvas.itemconfigure(self.restart_window_button, state='normal')

    def intersect(self, box1, box2):
        x1, y1, x2, y2 = box1
        a1, b1, a2, b2 = box2
        return not (x2 < a1 or x1 > a2 or y2 < b1 or y1 > b2)

    def restart_game(self):
        self.canvas.delete("all")
        self.car = self.canvas.create_rectangle(
            WIDTH//2 - CAR_WIDTH//2, HEIGHT - CAR_HEIGHT - 10,
            WIDTH//2 + CAR_WIDTH//2, HEIGHT - 10,
            fill="blue"
        )
        self.obstacles.clear()
        self.running = True
        self.score = 0
        self.speed = 10
        self.score_text = self.canvas.create_text(10, 10, anchor="nw", fill="white",
                                                  font=("Arial", 16), text="Score: 0")
        self.restart_window_button = self.canvas.create_window(WIDTH//2, HEIGHT//2 + 50, window=self.restart_button)
        self.canvas.itemconfigure(self.restart_window_button, state='hidden')

# Run the game
root = tk.Tk()
game = CarRacingGame(root)
root.mainloop()
