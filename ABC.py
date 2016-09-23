""" Simplistic "GUI Widgets" for a Pygame screen.
    
    Most widgets receive a 'surface' argument in the constructor.
    This is the pygame surface to which the widget will draw 
    itself when it's draw() method is called.
    
    Unless otherwise specified, all rectangles are pygame.Rect
    instances, and all colors are pygame.Color instances.
"""

import sys
import time
import pygame

from pygame import Rect, Color
from vec2d import vec2d

from game import *
import simpleanimation

from sys import exit
from random import randint

class WidgetError(Exception): pass
class LayoutError(WidgetError): pass





class Box(object):
    """ A rectangular box. Has a background color, and can have
        a border of a different color.
        
        Has a concept of the "internal rect". This is the rect
        inside the border (not including the border itself).
    """
    def __init__(self, 
            surface,
            rect,
            bgcolor,
            border_width=0,
            border_color=Color('black')):
       
       
        """ rect:
                The (outer) rectangle defining the location and
                size of the box on the surface.
            bgcolor: 
                The background color
            border_width:
                Width of the border. If 0, no border is drawn. 
                If > 0, the border is drawn inside the bounding 
                rect of the widget (so take this into account when
                computing internal space of the box).
            border_color:
                Color of the border.
        """
        
        
        self.surface = surface
        self.rect = rect
        self.bgcolor = bgcolor
        self.border_width = border_width
        self.border_color = border_color
        
        # Internal rectangle
        self.in_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
        
    def draw(self):
        pygame.draw.rect(self.surface, self.border_color, self.rect)        
        pygame.draw.rect(self.surface, self.bgcolor, self.in_rect)

    def get_internal_rect(self):
        
        """ The internal rect of the box.
        """
        
        return self.in_rect
        
        

class MessageBoard(object):
   
    """ A rectangular "board" for displaying messages on the 
        screen. Uses a Box with text drawn inside.
        
        The text is a list of lines. It can be retrieved and 
        changed with the .text attribute.
    """
    
    def __init__(self, 
            surface,
            rect,
            text,
            padding,
            font=('arial', 20),
            font_color=Color('white'),
            bgcolor=Color('gray25'),
            border_width=0,
            border_color=Color('black')):
        
        """ rect, bgcolor, border_width, border_color have the 
            same meaning as in the Box widget.
            
            text:
                The initial text of the message board.
            font:
                The font (a name, size tuple) of the message
            font_color:
                The font color
        """
        
        self.surface = surface
        self.rect = rect
        self.text = text
        self.padding = padding
        self.bgcolor = bgcolor
        self.font = pygame.font.SysFont(*font)
        self.font_color = font_color
        self.border_width = border_width
        
        self.box = Box(surface, rect, bgcolor, border_width, border_color)
        
    def draw(self):
        #Draw the surrounding box
        self.box.draw()
        
        # Internal drawing rectangle of the box 
        #
        #
        # Need a method that takes in a width and height of space required for text and padding
        # width, height = self.font.size(text)
        # Calculate required space for text+padding+border
        # utils.get_messagebox_coords(width, height, padding)
        # returns x, y, height, width?
        
        # Internal rectangle where the text is actually drawn
        text_rect = Rect(
            self.rect.left + self.border_width,
            self.rect.top + self.border_width,
            self.rect.width - self.border_width * 2,
            self.rect.height - self.border_width * 2)
            
        x_pos = text_rect.left
        y_pos = text_rect.top 
        
        # Render all the lines of text one below the other
        #
        for line in self.text:
            line_sf = self.font.render(line, True, self.font_color, self.bgcolor)
            
            #test if we can fit text into the MessageBoard + padding
            
            if ( line_sf.get_width() + x_pos + self.padding > self.rect.right or line_sf.get_height() + y_pos + self.padding > self.rect.bottom):
                raise LayoutError('Cannot fit line "%s" in widget' % line)
            
            self.surface.blit(line_sf, (x_pos+self.padding, y_pos+self.padding))
            y_pos += line_sf.get_height()





