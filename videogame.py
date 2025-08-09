import pygame
import sys
from os.path import join

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
TILE_SIZE = 64
game_state = "playing"
level = 1
fruit_list = [(500,1400),(500,800),(1800,1400),(1900,1400),(2000,1400),(2500,1400),(2600,1400),(2700,1400),(2500,400),(2600,400),(2700,800),(2600,800),
              (2500,180),(2600,180),(2700,180),(4900,100),(5000,100),(5000,800),(4900,800),(4800,800)]

fruit_list2 =[]
enemies_list =[(700,1400),(1200,1000),(2500,1000),(2000,1200),(4500,40),(5000,0),(9000,0)]
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer - NinjaFrog")
clock = pygame.time.Clock()

BLUE = (0, 0, 255)
SKY = (135, 206, 235)

# --- טוען את האריחים ---
terrain_img = pygame.image.load(join("assets", "Terrain", "Terrain.png")).convert_alpha()
tile_width = 352 // 6
tile_height = 176 // 4
tile_rect = pygame.Rect(0,0 , tile_width - 10, tile_height)

tile_level_2_rect =  pygame.Rect(192,0 , tile_width - 10, tile_height)
level_2_tile = terrain_img.subsurface(tile_level_2_rect)
level_2_tile = pygame.transform.scale(level_2_tile, (64, 64))


orange_tile = terrain_img.subsurface(tile_rect)
orange_tile = pygame.transform.scale(orange_tile, (64, 64))

# enemi_img = pygame.image.load(join("assets", "MainCharacters","MaskDude", "idle.png")).convert_alpha()
# enemi_width = 630 // 4
# enemi_height = 500 // 5
# enemi_rect = pygame.Rect(0,0, 10,10 )
# enemi_ = enemi_img.subsurface(enemi_rect)
# enemi_ = pygame.transform.scale(enemi_, (150, 150))


