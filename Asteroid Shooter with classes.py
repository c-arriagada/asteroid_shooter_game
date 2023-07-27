import pygame, sys
from random import randint, uniform

class Ship(pygame.sprite.Sprite):  # basic inheritance
    def __init__(self, groups):
        # 1. we have to init the parent class Sprite
        super().__init__(groups)
        # 2.  We need a surface -> image, specific of the class
        cat_image = pygame.image.load('./graphics/Figgy-1.png').convert_alpha()
        self.image = pygame.transform.scale(cat_image, (100, 85))

        # 3. We need a rect
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        # 4. Add a mask
        self.mask = pygame.mask.from_surface(self.image)

        # timer
        self.can_shoot = True
        self.shoot_time = None

        # sound
        self.laser_sound = pygame.mixer.Sound('./sounds/laser.ogg')

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 500:
                self.can_shoot = True

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_shoot(self):

        if pygame.mouse.get_pressed()[0] and self.can_shoot: #we only care about the left button
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Laser(self.rect.midtop, laser_group)
            self.laser_sound.play()


    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, False, pygame.sprite.collide_mask):
            pygame.quit()
            sys.exit()

    def update(self):
        self.laser_timer()
        self.input_position()
        self.laser_shoot()

        self.meteor_collision()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        heart_img = pygame.image.load('./graphics/Blue_heart.png').convert_alpha()
        self.image = pygame.transform.scale(heart_img, (35, 30))
        self.rect = self.image.get_rect(midbottom = pos)
        self.mask = pygame.mask.from_surface(self.image)

        #float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1) #-1 because you want it to move up
        self.speed = 600

        # sound
        self.explosion_sound = pygame.mixer.Sound('./sounds/explosion.wav')

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True, pygame.sprite.collide_mask):
            self.kill()
            self.explosion_sound.play()


    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = round(self.pos.x), round(self.pos.y)

        if self.rect.bottom < 0:
            self.kill()  #to free more memory

        self.meteor_collision()
        # self.rect.y -= 1

class Meteor(pygame.sprite.Sprite):
    def __init__(self, pos, groups):

        # basic setup
        super().__init__(groups)

        # randomizing the meteor size
        meteor_surf = pygame.image.load('./graphics/meteor.png').convert_alpha()
        meteor_size = pygame.math.Vector2(meteor_surf.get_size()) * uniform(0.5, 1.5)
        self.scaled_surf = pygame.transform.scale(meteor_surf, meteor_size)
        self.image = self.scaled_surf
        self.rect = self.image.get_rect(center = pos)
        self.mask = pygame.mask.from_surface(self.image)

        # float based position
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)  # -1 because you want it to move up
        self.speed = randint(400, 600)

        # rotation
        self.rotation = 0
        self.rotation_speed = randint(20, 50)

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center = self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.center = round(self.pos.x), round(self.pos.y)
        self.rotate()
        # self.rect.y -= 1

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Score:
    def __init__(self):
        self.font = pygame.font.Font('./graphics/subatomic.ttf', 50)

    def display(self):
        score_text = f'Score: {pygame.time.get_ticks() // 1000}' # divided by 1000 to get time in secs
        text_surf = self.font.render(score_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface,
                         (255, 255, 255),
                         text_rect.inflate(30, 30),
                         width=8, border_radius=5)

# basic setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
clock = pygame.time.Clock()

# background
background_surf = pygame.image.load('./graphics/background.png').convert()

# sprite groups
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# sprite creation
ship = Ship(spaceship_group)
# laser = Laser((100, 300), laser_group)
# spaceship_group.add(ship)

# timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)

# score
score = Score()

# background music
background_music = pygame.mixer.Sound('./sounds/music.wav')
background_music.play(loops = -1)

# game loop
while True:

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == meteor_timer:
            meteor_y_pos = randint(-150, -50)
            meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
            Meteor((meteor_x_pos, meteor_y_pos), meteor_group)

    # delta time
    dt = clock.tick() / 1000

    # background
    display_surface.blit(background_surf, (0, 0))

    # update
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()

    # score
    score.display()

    # graphics
    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    # draw the frame
    pygame.display.update()
