
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import time
from copy import deepcopy

size = 4

class Estimator:
	def estimate(self, precells, postcells, action, score):
		for i in range(size):
			score += self.__estimate_line([postcells[i][j] for j in range(size)])
			score += self.__estimate_line([postcells[j][i] for j in range(size)])
		return score

	def __estimate_line(self, line):
		monotone, adjoin = 0, 0
		for i in range(size - 1):
			if line[i + 1] > line[i]:
				monotone += line[i + 1] + line[i]
			else:
				monotone -= line[i + 1] + line[i]
			if line[i + 1] == line[i]:
				adjoin += line[i]
		return abs(monotone) * .3 + adjoin

class Auto2048:
	def __init__(self, url, estimator):
		self.browser = webdriver.Firefox()
		self.browser.get(url)
		self.estimator = estimator

	def get_cells(self):
		tiles = self.browser.find_elements_by_class_name('tile')
		self.cells = [[0 for i in range(4)] for i in range(4)]

		for tile in tiles:
			attr = tile.get_attribute('class').split()
			value = int(attr[1].split('-')[1])
			x = int(attr[2].split('-')[3]) - 1
			y = int(attr[2].split('-')[2]) - 1
			self.cells[x][y] = value

	def AI(self):

		self.get_cells()
		self.Print(self.cells)

		action, actionname = '', ''
		moveable = False
		
		strategies = [	{'fun': self.try_up, 'action': Keys.UP, 'name': 'Up'}, 
						{'fun': self.try_down, 'action': Keys.DOWN, 'name': 'Down'}, 
						{'fun': self.try_left, 'action': Keys.LEFT, 'name': 'Left'}, 
						{'fun': self.try_right, 'action': Keys.RIGHT, 'name': 'Right'}]
		for strategy in strategies:
			result = strategy['fun']()
			estimation = self.estimator.estimate(self.cells, result['cells'], strategy['name'], result['score'])
			if result['moveable'] and (moveable == False or max_estimation < estimation):
				action = strategy['action']
				max_estimation = estimation
				moveable = True
				actionname = strategy['name']

		if not moveable:
			return False

		self.browser.find_element_by_class_name('grid-container').send_keys(action)
		print 'Action: ', actionname
		return True

	def move_left(self, cells):
		moveable = False
		score = 0
		for x in range(size):
			pre = 0
			for y in range(size):
				if cells[x][y]:
					cells[x][pre] = cells[x][y]
					if y != pre:
						moveable = True
						cells[x][y] = 0
					pre += 1
			for y in range(size - 1):
				if cells[x][y] and cells[x][y] == cells[x][y + 1]:
					cells[x][y] += cells[x][y]
					score += cells[x][y]
					cells[x][y + 1] = 0
					moveable = True
			pre = 0
			for y in range(size):
				if cells[x][y]:
					cells[x][pre] = cells[x][y]
					if y != pre:
						moveable = True
						cells[x][y] = 0
					pre += 1
		return {'moveable': moveable, 'score': score, 'cells': cells}
	
	def try_left(self):
		cells = [[self.cells[i][j] for j in range(size)] for i in range(size)]
		return self.move_left(cells)

	def try_right(self):
		cells = [[self.cells[i][size - 1 - j] for j in range(size)] for i in range(size)]
		result = self.move_left(cells)
		result['cells'] = [[result['cells'][i][size - 1 - j] for j in range(size)] for i in range(size)]
		return result

	def try_up(self):
		cells = [[self.cells[j][i] for j in range(size)] for i in range(size)]
		result = self.move_left(cells)
		result['cells'] = [[result['cells'][j][i] for j in range(size)] for i in range(size)]
		return result
	
	def try_down(self):
		cells = [[self.cells[size - 1 - j][i] for j in range(size)] for i in range(size)]
		result = self.move_left(cells)
		result['cells'] = [[result['cells'][j][size - 1 - i] for j in range(size)] for i in range(size)]
		return result

	def __del__(self):
		self.browser.close()

	def Print(self, cells):
		print 
		for x in range(size):
			for y in range(size):
				print '%5d' % cells[x][y], 
			print 

if __name__ == '__main__':
	url = 'file://' + os.path.abspath('2048/index.html')
	# url = "http://gabrielecirulli.github.io/2048/"
	auto2048 = Auto2048(url, Estimator())
	while auto2048.AI():
		time.sleep(0.2)
	time.sleep(10)
WebElement