# --- פונקציה לטעינת תמונות מתוך sprite sheet ---
def load_images(sheet_path, frame_width, frame_height):
    sheet = pygame.image.load(sheet_path).convert_alpha()
    images = []
    for i in range(sheet.get_width() // frame_width):
        frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        images.append(frame)
    return images


# --- מחלקת שחקן עם אנימציה ---
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.state = "idle"
        self.facing_right = True

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 0.8
        self.jump_speed = -16
        self.on_ground = False
        self.jump_count = 0
        self.max_jumps = 2
        self.on_wall_left = False
        self.on_wall_right = False

    def import_assets(self):
        base_path = join("assets", "MainCharacters", "NinjaFrog")
        self.animations = {
            "idle": load_images(join(base_path, "Run.png"), 32, 32)[:1],
            "run": load_images(join(base_path, "Run.png"), 32, 32),
            "jump": load_images(join(base_path, "Jump.png"), 32, 32),
            "fall": load_images(join(base_path, "Fall.png"), 32, 32),
        }

        # קנה מידה
        for key in self.animations:
            self.animations[key] = [pygame.transform.scale(img, (64, 64)) for img in self.animations[key]]

    def get_state(self):
        if self.vel.y < 0:
            self.state = "jump"
        elif self.vel.y > 1:
            self.state = "fall"
        elif self.vel.x != 0:
            self.state = "run"
        else:
            self.state = "idle"

    def animate(self):
        self.get_state()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        image = self.animations[self.state][int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel.x = self.speed
            self.facing_right = True
        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.vel.y = self.jump_speed
                self.jump_count = 1
            elif self.jump_count < self.max_jumps:
                self.vel.y = self.jump_speed
                self.jump_count += 1
            elif self.on_wall_left or self.on_wall_right:
                self.vel.y = self.jump_speed
                self.jump_count = 1

    def apply_gravity(self):
        self.vel.y += self.gravity
        self.rect.y += self.vel.y

    def move_x(self, tiles):
        self.rect.x += self.vel.x
        self.on_wall_left = False
        self.on_wall_right = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                    self.on_wall_right = True
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                    self.on_wall_left = True

    def move_y(self, tiles):
        self.apply_gravity()
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0

    def update(self):
        self.input()
        self.animate()

# --- אריח ---
class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

# --- אויבים ---
class Enemi(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.state = "idle"
        self.facing_right = True

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 2
        self.gravity = 0.8
        self.on_ground = False

        self.direction = 1
        self.distance = 0
        self.max_distance = 500

        self.hit = False
        self.hit_timer = 0  # זמן שבו נפגע
        self.kill_delay = 500  # אלפיות שנייה עד שנעלם

    def import_assets(self):
        base_path = join("assets", "MainCharacters", "MaskDude")
        self.animations = {
            "hit": load_images(join(base_path, "hit.png"), 32, 32),
            "idle": load_images(join(base_path, "Run.png"), 32, 32)[:1],
            "run": load_images(join(base_path, "Run.png"), 32, 32),
            "jump": load_images(join(base_path, "Jump.png"), 32, 32),
            "fall": load_images(join(base_path, "Fall.png"), 32, 32),
        }

        # קנה מידה
        for key in self.animations:
            self.animations[key] = [pygame.transform.scale(img, (64, 64)) for img in self.animations[key]]
            

    
    def get_state(self):
        if self.hit:
            self.state = "hit"
        elif self.vel.y < 0:
            self.state = "jump"
        elif self.vel.y > 1:
            self.state = "fall"
        elif self.vel.x != 0:
            self.state = "run"
        else:
            self.state = "idle"

    def animate(self):
        self.get_state()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        image = self.animations[self.state][int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image
    
    def input(self):
        
        self.vel.x = self.speed * self.direction
        self.distance += abs(self.vel.x)

        if self.distance >= self.max_distance:
            self.direction *= -1
            self.facing_right = not self.facing_right
            self.distance = 0

    def apply_gravity(self):
        self.vel.y += self.gravity
        self.rect.y += self.vel.y

    def move_x(self, tiles):
        self.rect.x += self.vel.x
        self.on_wall_left = False
        self.on_wall_right = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.x > 0:
                    self.rect.right = tile.rect.left
                    self.on_wall_right = True
                elif self.vel.x < 0:
                    self.rect.left = tile.rect.right
                    self.on_wall_left = True

    def move_y(self, tiles):
        self.apply_gravity()
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.vel.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0
    def update(self):
        if self.hit:
            # ספירת זמן מרגע הפגיעה
            if pygame.time.get_ticks() - self.hit_timer >= self.kill_delay:
                self.kill()
            self.animate()
        else:
            self.input()
            self.animate()



# -- נקודת סיום ---
class End(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.state = "start (Moving)(64x64).png"
        

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
    def import_assets(self):
        base_path = ("")
        self.animations = {
             "start (Moving)(64x64).png": load_images((r"C:\Users\בצלאל\Desktop\Python-Platformer-main\assets\Items\Checkpoints\Start\Start (Moving) (64x64).png"), 64, 64)
            
        }

        # קנה מידה
        for key in self.animations:
            self.animations[key] = [pygame.transform.scale(img, (64, 64)) for img in self.animations[key]]

    def get_state(self):
        self.state = "start (Moving)(64x64).png"

    def animate(self):
        self.get_state()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        image = self.animations[self.state][int(self.frame_index)]
        self.image = image
    def update(self):
        self.animate()

class Fruit(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.state = "Strawberry.png"
        

        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
    def import_assets(self):
        base_path = ("")
        self.animations = {
             "Strawberry.png": load_images((r"C:\Users\בצלאל\Desktop\Python-Platformer-main\assets\Items\Fruits\Strawberry.png"), 32, 32)
            
        }

        # קנה מידה
        for key in self.animations:
            self.animations[key] = [pygame.transform.scale(img, (100, 100)) for img in self.animations[key]]

    def get_state(self):
        self.state = "Strawberry.png"

    def animate(self):
        self.get_state()
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0
        image = self.animations[self.state][int(self.frame_index)]
        self.image = image
    def update(self):
        self.animate()


# --- מצלמה ---
class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = screen
        self.offset = pygame.math.Vector2()
        self.half_w = WIDTH // 2
        self.half_h = HEIGHT // 2 

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_w
        self.offset.y = player.rect.centery - self.half_h
        self.display_surface.fill(SKY)

        for sprite in sorted(self.sprites(), key=lambda s: s.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

# --- בניית עולם ---
player = Player((100, 1200))
player_group = pygame.sprite.GroupSingle(player)
level_enemies = pygame.sprite.Group()
level_fruits = pygame.sprite.Group()
level_tiles = pygame.sprite.Group()
another_sprites = pygame.sprite.Group()
camera_group = CameraGroup()
camera_group.add(player)

level_map = [
    
    
    
    '    xxxx           x       xx          xxxxx                                                                          ',
    '    xxxx           x       xx          xxxxx                                    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ',
    '    xxxx           x       xx                                                                                      x  x',
    '    xxxx           x       xx                                                 x                                    x  x', 
    '    xxxx           x       xx   xxxxxxxxxxxxxxxxxxxxxxxx                                                           x  x',
    '    xxxx           x       xx          xxxxx                                                                          x',
    '    xxxx           x       xx        x    xxxxxxx                          x                                          x',
    '    xxxx           x       xx  xx    x                                                                                x',
    '    xxxx           x       xx  xx    x                                      xxxxxxxxxxxxx                       xx    x ',
    '    xxxxxxxxxxxx   x       xx  xx    x                                   x              x                       xx    x  ',
    '    xxxx           x           xx    x                                                 x                       xx    xx   ',
    '    xxxx           x           xx    x                                 x              x                       xx   xx    ',
    '    xxxx           x      xxxxxxx    x                                               x                       xx   xx     ',
    '    xxxx           x      xxx        x                                 x            x                       xx   xx      ',
    '    xxxx           x      xxx                                           xxxxxxxxxxxx                       xx   xx       ',
    '    xxxx           x              xxxxxxxxxxxxxxxx   xx                                                        xx       ',
    '    xxxx                        xxxxxxxxxxxx         xx                                                       xx        ',
    '    xxxx                       xxxxxxxxxxx           xx                                                  xxxxxx        ',
    '                               xxxxx                 xx                                               xxxxxx           ',
    '                               xxxxx                 xx                                            xxxxx              ',
    '    xxxx         xxxxxxxxxxxx                         xx                                       xxxx                    ',
    '    xxxx         xxx       xx                        xx                                      xxxxx                    ',
    '    xxxx         xxx                                 xx                                  xxxx                          ',
    '    xxxx         xxx                                                               xxxx                                ',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  xxxx                xxxx                                 ',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx         xxxx       xxxxx                                  ',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx               xxxxxxx                                      ',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx                                                           ',
    'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx                                                           ',
]

level2_map = [

    '                                                              xxxxxxx                                                   ',
    '                                                              xx                 xxxxxxxx       xxxxxxxx                  ',
    '                                                              xx                                                        ',
    '                                                              xx   xxxxxxxxxxxxxxx      xxxxxxxxxx     xxxxxx            ',
    '                                                                   xx                                                   ',
    '                                                                   xx             xxxxxxxx       xxxxxxxx                ',
    '                                                              xx   xx                                                  ',
    '                                                              xx           xxxxxxxx      xxxxxxxxx      xxxxxxxxx        ',
    '                                                              xx                                                      ',
    '                                                              xx    xx           xxxxxxxx                                ',
    '                                                                    xx                                                ',
    '                                                              xx    xx                                                  ',
    '                                                              xx    xx                                                  ',
    '                                                              xx                                                       ',
    '                                                              xx    xx                                                 ',
    '                                                              xx    xx                                                 ',
    '                                                                    xx                                                 ',
    '                                                                                                                       ',
    '                                                                                                                        ',
    '                                                          xxxxxxxxxxxxxxxxx                                               ',
    '                                      xxxxxxxxxxxxxxxxx                                                                 ',
    '                      xxxxxxxxxxxxxx                                                                                    ',
    ' xxxxxxxxxxxxxxxxxxx                                                                                                    ',

]
    
    

for row_index, row in enumerate(level_map):
    for col_index, cell in enumerate(row):
        if cell == 'x':
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            tile = Tile((x, y), orange_tile)
            level_tiles.add(tile)
            camera_group.add(tile)
for enemi in enemies_list:
    x = enemi[0]
    y = enemi[1]
    enemi =Enemi((x,y))
    level_enemies.add(enemi)
    camera_group.add(enemi)
for fruit in fruit_list:
    x = fruit[0]
    y = fruit[1]
    fruit =Fruit((x,y))
    level_fruits.add(fruit)
    camera_group.add(fruit)

end = End((100,1480))
another_sprites.add(end)
camera_group.add(end)

collected_fruits = 0

 
# --- לולאת המשחק ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if game_state == "playing":
        
        level_fruits.update()
        end.update()
        player.update()
        player.move_x(level_tiles)
        player.move_y(level_tiles)

        for enemi in level_enemies:
            enemi.update()
            enemi.move_x(level_tiles)
            enemi.move_y(level_tiles)
        
        # בדיקת התנגשות בין שחקן לפירות
        collected = pygame.sprite.spritecollide(player, level_fruits, dokill=True)
        collected_fruits += len(collected)
        # איסוף פירות

        # מעבר למסך סיום שלב
        if collected_fruits >= 25:
            game_state = "level complete"


        for enemy in level_enemies:
            if player.rect.colliderect(enemy.rect):
                if player.rect.bottom < enemy.rect.centery and player.vel.y > 0 and not enemy.hit:
                    enemy.hit = True
                    enemy.hit_timer = pygame.time.get_ticks()
                    player.vel.y = -15  # קפיצה קלה אחרי הפגיעה
                elif not enemy.hit:
                    game_state = "game over"

     
        camera_group.custom_draw(player)
        
        if player.vel.y > 150:
            game_state = "game over"
        font = pygame.font.SysFont(None, 40)
        fruit_text = font.render(f"fruits colected {collected_fruits}/ 25", True, (255, 0, 0))
        screen.blit(fruit_text, (20, 20))  # מצויר בפינה שמאלית עליונה

    elif game_state == "level complete":
        screen.fill((200, 255, 200))  # רקע ירוק בהיר
        font = pygame.font.SysFont(None, 100)
        text = font.render("You did it!", True, (0, 100, 0))
        screen.blit(text, (350, 250))
        font_small = pygame.font.SysFont(None, 50)
        next_level_text = font_small.render("To next level press Enter", True, (0, 100, 0))
        screen.blit(next_level_text, (340, 350))

    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
        level += 1
        game_state = "playing"

        # אפס את הקבוצות
        player_group.empty()
        level_enemies.empty()
        level_fruits.empty()
        level_tiles.empty()
        camera_group.empty()
        another_sprites.empty()

        # שחקן חדש
        player = Player((100, 100))
        player_group.add(player)
        camera_group.add(player)

        # אויבים חדשים (אפשר לשנות רשימה בעתיד)
        for enemi_data in enemies_list:
            enemi = Enemi(enemi_data)
            level_enemies.add(enemi)
            camera_group.add(enemi)

        # פירות חדשים (אותה רשימה לעת עתה)
        for fruit_data in fruit_list2:
            fruit = Fruit(fruit_data)
            level_fruits.add(fruit)
            camera_group.add(fruit)

        # סוף חדש
        end = End((100,1350))
        another_sprites.add(end)
        camera_group.add(end)

        # שלב חדש: תוכל לשנות את התצוגה פה לפי `level`
        if level == 2:
            SKY = (255, 206, 250)  # 
            orange_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
            orange_tile.fill((200, 100, 0))  # צבע שונה לבלוקים

        # בניית האריחים
        for row_index, row in enumerate(level2_map):
            for col_index, cell in enumerate(row):
                if cell == 'x':
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE
                    tile = Tile((x, y),level_2_tile )
                    level_tiles.add(tile)
                    camera_group.add(tile)

        collected_fruits = 0  # איפוס הספירה

    elif game_state =="game over":
        screen.fill((255, 255, 200))
        font = pygame.font.SysFont(None, 100)
        text = font.render("Game Over", True, (0, 255, 0))
        screen.blit(text, (400, 300))
        font_small = pygame.font.SysFont(None, 50)
        restart_text = font_small.render("Press Enter to Restart", True, (0,255 , 0))
        screen.blit(restart_text, (410, 400))
         
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
    # 1. אפס את כל הקבוצות הישנות
            player_group.empty()
            level_enemies.empty()
            camera_group.empty()

            
            # 2. צור שחקן חדש
            end = End((100,1480))
            another_sprites.add(end)
            camera_group.add(end)

            player = Player((100, 100))
            player_group.add(player)
            camera_group.add(player)

            for fruit in fruit_list:
                x = fruit[0]
                y = fruit[1]
                fruit =Fruit((x,y))
                level_fruits.add(fruit)
                camera_group.add(fruit)
            # בדיקת התנגשות בין שחקן לפירות
            collected = pygame.sprite.spritecollide(player, level_fruits, dokill=True)
            collected_fruits += len(collected)

            # 3. צור אויבים חדשים
            for enemi_data in enemies_list:
                enemi = Enemi(enemi_data)
                level_enemies.add(enemi)
                camera_group.add(enemi)

            collected_fruits = 0

            # 4. שנה את מצב המשחק
            game_state = "playing"

            
            for row_index, row in enumerate(level_map):
                for col_index, cell in enumerate(row):
                    if cell == 'x':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE
                        tile = Tile((x, y), orange_tile)
                        level_tiles.add(tile)
                        camera_group.add(tile)



    pygame.display.update()
    clock.tick(FPS)