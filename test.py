import sys
import random
import math
import os
import requests
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPixmapItem
from PySide6.QtGui import QBrush, QPen, QPainter, QPixmap, QImage, QPainterPath, QWindow
from PySide6.QtCore import Qt, QTimer, QRect
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import spotipy.util as util

def get_prof_pic():
    os.environ["SPOTIPY_CLIENT_ID"]="0689d1156c404b359ed3edd8c943df3e"  
    os.environ["SPOTIPY_CLIENT_SECRET"]="43d103e7338d4f8ebe3a6b89e04ccda7"   
    os.environ["SPOTIPY_REDIRECT_URI"]="http://127.0.0.1:8888/callback"
    scope = 'user-top-read'
    token = util.prompt_for_user_token(scope=scope, show_dialog=True)
    sp = spotipy.Spotify(auth=token)
    sp.trace = False

    range = 'short_term'
    results = sp.current_user_top_artists(time_range=range, limit=15)
    imgs = []
    for i, item in enumerate(results['items']):
        imgs.append((item['images'][0]['url'], item['name']))
    return imgs

def mask_image(imgdata, imgtype='png', size=64):
    # Load image
    image = QImage.fromData(imgdata, imgtype)
    
    # Convert image to 32-bit ARGB (adds an alpha channel i.e., transparency factor)
    image = image.convertToFormat(QImage.Format_ARGB32)
    
    # Crop image to a square
    imgsize = min(image.width(), image.height())
    rect = QRect(
        (image.width() - imgsize) / 2,
        (image.height() - imgsize) / 2,
        imgsize,
        imgsize,
    )
    
    image = image.copy(rect)
    
    # Create the output image with the same dimensions and an alpha channel and make it completely transparent
    out_img = QImage(imgsize, imgsize, QImage.Format_ARGB32)
    out_img.fill(Qt.transparent)
    
    # Create a QPainter to draw the image
    painter = QPainter(out_img)
    
    # Draw the image with rounded corners
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(out_img.rect(), 10, 10)
    painter.setClipPath(path)
    painter.drawImage(0, 0, image)
    
    # End painting
    painter.end()
    
    # Convert the image to a pixmap and rescale it
    pr = QWindow().devicePixelRatio()
    pm = QPixmap.fromImage(out_img)
    pm.setDevicePixelRatio(pr)
    size *= pr
    pm = pm.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    # Return the pixmap data
    return pm

class RoundButton(QGraphicsEllipseItem):
    def __init__(self, x, y, diameter, scene, image_url=None):
        super().__init__(0, 0, diameter, diameter)
        self.setBrush(QBrush(Qt.blue))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsScenePositionChanges)
        
        self.diameter = diameter
        self.scene = scene
        self.scene.addItem(self)

        self.text = QGraphicsTextItem("Button", self)
        self.text.setDefaultTextColor(Qt.white)
        self.text.setPos(diameter / 4, diameter / 4)

        if image_url:
            self.set_image(image_url)

        self.gravityX = 0.0015 * diameter
        self.gravityY = 0.001 * diameter
        self.friction = 0.06
        self.repelForce = 0.008 * diameter
        self.velocityX = 0
        self.velocityY = 0
        
        self.moving = False

    def set_image(self, url):
        response = requests.get(url)
        img = mask_image(response.content, size=self.diameter)
        self.image = QGraphicsPixmapItem(img, self)
        self.image.setPos(0, 0)

    def reset(self):
        self.gravityX = 0.0015 * self.diameter
        self.gravityY = 0.001 * self.diameter
        self.friction = 0.06
        self.repelForce = 0.01 * self.diameter
        self.velocityX = 0
        self.velocityY = 0

    def advance(self):
        if not self.moving:
            self.setPos(self.x() + self.velocityX, self.y() + self.velocityY)
            self.apply_gravity_and_friction()
            self.check_collisions()

    def apply_gravity_and_friction(self):
        cube_center_x = self.scene.width() / 2
        cube_center_y = self.scene.height() / 2

        if self.y() + self.diameter >= cube_center_y:
            self.velocityY -= self.gravityY
        else:
            self.velocityY += self.gravityY

        if self.x() + self.diameter >= cube_center_x:
            self.velocityX -= self.gravityX
        else:
            self.velocityX += self.gravityX

        self.velocityX *= 1 - self.friction
        self.velocityY *= 1 - self.friction

    def check_collisions(self):
        for item in self.scene.items():
            if item != self and isinstance(item, RoundButton):
                distance = math.sqrt((self.x() - item.x()) ** 2 + (self.y() - item.y()) ** 2)
                collision_distance = (self.diameter + item.diameter) / 2
                
                if distance < collision_distance:
                    dx = self.x() - item.x()
                    dy = self.y() - item.y()
                    angle = math.atan2(dy, dx)
                    repelX = math.cos(angle) * self.repelForce
                    repelY = math.sin(angle) * self.repelForce
                    self.velocityX += repelX
                    self.velocityY += repelY

    def mousePressEvent(self, event):
        self.moving = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.velocityX = 0
        self.velocityY = 0
        self.gravityX = 0
        self.gravityY = 0
        self.repelForce = 0

    def mouseReleaseEvent(self, event):
        self.moving = False
        self.reset()
        super().mouseReleaseEvent(event)

class MainWindow(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, 800, 600)

        self.buttons = []
        img_urls = get_prof_pic()
        for url, name in img_urls:
            x = random.randint(0, 700)
            y = random.randint(0, 500)
            diameter = random.randint(50, 150)
            button = RoundButton(x, y, diameter, self.scene, image_url=url)
            self.buttons.append(button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(10)

    def update_scene(self):
        for button in self.buttons:
            button.advance()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