class Button(object):
	"""     Employs some crap from Box to draw a rectangular button, 
			has some methods to handle click events.
	"""
        
	# needs to be replaced.
	(UNCLICKED, CLICKED) = range(2)
        
	def __init__(self, surface, pos=vec2d(0, 0), btntype="", imgnames=[], text="", textcolor=(0,0,0), 
		textimg=0,padding=0, attached=""):
		print "In button init method"
		self.surface = surface
		self.pos = pos
		self.btntype = btntype
		self.imgnames = imgnames
		self.text = text
		self.textcolor = textcolor
		self.textimg = textimg
		self.padding = padding
		self.attached = attached
		self.state = Button.UNCLICKED
		self.toggle = 0 
			
		#load images
		self.imgs = []
		for name in self.imgnames:
			img = pygame.image.load(name).convert_alpha()
			#img = img.set_colorkey((255,255,255))
			#it would be nice to make the images transparent,
			#but it throws an error not worth fighting
			self.imgs.append(img)
                
		self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
		self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
		print "Image dimensions are: " + str(self.imgwidth) + ", " + str(self.imgheight)
		
		#creates a text label to place in the middle of the button
		font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(font.size(self.text))
		self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
                
                
	def draw(self):
		if self.btntype == "Close":
			self.surface.blit(self.imgs[0], self.rect)
		elif self.btntype == "Toggle":
			self.surface.blit(self.imgs[self.toggle], self.rect)
			if self.toggle == self.textimg:
				self.surface.blit(self.textOverlay, self.textRect)
			
 
	def mouse_click_event(self, pos):
		if self.btntype == "Close":
			if self._point_is_inside(vec2d(pos)):
				self.state = Button.CLICKED
		elif self.btntype == "Toggle":
			if self._point_is_inside(vec2d(pos)):
				self.state = not self.state
				self.toggle = not self.toggle
				self.imgwidth, self.imgheight = self.imgs[self.toggle].get_size()
				self.rect = Rect(self.pos.x, self.pos.y, self.imgwidth, self.imgheight)
				self.textRect = Rect(self.pos.x+self.imgwidth/2-self.textSize.x/2,self.pos.y+self.imgheight/2-self.textSize.y/2,0,0)
		elif self.btntype == "Action":
			if self._point_is_inside(vec2d(pos)):
				self.count = 100
				expl = simpleanimation.start()
				print "Action"
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.rect.x and mpos.x < self.rect.x+self.imgwidth:
			if mpos.y > self.rect.y and mpos.y < self.rect.y+self.imgheight:
				return True





class textEntry(object):
	""" allows for reading input from the user """        
	def __init__(self, surface, pos=vec2d(0, 0), size = vec2d(200,50), text="", textcolor=(0,0,0),padding=0, bgcolor = (255,255,255)):
		print "In textEntry init method"
		self.surface = surface
		self.pos = pos
		self.size = size
		self.text = text
		self.textcolor = textcolor
		self.padding = padding
		self.clicked = False
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.lastKey = ""
		self.delay = 1
		
		#creates a text label to place in the middle of the rectangle
		self.font = pygame.font.SysFont("Times New Roman", 25)
		self.textOverlay =  self.font.render(self.text,1,self.textcolor)
		self.textSize = vec2d(self.font.size(self.text))
		self.textRect = Rect(self.pos.x, self.pos.y, self.textSize.x, self.textSize.y)
                
	def draw(self):
		if self.clicked:
			if pygame.key.get_focused():
				pressed = pygame.key.get_pressed()
				for i in range(len(pressed)):
					if pressed[i] == 1:
						key = pygame.key.name(i)
						if self.lastKey == key and self.delay <= 1:
							#delay time please fix
							self.delay += .4
						elif len(key) == 1 and self.font.size(self.text)[0] <= self.size.x:
							self.text+= key
							self.delay = 0
							self.lastKey = key
						elif key == "tab":
							self.text += "    "
							self.delay = 0
							self.lastKey = key
						elif key == "space":
							self.text += " "
							self.delay = 0
							self.lastKey = key
						elif key == "backspace":
							self.text = self.text[:-1]
							self.delay = 0
							self.lastKey = key
						
						self.textOverlay = self.font.render(self.text,1,self.textcolor)

		pygame.draw.rect(self.surface, (255,255,255), self.rect)
		self.surface.blit(self.textOverlay, self.textRect)
			
	def mouse_click_event(self, pos):
		if self._point_is_inside(vec2d(pos)):
			self.clicked = not self.clicked
        
	def _point_is_inside(self, mpos):
		if mpos.x > self.pos.x and mpos.x < self.pos.x+self.size.x:
			if mpos.y > self.pos.y and mpos.y < self.pos.y+self.size.y:
				return True
				
				
				
				





