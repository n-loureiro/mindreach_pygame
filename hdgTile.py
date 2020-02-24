import pygame 
from math import pi

class HdgTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        self.tile_size_x = size_x/2
        self.tile_size_y = size_y*0.4

        self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image.fill((17, 218, 255))
        self.rect = self.image.get_rect(left=size_x/2, top=size_y*0.6)
        self.canvas = canvas
        #self.canvas.blit(self.image, (0,0))


    def drawTerrain(self, tilt):
        self.image.fill((17, 218, 255))

        wrect = pygame.Rect(0, self.tile_size_y/2, self.tile_size_x, self.tile_size_y/2)
        pygame.draw.rect(self.image, (133, 87, 35), wrect)


        for line_i in range(5):
            wrect = pygame.Rect(self.tile_size_x*0.35, self.tile_size_y*0.2+(line_i)*self.tile_size_y*0.15, self.tile_size_x*0.3, self.tile_size_y/150)
            pygame.draw.rect(self.image, (255,255,255), wrect)
        for line_i in range(5):
            wrect = pygame.Rect(self.tile_size_x*0.4, self.tile_size_y*0.275+(line_i)*self.tile_size_y*0.15, self.tile_size_x*0.2, self.tile_size_y/150)
            pygame.draw.rect(self.image, (255,255,255), wrect)

        arc = pygame.Surface((int(self.tile_size_x*0.4), int(self.tile_size_y*0.4)))
        print(arc.get_rect().move(100,300))
        pygame.draw.arc(self.image, (255,255,255), (arc.get_rect().move(self.tile_size_x*0.3,self.tile_size_y/10)), 0, pi, int(self.tile_size_y/80))

