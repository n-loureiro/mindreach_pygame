import pygame 

class MapTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        print('here')
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
        self.blit_map()

        if pos[0]< self.tile_size_x and pos[1]< self.tile_size_y:
            self.waypoint_list.append(pos)
        

        if len(self.waypoint_list)>1: #if more than 1 point, connect them
            pygame.draw.polygon(self.image, (0,0,225), self.waypoint_list, 4)

        else:
            self.create_drone(pos)


        #Draw all waypoints
        for wp in self.waypoint_list:
            pygame.draw.circle(self.image, (250,10,0), wp, 5)

    def clear_waypoints(self):
        self.blit_map()
        self.waypoint_list = []

    def blit_map(self):
        self.image.blit(self.background_image, [0,0])

    def create_drone(self, pos):

        self.drone = pygame.image.load("drone.png").convert_alpha()
        self.drone = pygame.transform.scale(self.drone, (int(self.tile_size_x/20), int(self.tile_size_x/20)))
        self.drone = pygame.transform.rotozoom(self.drone, -45,1)


        self.rect_drone = self.drone.get_rect()
        self.rect_drone.center = pos

        self.image.blit(self.drone, self.rect_drone)