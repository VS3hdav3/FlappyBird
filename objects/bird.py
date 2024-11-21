import pygame
import os
#from ... import main

bird_img = [pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird1.png"))), 
        pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird2.png"))), 
        pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird3.png")))]

class Bird:
    max_rotation = 25
    imgs = bird_img
    rot_vel = 20
    ani_time = 5
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.imgs[0]
    
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    
    def move(self):
        self.tick_count += 1
        
        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement
        
        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        if displacement < 0:
            displacement -= 2
        
        self.y = self.y + displacement
        
        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.rot_vel
    
    def draw(self, win):
        self.img_count += 1
        
        # For animation of bird, loop through three images
        if self.img_count <= self.ani_time:
            self.img = self.imgs[0]
        elif self.img_count <= self.ani_time*2:
            self.img = self.imgs[1]
        elif self.img_count <= self.ani_time*3:
            self.img = self.imgs[2]
        elif self.img_count <= self.ani_time*4:
            self.img = self.imgs[1]
        elif self.img_count == self.ani_time*4 + 1:
            self.img = self.imgs[0]
            self.img_count = 0
        
        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.imgs[1]
            self.img_count = self.ani_time*2
        
        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)
        
        #rotated_image =  pygame.transform.rotate(self.img, self.tilt)
        #new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        #win.blit(rotated_image, new_rect.topleft)
    
    def get_mask(self):
        return pygame.mask.from_surface(self.img)
    
def blitRotateCenter(surf, image, topleft, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)