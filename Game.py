import pygame
import random
import math

# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Player(pygame.sprite.Sprite):
    """
    This class represents the bar at the bottom that the player controls.
    """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()


        # This could also be an image loaded from the disk.
        player = pygame.image.load("aaa.png").convert()
        player.set_colorkey(BLUE)
        self.image = player


        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down 1
        # when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -10

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.change_x = -6

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.change_x = 6

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.change_x = 0

class Bullet(pygame.sprite.Sprite):
    """ This class represents the bullet. """

    def __init__(self, start_x, start_y, dest_x, dest_y):
        """ Constructor.
        It takes in the starting x and y location.
        It also takes in the destination x and y position.
        """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Set up the image for the bullet
        self.image = pygame.Surface([4, 10])
        self.image.fill(WHITE)

        self.rect = self.image.get_rect()

        # Move the bullet to our starting location
        self.rect.x = start_x
        self.rect.y = start_y

        # Because rect.x and rect.y are automatically converted
        # to integers, we need to create different variables that
        # store the location as floating point numbers. Integers
        # are not accurate enough for aiming.
        self.floating_point_x = start_x
        self.floating_point_y = start_y

        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff);

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        velocity = 5
        self.change_x = math.cos(angle) * velocity
        self.change_y = math.sin(angle) * velocity

    def update(self):
        """ Move the bullet. """

        # The floating point x and y hold our more accurate location.
        self.floating_point_y += self.change_y
        self.floating_point_x += self.change_x

        # The rect.x and rect.y are converted to integers.
        self.rect.y = int(self.floating_point_y)
        self.rect.x = int(self.floating_point_x)

        # If the bullet flies of the screen, get rid of it.
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT:
            self.kill()

class Block(pygame.sprite.Sprite):
    """ This class represents the block. """
    def __init__(self, color):
        # Call the parent class (Sprite) constructor
        super().__init__()

        blocks = pygame.image.load("enemy3.png").convert()

        self.image = blocks 
        self.image.set_colorkey(RED)

        self.rect = self.image.get_rect()


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, width, height):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        platform = pygame.image.load("platform.png").convert()

        self.image = platform 
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()