class movingImg(object):
	def __init__(self, surface, image, pos=vec2d(0,0), speed=vec2d(1,0), gravity=1):
		self.surface = surface
		self.surfaceSize = vec2d(self.surface.get_size())
		self.image = pygame.image.load(image)
		self.pos = pos
		self.speed = speed
		self.gravity = gravity
		self.size = vec2d(self.image.get_size())
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
	
	def draw(self):
		if self.pos.x + self.size.x > self.surfaceSize.x or self.pos.x < 0:
			self.speed.x *= -1
		if self.pos.y + self.size.y > self.surfaceSize.y or self.pos.y < 0:
			self.speed.y *= -1
		self.pos.x += self.speed.x
		self.pos.y += self.speed.y
		self.rect = Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
		self.surface.blit(self.image, self.rect)







class Scene(object):

	def enter(self):
		print "Welcome to the Chronicles of Narnia."
		print "You are about to embark on the journey of,"
		print "'The Magicians Nephew'"
		
		
class Engine(object):

	def __init__(self, scene_map):
		self.scene_map = scene_map
		
	def play(self):
		current_scene = self.scene_map.opening_scene()
        last_scene = self.scene_map.next_scene('finished')
        
        while current_scene != last_scene:
            next_scene_name = current_scene.enter()
            current_scene = self.scene_map.next_scene(next_scene_name)
            
            
        current_scene.enter()
		
class Death(Scene):

	quips = [
		"The evil witch has killed you"
	]

	def enter(self):
		print Death.quips[randint(0, len(self.quips)-1)]
		exit(1)

# This is a game that should play from both first person and top down view?
# Think Zelda (some scenes require top down view like when in a building)
# There should be a home screen to show your inventory (IE: green, yellow rings) 
		
# First Scene
# Introduction to Digory and Polly
# Digory has to find Polly to unlock the next Scene
# If Digory cannot find Polly he will break down and cry
# If Digory tries to leave from the gate which he came in from, he will return to same Scene

class Gardens(Scene):

	def enter(self, Polly):
		print "You 'Digory' have moved into the city and need to find a friend to play with"
		
		choice = raw_input ('> ')
		if choice == 'find friend':
			print "Why are you sad Digory? Don't you want to play?"
			
			#How to include an action and sound effect?		
			#action == door unlocks, sound effect
			
			#How to use key strokes walk to door?
			#Is it okay if I use an If statment inside of another If statment?
			#Is there a better way?
			
			decision = raw_input ("> ")
			if decision == 'play':
				# key music and switch to next_scene
				next_scene(self, Attic)
		
		elif choice == ' ':
			return current_scene(self, Gardens)
		

class Attic(Scene):

	def enter(self, Polly):
		print "Digory: 'What is this place?'"
		print "Polly: 'I am not sure but I think we are inbetween the houses in"
		print "some kind of secret passage way to the Attic.'"
		print "Digory: 'What a creepy place to be!'"
		print "Polly: 'Yeah I am starting to feel chills!'...(Hears Sound)"
		print "'WHAT's THAT NOISE!'"
		
		# Digory and Polly are both breathing heavily now.
		# Every 15 seconds Polly or Digory (alternating) say "I'm Scared"
		# If both of them do not move within 30 seconds then Digory starts crying!"
		# Think "Left for dead" creepy feeling.
		
		# They must find a vase with key inside to unlock a locked door at the end of the
		# attic. 
		# This requires a grab function, equip function, and use function.
		# Zelda type functions
		
		grab = raw_input ('> ')
		if grab == 'grab vase':
			print "You have found a key (play sound effect and show key)"
		
		#How to incorporate feedback messages?
		#elif grab == grab vase (empty)
			#print "There used to be something important in here."
		
		# only if found key then can go to inventory to equip it
		# only if key is equiped then can use it
		action = raw_input ('> ')
		if key is equiped and action == 'open door':
			print "This key seems to fit perfectly"
			# There should be a visual/sound effect of door unlocking.
			# Switch to next scene
			next_scene(self, StudyRoom)
			
		elif key is not equiped and action == 'open door':
			print "You need something to unlock this door."
			
