import pygame
import random
import json
import threading
import socket
import time

# ---------- COLORS------------- #
violet = (42, 36, 60)
white = (255, 255, 255)
red = (225, 93, 64)
orange = (255, 148, 0)
green = (37, 137, 0)
blue = (101, 138, 187)
yellow = (242, 177, 64)
# ---------- COLORS------------- #

# --------- GLOBALS ------------ #
bgColor = violet
teamColor ={'a': red, 'b': blue, }
address = "192.168.112.135"
port = 8500
userDetails = {
    'name': None,
    'health': 100,
    'flags': {'fire': False, 'fired': False, 'dead': False, 'startGame': False, 'gameOver': False},
    'attackPosition': (-1, -1),
    'points': 0,
    'color': None,
    'attacksReceived': {},
    'teamName': None,
    'teamPlayerPositions': [],
    'myPosition': (),
    'gameMode': 1,
    'time': time.time(),
    'otherPlayers': {},
    'fanOf': None
}


enemySound = '/Users/praveen/Documents/PET/Games/Games/death_zone/Sounds/enemy_sound.mp3'
teamSound = '/Users/praveen/Documents/PET/Games/Games/death_zone/Sounds/team_sound.mp3'
winnerSound = '/Users/praveen/Documents/PET/Games/Games/death_zone/Sounds/winner.mp3'
introSound = '/Users/praveen/Documents/PET/Games/Games/death_zone/Sounds/intro.mp3'

def setup():
    #global address
    userDetails['name'] = input("enter your name ")
    while True:
        team = input("Select your team (Either A/B) ").lower()
        if team in ['a', 'b']:
            userDetails['teamName'] = team
            userDetails['color'] = teamColor[team]
            print("let the battle begin!!")
            break
        else:
            print("Invalid team")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))
        return sock
    except:
        raise Exception("unable to connect to address {address}:{port}".format(address = address, port = port))


def myPlayer(x, y, color):

    if x <= 0:
        x = 1
    if x + 20 >= display_width:
        x = display_width - 21
    if (y + 30) >= display_height:
        y = display_height - 31
    if y <= (display_height / 2):
        y = display_height / 2
    for tPlayerPos in userDetails['teamPlayerPositions']:
        if (x <= tPlayerPos[0] + 20) and (x + 20 >= tPlayerPos[0]) and (y + 30 >= tPlayerPos[1])\
                and (y <= tPlayerPos[1] + 30):
            x, y = userDetails['myPosition']
            break
    pygame.draw.rect(gameDisplay, color, (int(x), int(y), 20, 30), 0)
    userDetails['color'] = teamColor[userDetails['teamName']]
    return x, y


def showDetails():

    font = pygame.font.Font("/Users/praveen/Documents/PET/Games/FightMe/Fonts/CourierPrime.ttf", 15)
    info = 'POINTS: {points}      HEALTH: {health}'.\
        format(points = userDetails['points'], health = userDetails['health'])
    text = font.render(info, True, white)
    gameDisplay.blit(text, (5, (display_height + 20)))


def deadMessage():

    font = pygame.font.Font("/Users/praveen/Documents/PET/Games/FightMe/Fonts/CourierPrime.ttf", 30)
    info = 'YOU DIED !'
    text = font.render(info, True, yellow)
    gameDisplay.blit(text, ((display_width/2.5) - 20, display_height/2))


def waitForPlayers(musicController):

    if time.time() - userDetails['time'] > 2:
        info = ''
        userDetails['time'] = time.time()
    else:
        info = 'WAITING FOR PLAYERS TO JOIN ...'
    font = pygame.font.Font("/Users/praveen/Documents/PET/Games/FightMe/Fonts/CourierPrime.ttf", 18)
    text = font.render(info, True, white)
    gameDisplay.blit(text, ((display_width/3.5) - 20, display_height/2))
    if len(userDetails['otherPlayers']) == userDetails['gameMode'] * 2:
        musicController.stop()
        userDetails['flags']['startGame'] = True


def gameOver():
    font = pygame.font.Font("/Users/praveen/Documents/PET/Games/FightMe/Fonts/CourierPrime.ttf", 30)

    c = playSound(filePath = winnerSound)
    time.sleep(20)
    x = 0
    while x < 20:
        info = ''
        if x % 2 == 0:
            info = 'MALA DA! ANNAMALA !'
        text = font.render(info, True, orange)
        gameDisplay.blit(text, ((display_width / 2.5) - 20, display_height / 2))
        pygame.display.update()
        time.sleep(1)
    c.stop()



def shoot(x, y):
    x += 5
    pygame.draw.circle(gameDisplay, yellow, (int(x), int(y)), 5)


def playSound(filePath):
    pygame.mixer.init()
    pygame.mixer.music.load(filePath)
    pygame.mixer.music.play(0)
    return pygame.mixer.music

def sendMyPosition(x, y):
    sock.send(str.encode(str({userDetails['name']: [x, y, userDetails['teamName']]})))


def sendAttackPosition(x, y):
    sock.send(str.encode(str({userDetails['name']: [x, y, 'launch', userDetails['teamName']]})))