class Flag(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this code.
            """
        super().__init__()

        flag = pygame.image.load("flag2.png").convert()

        self.image = flag 
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()


class Level():
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving
            platforms collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.blocks_list = pygame.sprite.Group()
        self.all_sprite_list = pygame.sprite.Group()
        self.bullet_list = pygame.sprite.Group()
        self.flag_list = pygame.sprite.Group()
        self.player = player

        # How far this world has been scrolled left/right
        self.world_shift = 0

    # Update everythign on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        self.enemy_list.update()
        self.blocks_list.update()
        self.all_sprite_list.update()
        self.bullet_list.update()
        self.flag_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """

        # Draw the background
        screen.fill(BLUE)
        screen.blit(self.background,(self.world_shift // 3,0))

        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        self.enemy_list.draw(screen)
        self.blocks_list.draw(screen)
        self.all_sprite_list.draw(screen)
        self.bullet_list.draw(screen)
        self.flag_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll
        everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x

        for blocks in self.blocks_list:
            blocks.rect.x += shift_x
            
        for flag in self.flag_list:
            flag.rect.x += shift_x

# Create platforms for the level
class Level_01(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load("background3.jpg").convert()
        self.background.set_colorkey(RED)        
        self.level_limit = -1000  
        
        flag = Flag()
        flag.rect.x = (1800)
        flag.rect.y = (50)
        
        # Add the block to the list of objects
        self.flag_list.add(flag)
        self.all_sprite_list.add(flag)        
            

        # Array with width, height, x, and y of platform
        level = [[210, 70, 500, 500],
                 [210, 70, 800, 400],
                 [210, 70, 1000, 500],
                 [210, 70, 1120, 280],
                 [210, 70, 1400, 150],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Go through the array above and add platforms
        for blocks in level:
            for i in range(25):
                # This represents a block
                blocks = Block(BLUE)

                # Set a random location for the block
                blocks.rect.x = random.randrange(2000)
                blocks.rect.y = random.randrange(350)

                # Add the block to the list of objects
                self.blocks_list.add(blocks)
                self.all_sprite_list.add(blocks)
                

# Create platforms for the level
class Level_02(Level):
    """ Definition for level 2. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load("background3.jpg").convert()
        self.background.set_colorkey(RED)          
        self.level_limit = -1000
        
        flag = Flag()
        flag.rect.x = (1800)
        flag.rect.y = (500)
    
        # Add the block to the list of objects
        self.flag_list.add(flag)
        self.all_sprite_list.add(flag)              

        # Array with type of platform, and x, y location of the platform.
        level = [[210, 30, 450, 570],
                 [210, 30, 850, 420],
                 [210, 30, 1000, 520],
                 [210, 30, 1120, 280],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        # Go through the array above and add platforms
        for blocks in level:
            for i in range(50):
                # This represents a block
                blocks = Block(BLUE)

                # Set a random location for the block
                blocks.rect.x = random.randrange(2000)
                blocks.rect.y = random.randrange(350)

                # Add the block to the list of objects
                self.blocks_list.add(blocks)
                self.all_sprite_list.add(blocks)
                
pygame.init()

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Instruction Screen")

# Loop until the user clicks the close button.
done = False
    
# This is a font we use to draw text on the screen (size 36)
font = pygame.font.Font(None, 36)

font2 = pygame.font.Font(None, 150)

display_instructions = True
instruction_page = 1
name = ""    

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# -------- Instruction Page Loop -----------
while not done and display_instructions:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                name += event.unicode
            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
            elif event.key == pygame.K_RETURN:
                instruction_page += 1  
                if instruction_page == 3:
                    display_instructions = False                
 
    # Set the screen background
    screen.fill(BLACK)
 
    if instruction_page == 1:
        # Draw instructions, page 1
        # This could also load an image created in another program.
        # That could be both easier and more flexible.
 
        text = font.render("Instructions", True, WHITE)
        screen.blit(text, [10, 10])
       
        text = font.render("Enter your name: ", True, WHITE)
        screen.blit(text, [10, 40])    
       
        text = font.render(name, True, WHITE)
        screen.blit(text, [220, 40])        
 
        text = font.render("Hit enter to continue", True, WHITE)
        screen.blit(text, [10, 80])
       
        text = font.render("Page 1", True, WHITE)
        screen.blit(text, [10, 120])
 
    if instruction_page == 2:
        # Draw instructions, page 2
        text = font.render("Shoot enemy's in the sky to get a hightscore", True, WHITE)
        screen.blit(text, [10, 10])    
 
        text = font.render("Use A,D and space for movement and Mouse1 to shoot", True, WHITE)
        screen.blit(text, [10, 40])
 
        text = font.render("Hit enter to continue", True, WHITE)
        screen.blit(text, [10, 80])
 
        text = font.render("Page 2", True, WHITE)
        screen.blit(text, [10, 120])
 
    # Limit to 60 frames per second
    clock.tick(60)
 
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
   
    score = 0


def main():
    """ Main Program """
    pygame.init()
    
    global score

    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("My Game")

    # Create the player
    player = Player()

    # List to hold all the sprites
    all_sprite_list = pygame.sprite.Group()

    # List of each bullet
    bullet_list = pygame.sprite.Group() 
    blocks_list = pygame.sprite.Group()
    flag_list = pygame.sprite.Group()

    # Create all the levels
    level_list = []
    level_list.append(Level_01(player))
    level_list.append(Level_02(player))

    # Set the current level
    current_level_no = 0
    current_level = level_list[current_level_no]

    active_sprite_list = pygame.sprite.Group()
    player.level = current_level

    player.rect.x = 340
    player.rect.y = SCREEN_HEIGHT - player.rect.height
    active_sprite_list.add(player)


    # Loop until the user clicks the close button.
    done = False
    
    game_over = False
    
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif not game_over: 
                if event.type == pygame.MOUSEBUTTONDOWN:
                # Fire a bullet if the user clicks the mouse button
            
                # Get the mouse position
                    pos = pygame.mouse.get_pos()
                    
                    mouse_x = pos[0]
                    mouse_y = pos[1]

                    # Create the bullet based on where we are, and where we want to go.
                    bullet = Bullet(player.rect.x, player.rect.y, mouse_x, mouse_y)
    
                    # Add the bullet to the lists
                    all_sprite_list.add(bullet)
                    bullet_list.add(bullet)
            
            if pygame.sprite.spritecollide(player, level_list[1].flag_list, True):
                game_over = True

            if not game_over: 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        player.go_left()
                    if event.key == pygame.K_d:
                        player.go_right()
                    if event.key == pygame.K_SPACE:
                        player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_d and player.change_x > 0:
                    player.stop()
           
        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        all_sprite_list.update()
        
        
        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= 500:
            diff = player.rect.right - 500
            player.rect.right = 500
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= 120:
            diff = 120 - player.rect.left
            player.rect.left = 120
            current_level.shift_world(diff)
        
        if pygame.sprite.spritecollide(player, level_list[0].flag_list, True):
            current_level_no += 1
            current_level = level_list[current_level_no]
            player.level = current_level 
            

        # Calculate mechanics for each bullet
        for bullet in bullet_list:

            # See if it hit a block
            block_hit_list = pygame.sprite.spritecollide(bullet, level_list[0].blocks_list, True)
            block_hit_list = pygame.sprite.spritecollide(bullet, level_list[1].blocks_list, True)

            # For each block hit, remove the bullet and add to the score
            for blocks in block_hit_list:
                bullet_list.remove(bullet)
                all_sprite_list.remove(bullet)
                score += 1
            
            # Remove the bullet if it flies up off the screen
            if bullet.rect.y < -10:
                bullet_list.remove(bullet)
                all_sprite_list.remove(bullet)

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        current_level.draw(screen)
        active_sprite_list.draw(screen)
        all_sprite_list.draw(screen)
        
        if game_over:
            # If game over is true, draw game over
            text = font2.render("Game Over", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)      
       

        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
            
        scoretext = "Score: " + str(score)
        text = font.render(scoretext, True, WHITE)
        screen.blit(text, [10, 10])
            
        # Limit to 60 frames per second
        clock.tick(60)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

    # Be IDLE friendly. If you forget this line, the program will 'hang'
    # on exit.
    pygame.quit()

if __name__ == "__main__":
    main()