import pygame 

class MapTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        self.tile_size_x = size_x
        self.tile_size_y = size_y*0.6

        #self.image = pygame.Surface((self.tile_size_x, self.tile_size_y))
        self.image = pygame.Surface((size_x, size_y*0.6))
        
        self.background_image = pygame.image.load("champ.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (int(self.tile_size_x), int(self.tile_size_y)))
        #self.image.blit(self.background_image, [0,0])
        self.blit_map()
        self.rect = self.image.get_rect(left=0)
        self.canvas = canvas


        self.waypoint_list = []
        #self.canvas.blit(self.image, (0,size_y*0.6))

    def set_new_waypoint(self, pos):

        if pos[0]< self.tile_size_x and pos[1]< self.tile_size_y:
            self.waypoint_list.append(pos)
        self.blit_map()

        if len(self.waypoint_list)>1: #if more than 1 point, connect them
            pygame.draw.polygon(self.image, (0,0,225), self.waypoint_list, 4)

        #Draw all waypoints
        for wp in self.waypoint_list:
            pygame.draw.circle(self.image, (255,0,0), wp, 10)

    def clear_waypoints(self):
        self.blit_map()
        self.waypoint_list = []



    def blit_map(self):
        self.image.blit(self.background_image, [0,0])