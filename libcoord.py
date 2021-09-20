
import bisect, copy


class ObjCoord(object):
    
    color_basket = ["deep sky blue", "steel blue", "gold", "goldenrod",
                    "indian red", "coral", "red", "maroon", "dark violet",
                    "lime green", "forest green", "deep pink"]
    basket_index = 0
    
    
    
    def __init__(self, x = [], y = [], label = "Unknown", color = None):
        
        if (x != []):
            if(x != sorted(x) or x[0] > x[-1]):
                raise ValueError("x must be in strictly ascending order!")
        
        self.x = x
        self.y = y
        self.label = label
        self.color = color
        
        if color == None:
            self.color = ObjCoord.color_basket[ObjCoord.basket_index]
            ObjCoord.basket_index = (ObjCoord.basket_index + 1) % len(ObjCoord.color_basket)


    def changeColor(self, color):
        self.color = color       
            
    
    def generateSynthetic(self, begin = 350, end = 750, span = 0.4):
        
        intervals = zip(self.x, self.x[1:], self.y, self.y[1:])
        self.slopes = [(y2 - y1) / (x2 - x1) for x1, x2, y1, y2 in intervals]
                
        points = int((end-begin) // span +1)
        
        synthetic_x = []
        synthetic_y = []
        
        for i in range(points):
            item = round(begin + span*i, 2)
            synthetic_x.append(item)
            synthetic_y.append(self.interpolate(item))
            
        return ObjCoord(synthetic_x, synthetic_y, self.label)



    def interpolate(self, x):
        
        if x <= self.x[0]:
            return self.y[0]
        elif x >= self.x[-1]:
            return self.y[-1]
        
        # The purpose of Bisect algorithm is to find a position in
        # list where an element needs to be inserted to keep the list sorted
        
        # bisect_left(list, num) returns the position in the sorted list, where
        # the number passed in argument can be placed so as to maintain the resultant list
        # in sorted order. If the element is already present in the list, the left most
        # position where element has to be inserted is returned.
        i = bisect.bisect_right(self.x, x) -1
        return self.y[i] + self.slopes[i] * (x - self.x[i])
        
    
    
    def subtract(self, fc, label, color):
        
        if(len(self.x) != len(fc.x)):
            print("Can't subtract datasets of different length")
            return
        
        new_y = []
        for i in range(len(self.x)):
            new_y.append(self.y[i] - fc.y[i])
                       
        return ObjCoord(copy.deepcopy(self.x), new_y, label, color = color)
    
    
    
    def getString(self):
    
        if(len(self.x) != len(self.y)):
            print("Strange! self.x != self.y")
            return
        
        to_print = self.label + " coordinates:\n"
        for i in range(len(self.x)):
            print("x" + str(i) + ": " + str(self.x[i]) + " ; " + "y" + str(i) + ": " + str(self.y[i]) + "\n")
            
            