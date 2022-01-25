import pygame
import math

pygame.init()

win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Shape Cutting")
clock = pygame.time.Clock()

points = []
polygon_colour = (255, 0, 0)
mode = "draw"
polygon = None
cutoff = []
finish_polygon = False
line_start = None

font = pygame.font.Font("freesansbold.ttf", 32)
original_area = 100


class Line:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        if (p1[0] - p2[0]) == 0:
            self.m = "undefined"
            self.x_pos = p1[0]
        else:
            self.m = (p1[1] - p2[1]) / (p1[0] - p2[0])
            self.c = p1[1] - self.m * p1[0]

    def move(self, y_change):
        self.p1 = (self.p1[0], self.p1[1] + y_change)
        self.p2 = (self.p2[0], self.p2[1] + y_change)

        if (self.p1[0] - self.p2[0]) == 0:
            self.m = "undefined"
            self.x_pos = self.p1[0]
        else:
            self.m = (self.p1[1] - self.p2[1]) / (self.p1[0] - self.p2[0])
            self.c = self.p1[1] - self.m * self.p1[0]

    def collide(self, line):
        if line.m == self.m:
            return False
        if self.m == "undefined":
            collide_y = line.m * self.x_pos + line.c
            if max(line.p1[1], line.p2[1]) >= collide_y >= min(line.p1[1], line.p2[1]) and \
                    max(self.p1[1], self.p2[1]) >= collide_y >= min(self.p1[1], self.p2[1]):
                return self.x_pos, collide_y
            return False
        elif line.m == "undefined":
            collide_y = self.m * line.x_pos + self.c
            if max(line.p1[1], line.p2[1]) >= collide_y >= min(line.p1[1], line.p2[1]) and \
                    max(self.p1[1], self.p2[1]) >= collide_y >= min(self.p1[1], self.p2[1]):
                return line.x_pos, collide_y
            return False
        collide_x = (self.c - line.c) / (line.m - self.m)
        if max(line.p1[0], line.p2[0]) >= collide_x >= min(line.p1[0], line.p2[0]) and \
                max(self.p1[0], self.p2[0]) >= collide_x >= min(self.p1[0], self.p2[0]):
            collide_y = self.m * collide_x + self.c
            return collide_x, collide_y
        return False


class Polygon:
    def __init__(self, corners, colour=(255, 0, 0)):
        self.corners = corners
        self.colour = colour

        self.lines = []
        for i in range(len(corners) - 1):
            self.lines.append(Line(corners[i], corners[i + 1]))

        self.y_vel = 0
        self.area = self.get_area()

    def draw(self):
        pygame.draw.polygon(win, self.colour, self.corners)
        pygame.draw.polygon(win, (0, 0, 0), self.corners, 3)

    def fall(self):
        for i in range(len(self.corners)):
            self.corners[i] = (self.corners[i][0], self.corners[i][1] + self.y_vel)
        for line in self.lines:
            line.move(self.y_vel)
        self.y_vel += 0.5
        if min(self.corners, key=lambda x: x[1])[1] > 600:
            cutoff.remove(self)

    def split(self, collision):
        poly1 = []
        poly2 = []
        valid = True
        for line in self.lines:
            if line.p1 == collision[0][0].p1 and line.p2 == collision[0][0].p2:
                poly1.append(Line(line.p1, collision[0][1]))
                poly2.append(Line(collision[0][1], line.p2))
                valid = False
            elif line.p1 == collision[1][0].p1 and line.p2 == collision[1][0].p2:
                poly1.append(Line(collision[0][1], collision[1][1]))
                poly1.append(Line(collision[1][1], line.p2))

                poly2.append(Line(line.p1, collision[1][1]))
                poly2.append(Line(collision[1][1], collision[0][1]))

                valid = True
            elif valid:
                poly1.append(line)
            else:
                poly2.append(line)

        poly1 = Polygon.generate_poly(poly1)
        poly2 = Polygon.generate_poly(poly2)
        return max([poly1, poly2], key=lambda x: x.area), min([poly1, poly2], key=lambda x: x.area)

    def get_area(self):
        areas = []
        for line in self.lines:
            areas.append((line.p1[0] - line.p2[0]) * ((line.p1[1] + line.p2[1]) / 2))
        return abs(sum(areas))

    @staticmethod
    def generate_poly(lines):
        corners = []
        for line in lines:
            corners.append(line.p1)
        corners.append(lines[-1].p2)
        return Polygon(corners)


def point_in_polygon(point):
    test_line = Line((0, 0), point)
    num_collision = 0
    for line in polygon.lines:
        if line.collide(test_line):
            num_collision += 1
    return num_collision % 2 == 1


run = True
while run:
    mouse = pygame.mouse.get_pos()
    pressed = pygame.mouse.get_pressed(3)

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            pygame.quit()
            quit()

    win.fill((255, 255, 255))

    if mode == "draw":
        if pressed[0]:
            if len(points) > 2 and math.dist(mouse, points[0]) < 15:
                points.append(points[0])
                mode = "detect"
                polygon = Polygon(points)
                original_area = polygon.area
            elif mouse not in points:
                points.append(mouse)
        else:
            if len(points) > 0:
                pygame.draw.line(win, (0, 0, 0), points[-1], mouse, 3)
        for i in range(len(points) - 1):
            pygame.draw.line(win, (0, 0, 0), points[i], points[i + 1], 3)

        if len(points) > 2 and math.dist(mouse, points[0]) < 15:
            pygame.draw.circle(win, (200, 200, 200), points[0], 15)
    else:
        polygon.draw()
        for poly in cutoff:
            poly.draw()
            poly.fall()

        if pressed[0]:
            if not line_start and finish_polygon and not point_in_polygon(mouse):
                line_start = mouse
        else:
            finish_polygon = True
            if line_start and not point_in_polygon(mouse):
                cut = Line(line_start, mouse)
                collisions = []
                for line in polygon.lines:
                    if line.collide(cut):
                        collisions.append((line, line.collide(cut)))
                collisions.sort(key=lambda x: polygon.lines.index(x[0]))

                for i in range(0, len(collisions), 2):
                    polygon, part = polygon.split((collisions[i], collisions[i + 1]))
                    if part:
                        cutoff.append(part)
                        part.colour = (255, 166, 0)
            line_start = None
        if line_start:
            pygame.draw.line(win, (0, 0, 0), line_start, mouse, 3)

        if round(polygon.area / original_area * 100) <= 0:
            if round(polygon.area / original_area * 100, 2) <= 0:
                text = font.render("It's pretty much all gone stop wasting your time", True, (0, 0, 0))
            else:
                text = font.render(f"{round(polygon.area / original_area * 100, 2)}%", True, (0, 0, 0))
        else:
            text = font.render(f"{round(polygon.area / original_area * 100)}%", True, (0, 0, 0))
        win.blit(text, (400 - text.get_width() / 2, 10))

    pygame.display.update()
    clock.tick(60)
