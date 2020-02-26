import pygame 
import math

class MapTile(pygame.sprite.Sprite):
    def __init__(self, canvas, size_x, size_y):
        super().__init__()
        print('here')
        self.tile_size_x = size_x
        self.tile_size_y = size_y*0.6

        self.image = pygame.Surface((size_x, size_y*0.6))
        
        self.background_image = pygame.image.load("champ.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (int(self.tile_size_x), int(self.tile_size_y)))
        self.blit_map()
        self.rect = self.image.get_rect(left=0)
        self.canvas = canvas

        self.waypoint_list = []
        
        self.drone_flag = 0
        
        self.position = pygame.Vector2(self.tile_size_x/2, self.tile_size_y/2)
        self.direction = pygame.Vector2(1,0)
        self.speed = 0#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = 0
        self.angle_speed = 0

        self.create_drone()

    def set_new_waypoint(self, pos):
        self.blit_map()

        self.pos=pos

        if pos[0]< self.tile_size_x and pos[1]< self.tile_size_y:
            self.waypoint_list.append(pos)

        self.blit_waypoints()
        

    def blit_waypoints(self):

        if len(self.waypoint_list)>1: #if more than 1 point, connect them
            pygame.draw.polygon(self.image, (0,0,225), self.waypoint_list, 4)
        for wp in self.waypoint_list:
            pygame.draw.circle(self.image, (250,10,0), wp, 5)

    def clear_waypoints(self):
        self.blit_map()
        self.waypoint_list = []
        self.drone_flag = 0
        self.create_drone()

    def blit_map(self):
        self.image.blit(self.background_image, [0,0])

    def create_drone(self):

        self.drone_orig = pygame.image.load("drone.png").convert_alpha()
        self.drone_orig = pygame.transform.scale(self.drone_orig, (int(self.tile_size_x/20), int(self.tile_size_x/20)))
        self.drone_orig = pygame.transform.rotozoom(self.drone_orig, -90,1)
        self.drone = self.drone_orig

        self.rect_drone = self.drone.get_rect()

        if len(self.waypoint_list)>1: 
            self.rect_drone.center = self.waypoint_list[0]
        else:
            self.rect_drone.center = (self.tile_size_x/2, self.tile_size_y/2)

        self.image.blit(self.drone, self.rect_drone)

        self.drone_flag = 1
        self.position = pygame.Vector2(self.tile_size_x/2, self.tile_size_y/2)
        self.direction = pygame.Vector2(1,0)
        self.speed = 0#math.sqrt(math.pow(self.tile_size_x,2) + math.pow(self.tile_size_y,2))/30
        self.angle = 0
        self.angle_speed = 0

    def update(self):

        if self.angle_speed != 0:
            # Rotate the direction vector and then the image.
            self.direction.rotate_ip(self.angle_speed)
            self.angle += self.angle_speed
            self.drone = pygame.transform.rotate(self.drone_orig, -self.angle)
            self.rect_drone = self.drone.get_rect()
                        
        # Update the position vector and the rect.
        self.position += self.direction * self.speed
        self.rect_drone.center = self.position


        self.blit_map()
        self.blit_waypoints()
        self.image.blit(self.drone, self.rect_drone)