# Polly and Digory are in a passage and know how to get home but see a dim light from
# underneath a strange door. (The StudyRoom)			
class StudyRoom(Scene):

	def enter(self):
		print "Oh I know where we are says Digory!"
		print "Hey whats the light coming from that door? says Polly"
		print "Digory replies: 'Lets go look'"
		
		choice = raw_input ('> ')
		if choice == 'open door 1':
			print "Polly and Digory quietly opened the door and saw Uncle Andrew!"
			print "Before they could say anything they saw two guinea pigs vanish into"
			print "'thin air'!"
			print "Uncle Andrew! Digory exclaims; and before he relised it Uncle Andrew had"
			print "a hold of both of them!"
			print "OH PERFECT! Uncle Andrew says with a mysterious laugh."
			print "I have a present for both of you. Uncle Andrew hands them a cloth with"
			print "something inside."
			print "Polly was more eager than Digory thus she opened it first and saw a"
			print "shiny yellow ring."
			print "When she touched it she vasnished into 'thin air' just like the" 
			print "guinea pigs."
			print "Digory was shocked and scared by what he just saw!"
			print "Digory was about to inquire as Uncle Andrew began to explain: If you"
			print "ever want to see her or the two guinea pigs again you must take this"
			print "yellow ring to go to where she has gone and take these two green rings"
			print "to come back!"
		
		# to prevent a bug there should be a way to prevent from leaving the room without
		# having completed the mission at hand. IE: returning with the Witch
		
			action = raw_input ('> ')
			if action == 'yellow ring':
				print "Digory finds himself in a wormhole and within mere seconds he falls"
				print "on soft grass."
				next_scene(self, Sleepywoods)
			elif action == 'green ring':
				print "That is strange nothing happened." 		
				
			
		#action is wrong so should take them back to the Attic scene
		elif action == 'open door 2':
			print "That's strange how did we get here?"

class Sleepywoods(Scene):

	def enter(self):
		action = raw_input ('> ')
		if action == 'find Polly':
			print "Digory: 'Polly is that you!? I have been looking all over for you'."
			print "Digory: 'Wake up Polly do not fall asleep again!'"
			print "Polly: 'Where are we?'"
			print "Digory: 'I do not know but Uncle Andrew tricked us and now I am here to'"
			print "Digory: 'take you back!'"
			print "Polly: 'Okay! but let us take a look around first before we go back'."
			print "Digory: 'what are all of these pools?'"
			print "Polly: 'I don't know but I think they lead to another world. As if we'"
			print "Polly: 'are in a woods between worlds'."
			
			action = raw_input ('> ')
			if action == 'jump in pool':
				print "AHHHHHH! There is darkness, and then slowly there is light!"
				next_scene(self, Charn)
			