def setPlayers(attackPosition):
    userDetails['teamPosition'] = []
    if userDetails['flags']['startGame']:
        userDetails['flags']['gameOver'] = True
    for key, val in userDetails['otherPlayers'].items():
        #int(display_height - v[1] + 10)
        if val[2] == userDetails['teamName'] and key != userDetails['name']:
            playerX = int(val[0])
            playerY = int(val[1])
            userDetails['teamPosition'].append([playerX, playerY])
            playerColor = userDetails['color']
        elif key != userDetails['name']:
            playerColor = [v for k,v in teamColor.items() if k != userDetails['teamName']][0]
            playerX = int(display_width - val[0] - 20)
            playerY = int(display_height - val[1] - 30)
            if not ((playerX < -100 or playerX > display_width + 100) and
                    (playerY < - 100 or playerY > display_height + 100)):
                userDetails['flags']['gameOver'] = False

        if key != userDetails['name']:
            if (attackPosition[0] + 10 >= playerX) and (attackPosition[0] <= playerX + 20) and \
                    (attackPosition[1] + 5 >= playerY) and (attackPosition[1] - 5 <= playerY + 30):
                userDetails['points'] += 5
                userDetails['flags']['fired'] = False
                userDetails['attackPosition'] = (-1, -1)
                pygame.draw.rect(gameDisplay, white, (playerX, playerY, 20, 30), 0)
                print (userDetails)
            else:
                pygame.draw.rect(gameDisplay, playerColor, (playerX, playerY, 20, 30), 0)


def attackMe(myPosition):

    for key, val in userDetails['attacksReceived'].items():
        if val[3] == userDetails['teamName']:
            x = val[0]
            y = val[1]
        else:
            x = display_width - val[0] - 10
            y = display_height - val[1]
        if key != userDetails['name']:
            shoot(x, y)
            if (x + 10 >= myPosition[0]) and (x <= myPosition[0] + 20) and (y + 5 >= myPosition[1])\
                    and (y - 5 <= myPosition[1] + 30):
                userDetails['health'] -= 20
                userDetails['color'] = white
                if userDetails['health'] == 0:
                    userDetails['flags']['dead'] = True

    userDetails['attacksReceived'] = {}


def listenToServer():

    while True:
        data = sock.recv(1024)
        if data is not None:
            dataStr = data.decode('utf-8')
            dataList = dataStr.split('}')
            modifiedDataList = list(d + '}' for d in dataList)
            for modifiedData in modifiedDataList:
                try:
                    if len(modifiedData) > 5:
                        dataJson = json.loads(modifiedData.replace("'", "\""))
                except Exception as e:
                    raise Exception(e)
            for key, val in dataJson.items():
                if len(val) > 2 and val[2] == 'launch':
                    userDetails['attacksReceived'][key] = val
                else:
                    userDetails['otherPlayers'][key] = val


def runme():

    x = random.choice(range(1, int(display_width) - 1, 6))
    y = random.choice(range(int(display_height/2) + 1, int(display_height) - 1, 6))
    xChng = 0
    yChng = 0
    xprev = 0
    yprev = 0
    fx = 0
    fy = 0
    introSoundController = playSound(filePath = introSound)

    while True:

        gameDisplay.fill(bgColor)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sock.close()
                exit()

            if event.type == pygame.KEYDOWN and not userDetails['flags']['dead']:
                if event.key == pygame.K_LEFT:
                    xChng = -5
                if event.key == pygame.K_RIGHT:
                    xChng = 5
                if event.key == pygame.K_DOWN:
                    yChng = 5
                if event.key == pygame.K_UP:
                    yChng = -5
                if event.key == pygame.K_SPACE and not userDetails['flags']['fired'] \
                        and userDetails['flags']['startGame']:
                    userDetails['flags']['fire'] = True

            if event.type == pygame.KEYUP and not userDetails['flags']['dead']:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    xChng = 0
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    yChng = 0

        setPlayers(attackPosition = userDetails['attackPosition'])
        showDetails()

        if userDetails['flags']['fired']:
            shoot(fx, fy)
            fy += -10
            userDetails['attackPosition'] = (fx, fy)
            if fy > display_height or fy < 0:
                print (userDetails)
                userDetails['flags']['fired'] = False
            t11 = threading.Thread(target = sendAttackPosition, args = (fx, fy))
            t11.daemon = True
            t11.start()

        if not userDetails['flags']['startGame']:
            waitForPlayers(musicController = introSoundController)

        if userDetails['flags']['fire']:
            userDetails['flags']['fire'] = False
            userDetails['flags']['fired'] = True
            fx = x
            fy = y
            userDetails['attackPosition'] = (fx, fy)
            shoot(fx, fy)
            t12 = threading.Thread(target = sendAttackPosition, args = (fx, fy))
            t12.daemon = True
            t12.start()

        x += xChng
        y += yChng


        if not userDetails['flags']['dead']:
            attackMe(myPosition = (x, y))
            if x != xprev or y != yprev:
                t13 = threading.Thread(target = sendMyPosition, args = (x, y))
                t13.daemon = True
                t13.start()
            x, y = myPlayer(x = x, y = y, color = userDetails['color'])
            xprev = x
            yprev = y
            userDetails['myPosition'] = (x, y)

        else:
            attackMe(myPosition = (-30, -30))
            t13 = threading.Thread(target = sendMyPosition, args = (-1000, -1000))
            t13.daemon = True
            t13.start()
            deadMessage()

        if userDetails['flags']['gameOver']:
            print ('over')
            gameOver()
            pygame.quit()
            sock.close()
            exit()
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":

    sock = setup()
    pygame.init()

    display_width = 600
    display_height = 600
    gameDisplay = pygame.display.set_mode((display_width, display_height + 50))
    pygame.display.set_caption(userDetails['name'])

    clock = pygame.time.Clock()
    t1 = threading.Thread(target = listenToServer)
    t1.daemon = True
    t1.start()
    runme()
    pygame.quit()
    sock.close()
    exit()
