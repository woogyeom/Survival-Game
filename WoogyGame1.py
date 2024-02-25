import pygame
import random
import math
import sys
from pygame.locals import *

pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
TRANS = (0, 0, 0, 0)

screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.SysFont('Malgun Gothic', 20)
pygame.display.set_caption("Woogy Game")
clock = pygame.time.Clock()

regen_time = 5000 # ms
last_gen_time = pygame.time.get_ticks()
regen_mobs = 5

last_shot_time = pygame.time.get_ticks()

hit_inv_time = 500 # ms
last_hit_time = pygame.time.get_ticks()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.topleft = (390, 280)

        self.speed = 5
        self.attack_speed = 1

        self.maxhp = 100
        self.hp = 100
        self.lvl = 1
        self.exp = 0
        self.expcap = 5
        self.pickup = 50

        self.is_blinking = False
        self.blink_timer = 0
        self.blink_duration = 500

        self.score = 0

    def hit(self):
        if not self.is_blinking:
            self.is_blinking = True
            self.image.fill(ORANGE)
            self.blink_timer = pygame.time.get_ticks()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_a] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_d] and self.rect.x <= screen_width - self.rect.width:
            self.rect.x += self.speed
        if keys[K_w] and self.rect.y > 0:
            self.rect.y -= self.speed
        if keys[K_s] and self.rect.y <= screen_height - self.rect.height:
            self.rect.y += self.speed
        if self.is_blinking:
            elapsed_time = pygame.time.get_ticks() - self.blink_timer
            if elapsed_time >= self.blink_duration:
                self.image.fill(GREEN)
                self.is_blinking = False

class hud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # HP
        self.hp_image = pygame.Surface((40, 3))
        self.hp_image.fill(RED)
        self.hp_rect = self.hp_image.get_rect()

        # EXP
        self.exp_image = pygame.Surface((40, 3))
        self.exp_image.fill(CYAN)
        self.exp_rect = self.exp_image.get_rect()

        self.image = pygame.Surface((40, 8))
        self.image.fill(TRANS)

        self.image.blit(self.hp_image, (0, 0))
        self.image.blit(self.exp_image, (0, 5))

        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill(TRANS)
        player_x, player_y = player.rect.center

        # HP
        hp_new_width = max(0, 40 * player.hp / player.maxhp)
        self.hp_image = pygame.transform.scale(self.hp_image, (int(hp_new_width), 3))
        self.hp_image.fill(RED)
        self.hp_rect = self.hp_image.get_rect()
        self.hp_rect.center = (player_x, player_y - 30)

        #EXP
        exp_new_width = max(0, 40 * player.exp / player.expcap)
        self.exp_image = pygame.transform.scale(self.exp_image, (int(exp_new_width), 3))
        self.exp_image.fill(CYAN)
        self.exp_rect = self.exp_image.get_rect()
        self.exp_rect.center = (player_x, player_y - 25)

        #self.image.blit(self.hp_back_image, (0, 0))
        self.image.blit(self.hp_image, (0, 0))
        self.image.blit(self.exp_image, (0, 5))

        self.rect.midtop = player.rect.centerx, player.rect.top - 15

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        player_x, player_y = player.rect.center
        angle = random.uniform(0, 2 * math.pi)
        distance = max(screen_width, screen_height)
        self.rect.topleft = (
            player_x + distance * math.cos(angle),
            player_y + distance * math.sin(angle)
        )
        self.speed = 1

    def update(self):
        player_x, player_y = player.rect.center
        enemy_x, enemy_y = self.rect.center
        angle = math.atan2(player_y - enemy_y, player_x - enemy_x)
        self.rect.x = self.rect.x + self.speed * math.cos(angle)
        self.rect.y = self.rect.y + self.speed * math.sin(angle)

