import tkinter, tkinter.font, platform


class ObjPlot(tkinter.Canvas):
    
    
    def __init__(self, root, title = "", subtitle = "",
                 pixelWidth = 500, pixelHeight = 200, # pixels
                 beginX = 350, endX = 750,
                 beginY = 0, endY = 1,
                 labelX = "X", labelY = "Y",
                 bg = "white", span = 50,
                 xTicks = 10, yTicks = 5,
                 precision = 20):
        
        # Variables passed
        self.title = title
        self.subtitle = subtitle
        self.pixelWidth = pixelWidth
        self.pixelHeight = pixelHeight
        self.beginX = beginX
        self.endX = endX
        self.beginY = beginY
        self.endY = endY
        self.labelX = labelX
        self.labelY = labelY
        self.bg = bg
        self.span = span
        self.xTicks = xTicks
        self.yTicks = yTicks
        self.precision = precision
        
        
        # Widget stuff
        tkinter.Canvas.__init__(self, root, width= self.pixelWidth, height= self.pixelHeight, bg = self.bg)
        
        self.bind( "<Configure>", self.__onResize)
        self.bind( "<Button-1>", self.__onStartRect )
        self.bind( "<ButtonRelease-1>", self.__onStopRect )
        self.bind( "<B1-Motion>", self.__onMovingRect )
        if platform.system() == "Darwin": # = MacOS
            self.bind( "<Button-2>", self.__onRestoreAxis )
            self.bind( "<Double-Button-2>", self.__onCleanPlot )
        else:
            self.bind( "<Button-3>", self.__onRestoreAxis )
            self.bind( "<Double-Button-3>", self.__onCleanPlot )

        
        # Variables not passed:
        self.__plot_list = []
        
        self.rectX_start = 0
        self.rectY_start = 0
        self.rectX_end = 0
        self.rectY_end = 0
        self.rect_id = None
        
        self.zoomX_start = self.beginX
        self.zoomY_start = self.beginY
        self.zoomX_end = self.endX
        self.zoomY_end = self.endY
        
        self.beginX_current = self.beginX
        self.endX_current = self.endX
        self.beginY_current = self.beginY
        self.endY_current = self.endY
        
        
        # FONTS
        if platform.system() == "Windows":
            self.font_normal = tkinter.font.Font(family="Verdana", weight = "normal", size = 10)
            self.font_bold = tkinter.font.Font(family="Verdana", weight = "bold", size = 10)
        elif platform.system() == "Linux":
            self.font_normal = tkinter.font.Font(family="Helvetica", weight = "normal", size = 10)
            self.font_bold = tkinter.font.Font(family="Helvetica", weight = "bold", size = 10)
        elif platform.system() == "Darwin": # "Darwin" for MacOS
            self.font_normal = tkinter.font.Font(family="Verdana", weight = "normal", size = 12)
            self.font_bold = tkinter.font.Font(family="Verdana", weight = "bold", size = 12)
            
        


    def __onCleanPlot(self, event):
        
        self.cleanPlot()
        
        
        
    def cleanPlot(self):
        
        self.delete("all")
        self.__plot_list.clear()
        self.__redrawAxis()
    
    
    
    def __onRestoreAxis(self, event):
        
        self.beginX_current = self.beginX
        self.endX_current = self.endX
        self.beginY_current = self.beginY
        
        self.__drawCanvas()
    
    
    
    def __onResize(self, event): # Every time window is resized, clean the canvas and re-plot
        
        self.pixelWidth = event.width
        self.pixelHeight = event.height
        
        self.__redrawCanvas()
        
        
        
    def __onStartRect(self, event):
        if (event.x <= self.span or event.x >= (self.span + self.lengthX) or
            event.y <= self.span or event.y >= (self.span + self.lengthY)):
            self.rect_id = None
            return
        
        self.rectX_start = event.x
        self.rectY_start = event.y
        
        self.rect_id = self.create_rectangle(self.rectX_start, self.rectY_start,
                                             self.rectX_start, self.rectY_start)
        


    def __onMovingRect(self, event):
        
        if self.rect_id == None:
            return
        
        if (event.x <= self.span or event.x >= (self.span + self.lengthX) or
            event.y <= self.span or event.y >= (self.span + self.lengthY)):
            return
        
        self.rectX_end = event.x
        self.rectY_end = event.y
        
        # Modify rectangle x1, y1 coordinates
        self.coords(self.rect_id,
                    self.rectX_start, self.rectY_start,
                    self.rectX_end, self.rectY_end)



    def __onStopRect(self, event):
        
        if self.rect_id == None:
            return
        
        # (rectX_start - span) : lengthX = (x - 350) : (750 - 350)
        self.zoomX_start = (self.rectX_start - self.span) * (self.endX_current - self.beginX_current) / self.lengthX + self.beginX_current
        self.zoomX_start = int(self.zoomX_start)
        
        # (rectY_start - span) : lengthY = (1 - y) : (1 - (-0.1)
        self.zoomY_start = ((self.rectY_start - self.span) * (self.endY_current - self.beginY_current) / self.lengthY - self.endY_current) *-1
        self.zoomY_start = round(self.zoomY_start, 2)
        
        # (rectX_end - span) : lengthX = (x - 350) : (750 - 350)
        self.zoomX_end = (self.rectX_end - self.span) * (self.endX_current - self.beginX_current) / self.lengthX + self.beginX_current
        self.zoomX_end = int(self.zoomX_end)
        
        # (rectY_start - span) : lengthY = (1 - y) : (1 - (-0.1)
        self.zoomY_end = ((self.rectY_end - self.span) * (self.endY_current - self.beginY_current) / self.lengthY - self.endY_current) *-1
        self.zoomY_end = round(self.zoomY_end, 2) 
        
        
        self.beginX_current = min(self.zoomX_start, self.zoomX_end)
        self.endX_current = max(self.zoomX_start, self.zoomX_end)
        self.beginY_current = min(self.zoomY_start, self.zoomY_end)
        self.endY_current = max(self.zoomY_start, self.zoomY_end)
        
        
        self.__redrawCanvas()
    
    
    
    def __redrawCanvas(self):
        
        self.delete("all")
        
        self.__redrawAxis()
        self.__redrawPlots()
        self.__redrawLegend()
        
        
        
    def __drawCanvas(self):
        
        self.delete("all")
        
        self.__calculateZoom()
        self.__redrawAxis()
        self.__redrawPlots()
        self.__redrawLegend()
    
    
    
    def __calculateZoom(self):
        
        if self.__plot_list == []:
            self.endY_current = self.endY
            return
        
        max_heigth = 0
        for data in self.__plot_list:
            for i in range(len(data.x)):
                if (self.beginX_current <= data.x[i] and data.x[i] <= self.endX_current):
                    if data.y[i] > max_heigth:
                        max_heigth = data.y[i]
        self.endY_current = max_heigth + 0.01
        
        
        
    def __redrawAxis(self):
        
        # Some preliminary stuff based on __onResize()
        self.lengthX = self.pixelWidth -self.span -self.span # xAxis length in pixels.
        self.lengthY = self.pixelHeight -self.span -self.span # yAxis length in pixels.
        self.spaceXpix = self.lengthX // self.xTicks
        self.spaceYpix = self.lengthY // self.yTicks
        self.spaceX = (self.endX_current -self.beginX_current) // self.xTicks
        self.spaceY = (self.endY_current -self.beginY_current) / self.yTicks
        
        # Create title
        self.create_text(self.pixelWidth //2 , self.span //3, anchor='n', text= self.title, font = self.font_bold)
        # Create subtitle (15 pixels below the title)
        self.create_text(self.pixelWidth //2 , self.span //3  +15, anchor='n', text= self.subtitle)
        
        # Create X line     
        self.create_line(self.span, self.span + self.lengthY,
                           self.span + self.lengthX, self.span + self.lengthY,
                           width=2, fill ="black")
        
        # Create X ticks and numbers
        for i in range(self.xTicks +1):
            self.create_line(self.span + self.spaceXpix*i, self.span + self.lengthY,
                               self.span + self.spaceXpix*i, self.span + self.lengthY + 5,
                               width=1, fill="black")
            self.create_text(self.span + self.spaceXpix*i, self.span + self.lengthY + 5, # +5 for spacing in the pdf export
                               anchor='n', text='%d'% (self.beginX_current + self.spaceX*i), font = self.font_normal)   
        # Create X label
        self.create_text(self.span + self.lengthX , self.span + self.lengthY + self.span//2 + 10,
                               anchor='w', text= self.labelX, font = self.font_normal)
        
        # Create Y line
        self.create_line(self.span, self.span + self.lengthY,
                           self.span, self.span,
                           width=2, fill ="black")
        # Create Y ticks and numbers
        for i in range(self.yTicks +1):
            self.create_line(self.span, self.span + self.lengthY - self.spaceYpix*i,
                               self.span - 5, self.span + self.lengthY - self.spaceYpix*i,
                               width=1, fill="black")
            self.create_text(self.span -5 -5, self.span + self.lengthY - self.spaceYpix*i,# -5 for spacing in the pdf export
                               anchor='e', text='%.2f' % (self.beginY_current + self.spaceY*i), font = self.font_normal)
        # Create Y label
        self.create_text(self.span, self.span//2,
                               anchor='e', text= self.labelY, font = self.font_normal)
    
    
    
    def __redrawPlots(self):
        
        for plot in self.__plot_list:
            
            is_first_line = True
        
            # initial points:
            currX = self.span + (plot.x[0] - self.beginX_current) * self.lengthX / (self.endX_current - self.beginX_current)
            currY = self.span + self.lengthY - (plot.y[0] - self.beginY_current) * self.lengthY / (self.endY_current - self.beginY_current)
            
            
            # To solve the problem when zooming:
            if currX < self.span:
                currX = self.span
            elif currX > (self.span + self.lengthX):
                currX = self.span + self.lengthX
            
            if currY < self.span:
                currY = self.span
            elif currY > (self.span + self.lengthY):
                currY = self.span + self.lengthY
            
            
            for i in range(len(plot.x)):
                
                if i % self.precision != 0: # to speed up the plotting
                    continue
                
                # (x - 350) : (750 - 350) = newX : lengthX
                newX = (plot.x[i] - self.beginX_current) * self.lengthX / (self.endX_current - self.beginX_current)
                
                # (y - (-0.1): (1 - (-0.1)) = newY : lengthY
                newY = (plot.y[i] - self.beginY_current) * self.lengthY / (self.endY_current - self.beginY_current)
                
                
                newX = self.span + newX
                newY = self.span + self.lengthY - newY
                
                
                if (newX >= self.span and newX <= (self.span + self.lengthX) and
                    newY >= self.span and newY <= (self.span + self.lengthY)):
                    
                    if (is_first_line == True):
                        is_first_line = False
                        currX, currY = newX, newY
                        continue
                    else:
                        self.create_line(currX, currY, newX, newY, width = 3, fill= plot.color)
                    
                
                currX, currY = newX, newY
#                 else:
#                     print("Out of border!")
                    
              
              
    def __redrawLegend(self):
        
        coord_x = self.span + self.lengthX + self.span -5
        coord_y = 15 
        
        for plot in self.__plot_list:
            
            self.create_text(coord_x, coord_y, anchor='e', text= plot.label,
                             font= self.font_bold,  fill= plot.color)
            coord_y += 20
            
            
            
    def plotLine(self, fc): # Draw and save the given FastCoord
        
        if (len(fc.x) != len(fc.y)):
            print("len(x) != len(y)")
            return
        
        self.__plot_list.append(fc)
        
        self.__drawCanvas()
        
    
    def loadLine(self, fc):
        
        if (len(fc.x) != len(fc.y)):
            print("len(x) != len(y)")
            return
        
        self.__plot_list.append(fc)
        
        
    def updatePlot(self):
        
        self.__drawCanvas()
        
    
        
        