class Charn(Scene):

	def enter(self):
		print "Digory: 'Wow this place is cold and it looks like everything is dead!'"
		print "Polly: 'Maybe there are people inside the city because it is so cold outside?'"
		print "Polly: 'Lets go in to check, unless you are scared and want to go back?'"
		print "Digory: 'No I am not scared, unless you are scared?'"
		print "Polly: 'No I am not scared.'"
		print "Digory: 'Lets go inside then.'"
		
		# I am trying to include more choices for a better UX
		# How to allow free movement and exploration within each scene?
		# Does my raw input have to be so 'Limited'?
		# How do I include more sideline stories to make the game seem less linear?
		action = raw_input ('> ')
		if action == 'walk into city':
			# animated action == go to the city center
			print "There seems to be something wrong with this city, everything is so quiet"
			print "It seems like everything is dead."
			print "There is a big dining room up ahead."
			print "Maybe there is someone there."

			
			
			chioce = raw_input ('> ')
			if choice == 'dinning room':
				# there should be a change in visual/sound effect when entering room
				# animated action == walk into dining room
				print "Digory: 'Wow look Polly, what happened here!?'"
				print "Digory: 'Why are there statues sitting at the dinning table?'"
				print "Polly: 'I do not know but it seems like they were alive'"
				print "Polly: 'and became frozen instantly'."
				print "Polly: 'The head of the table seems to be happy but'"
				print "Polly: 'the farther you go down the sadder they look'."
				print "Digory: 'Look at that beautiful lady at the end! She must be the queen'."
				
				# How can you put an object in plane sight, waiting for impulse to enacted
				# upon. IE: Zelda you can click to read a sign and then after 
				# you can perform an action to unlock that puzzle
				print "Polly: 'Look here Digory, there is a hammer with a bell and this'"
				print "Polly: 'sign says 'Those who dare to strike the bell'"
				print "Polly: 'or else you will go to hell'."

				
				
				action = raw_input ('> ')
				if action == 'ring bell':
					print "Despite protests from Polly, Digory rings the bell."
					print "The ground began to shake and there were strange lights in"
					print "the sky. Before Polly and Digory could run out of there one"
					print "of the statues began to move."
					print "It was the queen. She slowly came to life and seemed to be"
					print "Taller and Stronger than Digory had imagined before!"
					print "Witch: 'Who has rung the bell and awakened me from my slumber!?'"
					print "Witch 'Where is my faithful servant?'"
					print "Digory stepped out into the light, trembling with fear."
					print "He thought he might get a prize from this awe powerful queen."
					print "Witch: 'Well, well what do we have here, a child it seems'."
					print "Witch: 'Where is your offering, lest I might eat you?'"
					print "Digory: 'I don't know about offering but here is my friend Polly'"
					print "Witch: 'Oh so you want me to eat your friend!?'"
					print "Digory: 'No, No! I mean I am the one who rang the bell'" 
					print "Digory: 'even though she told me not to'."
					print "Witch: 'So I should eat her because she is defiant!'"
					print "Polly: 'No please do not eat me!'"
					print "Digory: 'No my queen I can go get food and bring it back for you'."
					print "Digory and Polly knew that they must leave immediately"
					print "before something bad happens to either of them!"
					print "They both reached into their pockets at the same time,"
					print "but before they could touch their green rings the Queen grabbed"
					print "them both by their coats!"
					print "AHHH!"
					next_scene(self, StudyRoom)		

		
class StudyRoom(Scene):

	def enter(self):
		print "In a blink of an eye they were back in Uncle Andrew's study room."
		print "Digory thought to himself 'that is strange it seems as if no time has passed"
		print "at all even though they had been gone for what seemed for hours!"
		print "Polly: 'Oh no Digory the Witch grabbed our coats and came with us'."
		print "Little did polly know that the Witch no longer had her powers in their world."
		print "Witch: 'Now you must be my servent!" "speaking to Uncle Andrew'"
		print "Uncle Andrew: 'Why yes ofcourse I am here at your service!'"
		print "Uncle Andrew: 'How may I help you?" "speaking in the most curtious way he'"
		print "Uncle Andrew: 'possible, because he was in awe of such a beautiful woman'."
		print "Witch: 'Fetch me a chariot and take me out of this filth!'"
		print "Witch: 'It is time to rule this place you call 'Earth'!'"
		print "Uncle Andrew: 'Yes ma'm right away!'"
		
		action = raw_input ('> ')
		if action == 'open door':
			next_scene(self, England)
			