class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = player.rect.center
        self.speed = 20
        self.target_enemy = self.find_closest_enemy(enemy_group)

    def find_closest_enemy(self, enemy_group):
        closest_enemy = None
        min_distance = float('inf')

        for enemy in enemy_group:
            if (0 <= enemy.rect.centerx <= screen_width and 0 <= enemy.rect.centery <= screen_height):
                distance = math.sqrt((self.rect.centerx - enemy.rect.centerx) ** 2 +
                                    (self.rect.centery - enemy.rect.centery) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_enemy = enemy

        return closest_enemy
    
    def update(self):
        if not (0 <= self.rect.x <= screen_width and 0 <= self.rect.y <= screen_height):
                self.kill()

        if self.target_enemy:
            player_x, player_y = self.rect.center
            enemy_x, enemy_y = self.target_enemy.rect.center
            angle = math.atan2(enemy_y - player_y, enemy_x - player_x)
            self.rect.x += self.speed * math.cos(angle)
            self.rect.y += self.speed * math.sin(angle)

            if not self.target_enemy.alive:
                self.kill()

            enemy_hit = pygame.sprite.spritecollideany(self, enemy_group)
            if pygame.sprite.spritecollideany(self, enemy_group):
                new_exp = ExpPoint(player, enemy_x, enemy_y)
                exp_group.add(new_exp)
                all_sprites.add(new_exp)
                self.kill()
                player.score += 1
                enemy_hit.kill()
        else:
            self.kill()

class ExpPoint(pygame.sprite.Sprite):
    def __init__(self, player, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 3))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10

    def update(self):
        player_x, player_y = player.rect.centerx, player.rect.centery

        distance_to_player = math.sqrt((self.rect.centerx - player_x) ** 2 + (self.rect.centery - player_y) ** 2)

        if distance_to_player <= player.pickup:
            angle = math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx)
            self.rect.x += self.speed * math.cos(angle)
            self.rect.y += self.speed * math.sin(angle)
        exp_hit = pygame.sprite.spritecollideany(player, exp_group)
        if exp_hit:
            player.exp += 1
            if player.exp >= player.expcap:
                player.exp -= player.expcap
                player.expcap += 5
                player.hp = max(player.hp, player.hp + 5)
                player.lvl += 1
                player.attack_speed -= 0.1
            exp_hit.kill()

player = Player()
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
exp_group = pygame.sprite.Group()
ui = pygame.sprite.Group()

ui.add(hud())
for _ in range(10):
    enemy = Enemy()
    enemy_group.add(enemy)

all_sprites = pygame.sprite.Group()
all_sprites.add(player, enemy_group, exp_group, ui)

running = True
game_over = False

while running and not game_over:
    clock.tick(60)
    screen.fill((115, 115, 115))

    score_text = font.render(f'Score: {player.score}', True, WHITE)
    lvl_text = font.render(f'Level: {player.lvl}', True, WHITE)

    score_width, score_height = score_text.get_rect().size[0], score_text.get_rect().size[1]
    lvl_width, lvl_height = lvl_text.get_rect().size[0], lvl_text.get_rect().size[1]
    score_x, score_y = (screen_width - score_width) / 2, 10
    lvl_x, lvl_y = (screen_width - lvl_width) / 2, 30

    screen.blit(score_text, (score_x, score_y))
    screen.blit(lvl_text, (lvl_x, lvl_y))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()
    if current_time - last_gen_time >= regen_time:
        last_gen_time = current_time
        for _ in range(regen_mobs):
            new_enemy = Enemy()
            enemy_group.add(new_enemy)
            all_sprites.add(new_enemy)
        regen_mobs += 3

    if current_time - last_shot_time >= (player.attack_speed * 1000):
        last_shot_time = current_time
        new_bullet = Bullet()
        bullet_group.add(new_bullet)
        all_sprites.add(new_bullet)

    player.update()
    for enemy in enemy_group:
        enemy.update()
    bullet_group.update()
    exp_group.update()
    ui.update()

    all_sprites.draw(screen)

    if pygame.sprite.spritecollideany(player, enemy_group):
        if current_time - last_hit_time >= hit_inv_time:
            last_hit_time = current_time
            player.hit()
            player.hp -= 10
            if player.hp <= 0:
                game_over = True

    pygame.display.flip()

    while running and game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        gameover = pygame.Surface((screen_width, screen_height))
        screen.blit(gameover, (0, 0))
        gameover_text = font.render('GAME OVER', True, (255, 255, 255))
        text_width, text_height = gameover_text.get_rect().size[0], gameover_text.get_rect().size[1]
        text_x, text_y = (screen_width - text_width) / 2, (screen_height - text_height) / 2 - 40

        score_text = font.render(f'Final Score: {player.score}', True, WHITE)
        lvl_text = font.render(f'Final Level: {player.lvl}', True, WHITE)

        score_width, score_height = score_text.get_rect().size[0], score_text.get_rect().size[1]
        lvl_width, lvl_height = lvl_text.get_rect().size[0], lvl_text.get_rect().size[1]
        score_x, score_y = (screen_width - score_width) / 2, text_y + 20
        lvl_x, lvl_y = (screen_width - lvl_width) / 2, text_y + 40

        screen.blit(score_text, (score_x, score_y))
        screen.blit(lvl_text, (lvl_x, lvl_y))
        screen.blit(gameover_text, (text_x, text_y))

        pygame.display.flip()

pygame.quit()
sys.exit()