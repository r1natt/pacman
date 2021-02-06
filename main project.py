import pygame
import sys
import os
import random

WINDOW_SIZE = WIDTH, HEIGHT = 475, 550  # размер поля (19, 22), размер клетки 25
TICK = pygame.USEREVENT + 1  # событие, нужно для отсчета одного момента
PACMAN_MOTION = pygame.USEREVENT + 1  # событие для отсчета смены кадра


class Pacman(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()
        self.retset = set()  # множество для записи допустимых кнопок
        self.width = 19  # ширина поля
        self.height = 22  # высота поля
        self.screen = screen  # поверхность, на которой все выводим

        self.y = 12  # координаты пакмана во вложенном списке
        self.x = 9  # нужен для метода create_pacman в классе Pacman
        self.PacmanCurrentPos = (225, 300)  # сохраняет позицию пакмана, (225, 300) - позиция в начале игры в пикселях

        self.all_sprites = pygame.sprite.Group()
        self.main_pacman_sprite = pygame.sprite.Sprite()
        self.main_pacman_sprite.image = pygame.image.load('data/pacmanleft.png')
        self.main_pacman_sprite.rect = self.main_pacman_sprite.image.get_rect()
        self.main_pacman_sprite.add(self.all_sprites)
        self.main_pacman_sprite.rect.x = self.PacmanCurrentPos[0]
        self.main_pacman_sprite.rect.y = self.PacmanCurrentPos[1]
        pygame.display.flip()

        self.currentkey = 0
        self.count = 0

        self.left = 0  # отступ с левого верхнего края по оси x (пока нет счета очков, будет 0)
        self.top = 0  # отступ с левого верхнего края по оси y (пока нет счета очков, будет 0)
        self.cell_size = 25  # размер клетки в пикселях

        self.nodes_pos = set()

        self.board = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 4, 0, 0, 3, 0, 0, 0, 3, 1, 3, 0, 0, 0, 3, 0, 0, 4, 1],
                      [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
                      [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
                      [1, 3, 0, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 3, 0, 0, 3, 1],
                      [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                      [1, 3, 0, 0, 3, 1, 3, 0, 3, 1, 3, 0, 3, 1, 3, 0, 0, 3, 1],
                      [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
                      [1, 3, 3, 1, 0, 1, 3, 0, 3, 0, 3, 0, 3, 1, 0, 1, 3, 3, 1],
                      [1, 1, 0, 1, 0, 1, 0, 1, 2, 2, 2, 1, 0, 1, 0, 1, 0, 1, 1],
                      [1, 3, 3, 3, 3, 3, 3, 1, 5, 5, 5, 1, 3, 3, 3, 3, 3, 3, 1],
                      [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                      [1, 0, 1, 3, 3, 1, 3, 0, 0, 0, 0, 0, 3, 1, 3, 3, 1, 0, 1],
                      [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
                      [1, 3, 0, 0, 3, 0, 0, 0, 3, 1, 3, 0, 0, 0, 3, 3, 0, 3, 1],
                      [1, 0, 1, 1, 0, 1, 1, 1, 3, 1, 3, 1, 1, 1, 0, 1, 1, 0, 1],
                      [1, 3, 3, 1, 3, 3, 3, 0, 0, 0, 0, 0, 3, 3, 3, 1, 3, 3, 1],
                      [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
                      [1, 3, 3, 0, 3, 1, 3, 0, 3, 1, 3, 0, 3, 1, 3, 0, 3, 3, 1],
                      [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
                      [1, 4, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 4, 1],
                      [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        # 0 - клетка, по которой можно ходить,
        # 1 - стена
        # 2 - стенка выхода привидений
        # 3 - узел, расходжение путей

    def render(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 0:
                    pygame.draw.rect(self.screen, (0, 0, 0), (x * self.cell_size + self.left,
                                                              y * self.cell_size + self.top,
                                                              self.cell_size, self.cell_size), width=0)
                if self.board[y][x] == 1:
                    pygame.draw.rect(self.screen, (0, 0, 128), (x * self.cell_size + self.left,
                                                                y * self.cell_size + self.top,
                                                                self.cell_size, self.cell_size), width=0)
                if self.board[y][x] == 2:
                    pygame.draw.rect(self.screen, (252, 15, 192), (x * self.cell_size + self.left,
                                                                   y * self.cell_size + self.top,
                                                                   self.cell_size, self.cell_size), width=0)
                """if self.board[y][x] == 3:
                    pygame.draw.rect(self.screen, (26, 185, 192), (x * self.cell_size + self.left,
                                                                   y * self.cell_size + self.top,
                                                                   self.cell_size, self.cell_size), width=0)"""

    def nodes(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.board[y][x] == 3:
                    self.nodes_pos.add((x, y))

    def pacman_movement(self, key, cy, cx):  # key - проверяемый ход WASD в виде кода кнопок, (y, x) - координата клетки
        y = (cy - self.top) // self.cell_size
        x = (cx - self.left) // self.cell_size
        self.retset = set()

        horkeycheck = (key == 97 or key == 100)
        verkeycheck = (key == 119 or key == 115)
        ycellcheck = (cy - self.top) % self.cell_size == 0
        xcellcheck = (cx - self.top) % self.cell_size == 0

        if (horkeycheck and ycellcheck) or (verkeycheck and xcellcheck):
            if (self.board[y][(cx - self.left + 26) // self.cell_size] != 1 and
                     self.board[y][(cx - self.left + 26) // self.cell_size] != 2):  # проверяем есть ли ход справа
                self.retset.add(100)  # добавляем код кнопки D, если ход есть
            if (self.board[(cy - self.left + 26) // self.cell_size][x] != 1 and
                     self.board[(cy - self.left + 26) // self.cell_size][x] != 2):  # проверяем есть ли ход снизу
                self.retset.add(115)  # добавляем код кнопки S, если ход есть
            if (self.board[y][(cx - self.left - 1) // self.cell_size] != 1 and
                     self.board[y][(cx - self.left - 1) // self.cell_size] != 2):  # проверяем есть ли ход слева
                self.retset.add(97)  # добавляем код кнопки A, если ход есть
            if (self.board[(cy - self.left - 1) // self.cell_size][x] != 1 and
                     self.board[(cy - self.left - 1) // self.cell_size][x] != 2):  # проверяем есть ли ход сверху
                self.retset.add(119)  # добавляем код кнопки W, если ход есть

            if key in self.retset:  # проверяем допустим ли наш ход WASD
                self.currentkey = key
                pacman.pacman_move(key)  # вызываем метод самого движения
        else:
            pacman.pacman_move(self.currentkey)

    def motion_counting(self):
        self.count = (self.count + 1) % 3

    def pacman_move(self, key):
        left = {0: 'data/pcmcirc.png', 1: 'data/pcmedleft.png', 2: 'data/pacmanleft.png'}
        down = {0: 'data/pcmcirc.png', 1: 'data/pcmeddown.png', 2: 'data/pcmdown.png'}
        right = {0: 'data/pcmcirc.png', 1: 'data/pcmedright.png', 2: 'data/pcmright.png'}
        up = {0: 'data/pcmcirc.png', 1: 'data/pcmedup.png', 2: 'data/pcmup.png'}
        if key == 97:  # A
            x = (self.PacmanCurrentPos[0] - 1 - self.left) // self.cell_size
            y = (self.PacmanCurrentPos[1] - self.left) // self.cell_size
            # print(x, y, self.board[y][x], self.PacmanCurrentPos)
            if self.board[y][x] != 1 and self.board[y][x] != 2:
                pygame.draw.rect(self.screen, (0, 0, 0), (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1],
                                                          self.cell_size, self.cell_size), width=0)
                self.PacmanCurrentPos = (self.PacmanCurrentPos[0] - 1, self.PacmanCurrentPos[1])
                self.main_pacman_sprite.rect.x = self.PacmanCurrentPos[0]
                self.main_pacman_sprite.rect.y = self.PacmanCurrentPos[1]
                print(self.main_pacman_sprite.rect)
                self.main_pacman_sprite.image = pygame.image.load(left[self.count])
                self.all_sprites.draw(screen)
                pygame.display.flip()
        elif key == 115:  # S
            x = (self.PacmanCurrentPos[0] - self.left) // self.cell_size
            y = (self.PacmanCurrentPos[1] + 1 - self.left) // self.cell_size
            # print(x, y, self.board[y][x], self.PacmanCurrentPos)
            if self.board[y][x] != 1 and self.board[y][x] != 2:
                pygame.draw.rect(self.screen, (0, 0, 0), (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1],
                                                          self.cell_size, self.cell_size), width=0)
                self.PacmanCurrentPos = (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1] + 1)
                self.main_pacman_sprite.rect.x = self.PacmanCurrentPos[0]
                self.main_pacman_sprite.rect.y = self.PacmanCurrentPos[1]
                print(self.main_pacman_sprite.rect)
                self.main_pacman_sprite.image = pygame.image.load(down[self.count])
                self.all_sprites.draw(screen)
                pygame.display.flip()
        elif key == 100:  # D
            x = (self.PacmanCurrentPos[0] + 1 - self.left) // self.cell_size
            y = (self.PacmanCurrentPos[1] - self.left) // self.cell_size
            # print(x, y, self.board[y][x], self.PacmanCurrentPos)
            if self.board[y][x] != 1 and self.board[y][x] != 2:
                pygame.draw.rect(self.screen, (0, 0, 0), (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1],
                                                          self.cell_size, self.cell_size), width=0)
                self.PacmanCurrentPos = (self.PacmanCurrentPos[0] + 1, self.PacmanCurrentPos[1])
                self.main_pacman_sprite.rect.x = self.PacmanCurrentPos[0]
                self.main_pacman_sprite.rect.y = self.PacmanCurrentPos[1]
                print(self.main_pacman_sprite.rect)
                self.main_pacman_sprite.image = pygame.image.load(right[self.count])
                self.all_sprites.draw(screen)
                pygame.display.flip()
        elif key == 119:  # W
            x = (self.PacmanCurrentPos[0] - self.left) // self.cell_size
            y = (self.PacmanCurrentPos[1] - 1 - self.left) // self.cell_size
            # print(x, y, self.board[y][x], self.PacmanCurrentPos)
            if self.board[y][x] != 1 and self.board[y][x] != 2:
                pygame.draw.rect(self.screen, (0, 0, 0), (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1],
                                                          self.cell_size, self.cell_size), width=0)
                self.PacmanCurrentPos = (self.PacmanCurrentPos[0], self.PacmanCurrentPos[1] - 1)
                self.main_pacman_sprite.rect.x = self.PacmanCurrentPos[0]
                self.main_pacman_sprite.rect.y = self.PacmanCurrentPos[1]
                print(self.main_pacman_sprite.rect)
                self.main_pacman_sprite.image = pygame.image.load(up[self.count])
                self.all_sprites.draw(screen)
                pygame.display.flip()

    def pacman_pos(self):
        return self.PacmanCurrentPos


class Dots(Pacman, pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen = screen
        self.dots = pygame.sprite.Group()
        self.dotcount = 0

    def dot_update(self):
        sprite = pygame.sprite.spritecollide(self.main_pacman_sprite, self.dots, True)

    def first_render_dots(self):
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x] == 0 or self.board[y][x] == 3:
                    self.dot = pygame.sprite.Sprite()
                    self.dot.image = pygame.image.load('data/dot.png')
                    self.dot.rect = self.dot.image.get_rect()
                    self.dot.add(self.dots)

                    self.dot.rect.x = x * self.cell_size + self.left + 10
                    self.dot.rect.y = y * self.cell_size + self.top + 10
                    self.dots.draw(self.screen)
                    pygame.display.flip()

    def render_dots(self):
        self.dots.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    pygame.time.set_timer(TICK, 15)
    pygame.time.set_timer(PACMAN_MOTION, 50)
    running = True

    pacman = Pacman(screen)  # передаем только поверхность, потому что размеры известны
    pacman.render()
    pacman.nodes()
    pygame.display.flip()
    PacmanCurrentKey = ''
    dot = Dots(screen)
    dot.first_render_dots()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:  # проверка по кнопкам ASDW
                pacman_cur_pos = pacman.pacman_pos()  # получаем координаты в реальном времени
                if event.key == 97:  # проверяем A
                    PacmanCurrentKey = 97
                    pacman.pacman_movement(97, pacman_cur_pos[1], pacman_cur_pos[0])
                    # вызов метода проверки возможности хода
                if event.key == 115:  # проверяем S
                    PacmanCurrentKey = 115
                    pacman.pacman_movement(115, pacman_cur_pos[1], pacman_cur_pos[0])
                    # вызов метода проверки возможности хода
                if event.key == 100:  # проверяем D
                    PacmanCurrentKey = 100
                    pacman.pacman_movement(100, pacman_cur_pos[1], pacman_cur_pos[0])
                    # вызов метода проверки возможности хода
                if event.key == 119:  # проверяем W
                    PacmanCurrentKey = 119
                    pacman.pacman_movement(119, pacman_cur_pos[1], pacman_cur_pos[0])
                    # вызов метода проверки возможности хода
            if event.type == TICK:
                pacman_cur_pos = pacman.pacman_pos()
                dot.dot_update()
                dot.render_dots()
                pacman.pacman_movement(PacmanCurrentKey, pacman_cur_pos[1], pacman_cur_pos[0])
            if event.type == PACMAN_MOTION:
                pacman.motion_counting()
        pygame.display.flip()
    pygame.quit()