class England(Scene):

	def enter(self):
		print "Uncle Andrew quickly rushed outside and called a cab."
		print "Uncle Andrew: 'Take us through the streets of England to all the fancy stores'."
		print "For that was what Uncle Andrew thought the beautiful woman wanted."
		print "Little did he know that the beautiful woman was actually a witch in another world."
		print "Cabby: 'Here we are sir. That would be 5 pence'."
		print "Witch: 'Muhaha you are a funny little rodent arent you!'"
		print "The Witch walks into the store and grabs all of the jewelry."
		print "Uncle was paralized in shock by what just happened and appologized to the owner."
		print "Witch: 'This is great! Take me to next place!'"
		print "At this time the sirens of the police were just down the street"
		
		action = raw_input ('> ')
		if action == 'run away':
			next_scene(self, Crash)
		elif action == 'stay':
			print "The police have arrested the Witch!"
			print "She stays and rules over 'Earth' until all things die!"
			return Death
		
		
class Crash(Scene):

	def enter(self):
		print "Police: 'Pull over now or you will face capitol punishment!'"
		print "Witch: 'NEVER MUHAHAHA!'"
		print "Cabby: 'We should listen to what they say. Oh nooo!'"
		print "The cabby lost control of the cab and crashed right into a lampost"
		print "oustide of Digorys house."
		print "Digory: 'Look Polly they came back!'"
		print "Polly: 'Oh no Digory it looks like trouble. Look at what we have done'."
		print "Polly: 'We should take her back to her world as soon as possible before'"
		print "Polly: 'She destorys our world just as she has destroyed hers!'"
		print "Digory: 'You are right but how? There are Police and rioters everywhere!'"
		
		choice = raw_input ('> ')
		if choice == 'go outside':
			print "Digory: 'No polly its too dangerous. I cannot do it'."
			print "Polly: 'Grow a pair of balls and fix the problem you started!'"
			
			action = raw_input ('> ')
			if action == 'grab the Witch':
				print "Polly and Digory run accros the lawn to the lamp post with bullets"
				print "flying by them left and right. Digory see's his uncle is in danger"
				print "and helps him up! Then Digory and Polly grab on to the Witch."
				
				equip = raw_input ('> ')
				if equip == 'green ring':
					print "You put on the wrong rings and while fumbling for the other"
					print "ring you get shot by a stray bullet!"
					print "Game Over"
					return Death
					
				elif equip == 'yellow ring':
					print "Digory: 'Oh no Polly look what happened!'"
					print "Digory and Polly did not realize that the Witch was holding"
					print "onto the cab and the lamp post. In doing so she brought the"
					print "Cabby, Uncle Andrew, the cab and lampost with her."
					next_scene(self, Sleepywoods)

class Sleepywoods(Scene):

	def enter(self):
		print "Polly and Digory look at each other knowing that only they have been in"
		print "the sleepy woods before. They gave each other a look and quick glance"
		print "at the pool in front of them."
		print "Digory: 'Now Polly!'"
		
		action = raw_input ('> ')
		if action == 'jump in pool':
			print "They both grabbed the Witch and jumped into the pool thinking that it would"
			print "go back to the abandoned city where the Witch came from!"
			print "But no that is not at all what happened."
			next_scene(self, Newworld)

class Newworld(Scene):

	def enter(self):
		print "It was strange, cold and Dark. Polly cold feel Digory grabbing her hand"
		print "but could not see him."
		print "Polly: 'Digory! she whispered'"
		print "Digory: 'I am right here!'"
		print "Then all of sudden there was bring white light that made them all tremble."
		print "And then right before their eyes they could see water and mountains forming."
		print "They saw an entire new world come to life!"
		print "The Witch thought to herself 'This is perfect!' and quietly left."
		
		action = raw_input ('> ')
		if action == 'search':
			print "Where did she go they all thought! But were overcome with a great sleep"
			print "for the Witch had cast a spell on them."
			next_scene(self, Narnia)
			
class Narnia(Scene):
		
	def enter(self):
		print "As they all woke up from their sleep they saw a lion speaking in familiar"
		print "toung. He was speaking to trees and plants and animals."
		print "Strange they all thought because it sounded as if the animals were speaking"
		print "to the Lion also!"
		print "Digory: 'Common guys, quickly get up! The Lion is comming this way!'"
		print "Aslan: 'Hello my name is Aslan. What brings you to my world?'"
		print "The others were so terrified by the whole seen that they dare not even move."
		print "Digory: 'Responded, hello Aslan, I am Digory and this is Polly. We came here'"
		print "to... 'he thought to himself it doesn't feel right to lie I should tell him"
		print "the truth' get rid of this evil Witch who destroys everything in her path!"
		print "Aslan: 'Oh so you are the one who let her into my world!'"
		print "Aslan: 'Well then it just seems right that you would be the one to fix what'"
		print "you have done! How dare you bring evil to my world!"
		print "Digory: 'I am terribly sorry Aslan! I will do anything to make it up to you'."
		print "Aslan: 'Here take this fine horse 'It was the cabbys horse' and go up to the'"
		print "tallest mountain and get an apple from that tree and bring it back to me."
		print "Do not eat from that tree or take something that is not yours!"
		print "Digory: 'Yes sir'."
		print "Aslan at that moment took a deep breath and blew on the horses face."
		print "Instantly the horse transformed before everyones eyes and grew wings!"
		print "They all stood in awe of what just Happened."
		print "Aslan: 'Now GO!'"
		
		choice = raw_input ('> ')
		if choice == 'mountain':
			next_scene(self, GardenMountain)
		elif choice == 'stay':
			print "You pissed off Aslan and got struck by lightning!"
			return Death
			
class GardenMountain(Scene):

	def enter(self):
		print "Polly: 'Do you really trust Aslan? How will we defeat the Witch? She is much'"
		print "more powerful than the both of us."
		print "Digory: 'I dont know Polly but I do know we are the ones who brought the'"
		print "Witch here. We have to at least try Polly!"
		print "They were surprised by how quickly they got to the long distant mountains."
		print "When they were almost there they felt a strange cold come over them. They"
		print "knew immediately that the Witch was there and cast a spell over the place."
		print "They decided to try and sneak into the garden at the top and leave as"
		print "quick as possible. 'In and Out' the both said to each other."
		
		action = raw_input ('> ')
		if action == 'enter garden':
			# play music on entrance and set boundaries for final level
			# Objective is to distract the queen and grab a fresh apple"
			print "The Witch looks different. As if something has come over her."
			print "Polly: 'She must have had some of the apples. They probably poisoned her'."
			print "The Witch had gained in strength but her eyes looked weak as if they"
			print "were full of pain."
			print "Digory: 'Quick Polly, climb the tree!'"
			
			action = raw_input ('> ')
			if action == 'run behind Witch':
				print "The Witch can't see you now. Quick grab an apple and throw it"
				print "to Polly!"
				
				action = raw_input ('> ')
				if action == 'throw apple':
					print "The Witch turned right after Digory threw the apple and did not"
					print "see them take it."
					print "Witch: 'What are you two up to!? Will you not stay here with me'"
					print "as my servants and we can rule over this new world together."
					print "Polly: 'No thank you!'"
					print "Witch: 'Why not!?'"
					print "As Digory was escaping he said, because staying here and eating"
					print "this fruit will only make you sad and full of pain!"
					print "Little did Digory know that that was how the Witch really felt!"
					
					action = raw_input ('> ')
					if action == 'run away':
						print "Digory: 'Hey Witch! Look, what is that! (pointing his"
						print "finger in the other direction)'."
						print "The Witch turned around and looked but could not see anything"
						print "Witch: 'What do you mean? I do not see anything!'"
						print "(little did she know that both Digory and Polly were already"
						print "on the horse)"
						print "In the distance they heared 'I will get you for this!'"
						print "But Digory and Polly were just so glad to get out of there"
						print "as quick as they could!"
						print "Polly: 'Few that was close! What now? are we safe?'"
						print "Digory: 'I do not know Polly but I think Aslan is good, and"
						print "He will protect us no matter what happens. Lets go bring"
						print "Him this apple like he asked us to'."
						next_scene(self, Narnia)
class Narnia(Scene):

	def enter(self):
		print "Aslan: 'Good Digory and Polly, I knew I could trust you both!'"
		
		action = raw_input ('> ')
		if action == 'give apple':
			print "Digory: 'Wow look Polly, Aslan put the apple into the ground and it grew"
			print "into a tree instantly!'"
			print "Aslan: 'Yes Digory, because my Word is the Truth and whatever I say will"
			print "come to be'."
			print "Aslan: 'Now Digory I know that the Witch tempted you to take an apple to"
			print "bring home to your mother. Just like the Witch anything that you"
			print "take out of selfish desire without permission will only lead to pain"
			print "and sadness. However what you do not know is what you recieve in good"
			print "will and honest character will bring you joy and life. It is the root"
			print "of how you get the apple that will give you the desires of your heart'."
			print "Aslan: 'Do you understand?'"
			print "Digory: 'Yes, Great Aslan'."
			
			choice = raw_input ('> ')
			if choice == 'ask':
				print "Digory: 'Great Aslan, may I have an apple to take to my sick mother?'"
				print "Aslan: 'Yes ofcourse you can my boy! Here take this one'."
				
				print "Aslan: 'The cabby has requested for me to bring his wife to this world."
				print "I have decided that they shall be King and Queen to rule over the land,"
				print "and take care of all the plants and animals."
				print "You however must go home immediately to save your mother. Please"
				print "take your Uncle Andrew with you, he is such a bother!'"
				print "Digory: 'Yes Great Aslan! Anything you wish'."
				
				choice = raw_input ('> ')
				if chioce == 'Go':
					print "Aslan blows on Digory, Polly, and Uncle Andrew. They all go back"
					print "to whence they came from. Home!"
					next_scene(self, StudyRoom)
					
			elif choice == 'take':
				print "Aslan: 'YOU EVIL LITTLE BOY!'"
				print "Aslan has struck you with lightning and you have died!"
				return Death

class StudyRoom(Scene):

	def enter(self):
		print "They all came back in one piece! And boy oh boy was Uncle Andrew happy to"
		print "be home! But Digory has something else entirely on his mind. Digory ran out"
		print "of the study room to find his mother at her bed side."
		print "Digory was so filled with excitment that he wantted to tell her everything,"
		print "but his mother was too weak to even open her eyes."
		print "He started crying out of the pain and sorrow he had for his mother. Then he"
		print "remembered the gift that Aslan had given him! He was sure this would help!"
		
		action = raw_input ('> ')
		if action == 'give apple':
			print "Digory helped his mother sit up straight and gave her a piece of the"
			print "delicious apple he got from Aslan. As soon as it touched her lips her"
			print "skin started to change color! Digory could not believe it! Right infront"
			print "of his own eyes, his mother was getting a little bit better. The more"
			print "she had of the apple the better she got. By the time she finished eating"
			print "the apple she was full of color and youth. She said 'I feel like I am"
			print "young again!' and by this Digory knew that his mother had gotten all"
			print "better. There was no more sign of the sickness in her."
			print "Digory and Polly thought maybe they should try to bury the apple and"
			print "the rings in the back yard."
			
			action = raw_input ('> ')
			if action == 'plant apple':
				print "Sure enough as soon as they did, a small tree had sprung up."
				print "They knew this tree would bring them good fruit!"
				print "It was a magical tree for sure!"
				
				print "Digory and Polly grew fond of their friendship!"
				print "Their adventures had truely had an impact on them and shared"
				print "in the joy of recounted the stories with each other frequently."
				next_scene(self, Mansion)

class Mansion(Scene):

	def enter(self):
		print "As the years went on Digorys family had moved out of the city and into"
		print "the country side where they was more peace and calm."
		print "In his old age Digory had asked his family to cut down the great apple tree."
		print "By that time it had already grown quite big and blew down in a storm!"
		print "It was a sad moment for Digory since he had grown so fond of it but"
		print "nonetheless it was cut down and his family decided that the wood would"
		print "make for a good wardrobe! And so they did."
		print "THE END!"
		return 'finished'
					
class Map(object):

    def __init__(self, start_scene):
        pass

    def next_scene(self, scene_name):
        pass

    def opening_scene(self):
        pass


a_map = Map('Gardens')
a_game = Engine(a_map)
a_game.play()