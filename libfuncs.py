from libcoord import ObjCoord
from libmatrix import ObjMatrix
import libleasts
import webbrowser, platform, csv, copy, tkinter, tkinter.messagebox, tkinter.font
import pylightxl as xl
import math, statistics



def parseMD(widget, file, top):
    
    file_info = open(file, "r")
    lines = file_info.readlines()
    
    line_counter = 1
    link_list = []
    for line in lines:
        # title
        if line.startswith("### "):
            line = line.replace("### ", "")
            widget.insert("end", line)
            widget.tag_add('title', str(line_counter)+'.0', str(line_counter)+'.end')
        # code
        elif line.startswith("    "):
            line = line.replace("    ", "")
            widget.insert("end", line)
            widget.tag_add('code', str(line_counter)+'.0', str(line_counter)+'.end')
        # image
        elif line.startswith("!["):
            continue
        # body
        else:
            widget.insert("end", line)
            widget.tag_add('body', str(line_counter)+'.0', str(line_counter)+'.end')
        # link 
        if line.find("<") != -1 and line.find(">") != -1:
            while line.find("<") != -1 and line.find(">") != -1:
                begin = line.find("<")
                end = line.find(">")
                line = line.replace("<", "", 1) # first occurence
                line = line.replace(">", "", 1)
                widget.delete(str(line_counter)+'.'+str(begin))
                widget.delete(str(line_counter)+'.'+str(end -1))
                widget.tag_add("link", str(line_counter)+'.'+str(begin), str(line_counter)+'.'+str(end -1))
                url = widget.get(str(line_counter)+'.'+str(begin), str(line_counter)+'.'+str(end -1))
                link_list.append({
                    "url": url,
                    "line": line_counter,
                    "begin": begin,
                    "end": end-1})
        # inline code
        if line.find("`") != -1:
            while line.find("`") != -1:

                begin = line.find("`"); line = line.replace("`", "", 1) # first occurence
                end = line.find("`"); line = line.replace("`", "", 1) # second occurence

                begin_coord = str(line_counter)+'.'+str(begin)
                end_coord = str(line_counter)+'.'+str(end)

                widget.delete(begin_coord)
                widget.delete(end_coord)                

                widget.tag_add("code", begin_coord, end_coord)
                
        line_counter += 1
    
    # link tag & bindings
    widget.tag_config("link", foreground = "blue", underline = 1)
    def onEnter(event):
        widget.config(cursor="hand2")
    widget.tag_bind("link", "<Enter>", onEnter)
    def onLeave(event):
        widget.config(cursor="")
    widget.tag_bind("link", "<Leave>", onLeave)
    def onClick(event):
        position = event.widget.index("current")
        current_line = int(position.split(".")[0])
        current_col = int(position.split(".")[1])
        for link in link_list:
            if current_line == link["line"]:
                if link["begin"] <= current_col and current_col <= link["end"]:
                    if "www." in link["url"]:
                        webbrowser.open("http://" + link["url"], new=2) # 2: open in new tab if possible
                    elif "@" in link["url"]:
                        webbrowser.open("mailto:" + link["url"], new=1) # 1: open in same window if possible
                    else:
                        print("This doesn't seem a valid url")
    widget.tag_bind("link", "<Button-1>", onClick)
    
    # other tags
    if platform.system() == "Windows": 
        widget.tag_config('title', font='Verdana 15 bold')
        widget.tag_config('body', font='Verdana 10')
        widget.tag_config('code', font='Courier 10', foreground='green')
    if platform.system() == "Linux":
        widget.tag_config('title', font='Helvetica 15 bold')
        widget.tag_config('body', font='Helvetica 10')
        widget.tag_config('code', font='Courier 10', foreground='green')
    if platform.system() == "Darwin": # "Darwin" for MacOS
        widget.tag_config('title', font='Verdana 17 bold')
        widget.tag_config('body', font='Verdana 12')
        widget.tag_config('code', font='Courier 12', foreground='green')
        
        

def loadCSV(file):
        
    vector = []
    

    # PART 1. Try to understand delimiters:
    csv_file = open(file, "r")
    full_string = csv_file.read()
    csv_file.close()
    if ";" in full_string: delimiter = ";"
    elif "\t" in full_string: delimiter = "\t"
    else: delimiter = ","
    

    # PART 2. Header processing:
    csv_file = open(file, "r")
    dictionary = csv.DictReader(csv_file, delimiter = delimiter)
    names = dictionary.fieldnames # gets dataset labels
    # if the .csv is formatted like "A;B;C;D;E;" instead of "A;B;C;D;E"
    # the resulting vectors wil be ['A','B','C','D','E',''] 
    # this will alter also n_sets. Remove here the trailing '' to avoid further controls.
    if(names[-1] == ''): del names[-1] 
    del names[0] # excludes the x (nm) column
    n_sets = len(names) # counts how many datasets
    

    # PART 3: Create empty dataset vector with correct names:
    for i in range(n_sets):
        fc = ObjCoord()
        fc.label = names[i]
        vector.append(copy.deepcopy(fc)) # deepcopy necessary here!
    

    # PART 4: Fill datasets:
    rows = csv.reader(csv_file, delimiter = delimiter) # first row already read!   
    for row in rows:
        for i in range(n_sets):
            if delimiter == ";":
                vector[i].x.append(float(row[0].replace(",",".")))
                vector[i].y.append(float(row[i+1].replace(",",".")))
            else:
                vector[i].x.append(float(row[0])) # convert string to float
                vector[i].y.append(float(row[i+1])) # +1 excludes the nm column
    

    # PART 5: Check for inversed datasets (as in Cary spectrophotometers):
    for i in range(n_sets):
        if vector[i].x[0] > vector[i].x[-1]:
            vector[i].x.reverse()
            vector[i].y.reverse()
    
    
    csv_file.close()
    return vector



def loadXLSX(file):
        
    vector = []
    
    db = xl.readxl(fn=file)
    sheetnames = db.ws_names # return all worksheet names
    
    # metadata processing (assuming datapoints are stored in the first worksheet):
    names = db.ws(ws=sheetnames[0]).row(row=1) # gets dataset labels
    del names[0] # excludes the x (nm) column
    n_sets = len(names) # counts how many datasets
    
    # create empty dataset vector with correct names:
    for i in range(n_sets):
        fc = ObjCoord()
        fc.label = names[i]
        vector.append(copy.deepcopy(fc)) # deepcopy necessary here!
    
    # fill datasets:
    skipped = False
    for row in db.ws(ws=sheetnames[0]).rows:
        if skipped == False: # skip header row
            skipped = True
            continue
        for i in range(n_sets):
            vector[i].x.append(float(row[0])) # convert string to float
            vector[i].y.append(float(row[i+1])) # +1 excludes the nm column
    
    # check for inversed datasets (as in Cary spectrophotometers):
    for i in range(n_sets):
        if vector[i].x[0] > vector[i].x[-1]:
            vector[i].x.reverse()
            vector[i].y.reverse()
    
    return vector



def saveCSV(datasets, standards, algo, file_path, progress):
        
    file = open(file_path, "w")
    header = ["Sample", "Goodness", "Chl a/b", "Chl/Car", "Chl [uM]", "Car [uM]", "Chl a [uM]", "Chl b [uM]", 
              "Beta 80 [uM]", "Lute 80 [uM]", "Neo 80 [uM]", "Viola 80 [uM]", "Zea 80 [uM]",
              "Chl a 70 [uM]", "Chl a 90 [uM]", "Chl b 70 [uM]", "Chl b 90 [uM]"]
    writer = csv.DictWriter(file, fieldnames= header)  
    writer.writeheader()
    
    i = 1
    for dataset in datasets:
        
        chl_concents, chl_comps = fitterChl(dataset, standards, algo)
        chl_a_conc, chl_a_comp = compsAdder(chl_concents[0:2], chl_comps[0:2], "Chl a")
        chl_b_conc, chl_b_comp = compsAdder(chl_concents[2:4], chl_comps[2:4], "Chl b")
        chl_conc, chl_fit = compsAdder(chl_concents[0:4], chl_comps[0:4], "Chl fit")
        car_concents, car_comps = fitterCar(dataset, standards, chl_fit, algo)
        car_conc, car_fit = compsAdder(car_concents[0:5], car_comps[0:5], "Car fit")
        # choosen_subtracted = dataset.subtract(chl_fit) # doesn't matter here.
        tot_conc, tot_fit = compsAdder([chl_conc, car_conc], [chl_fit, car_fit], "Total fit")

        # calculate the goodness of the fit:
        goodness = calculateFttingError(dataset, tot_fit)

                                                 
        writer.writerow({"Sample" : dataset.label, "Goodness": goodness, "Chl a/b": round(chl_a_conc/chl_b_conc, 3),
                         "Chl/Car": round(chl_conc/car_conc, 3), "Chl [uM]": round(chl_conc, 3),
                         "Car [uM]": round(car_conc, 3), "Chl a [uM]": round(chl_a_conc, 3),
                         "Chl b [uM]": round(chl_b_conc, 3), "Beta 80 [uM]": round(car_concents[0], 3),
                         "Lute 80 [uM]": round(car_concents[1], 3), "Neo 80 [uM]": round(car_concents[2], 3),
                         "Viola 80 [uM]": round(car_concents[3], 3), "Zea 80 [uM]": round(car_concents[4], 3),
                         "Chl a 70 [uM]": round(chl_concents[0], 3), "Chl a 90 [uM]": round(chl_concents[1], 3),
                         "Chl b 70 [uM]": round(chl_concents[2], 3), "Chl b 90 [uM]": round(chl_concents[3], 3)})
        
        progress['value'] = (i)/len(datasets)*100
        progress.update_idletasks()
        i += 1
        


def saveXLSX(datasets, standards, algo, file_path, progress, norm):
    
    db = xl.Database() # create a black pylightxl-db
    db.add_ws(ws="chlorocarfitter") # add a blank worksheet to the pylightxl-db
    
    # write the header:
    header = ["Sample", "FitQual_Blue", "FitQual_Red",
              "", # skip one column
              "Chl/Car", "Chl a/b", 
              "", # skip one column
              # raw concetrations:
              "Chl a [uM]", "Chl b [uM]", "Car [uM]", 
              "Beta 80 [uM]", "Lute 80 [uM]", "Neo 80 [uM]", "Viola 80 [uM]", "Zea 80 [uM]",
              # "Chl a 70 [uM]", "Chl a 90 [uM]", "Chl b 70 [uM]", "Chl b 90 [uM]", # not so useful for the final user!
              # normalized values:
              "", # skip one column
              "Norm Chl a [uM]", "Norm Chl b [uM]", "Norm Car [uM]",
              "Norm Beta 80 [uM]", "Norm Lute 80 [uM]", "Norm Neo 80 [uM]", "Norm Viola 80 [uM]", "Norm Zea 80 [uM]"]
    for col_id, data in enumerate(header, start=1):
        db.ws(ws="chlorocarfitter").update_index(row=1, col=col_id, val=data)
    
    # write rows (one sample per row):
    i = 1
    for dataset in datasets:
        
        chl_concents, chl_comps = fitterChl(dataset, standards, algo)
        chl_a_conc, chl_a_comp = compsAdder(chl_concents[0:2], chl_comps[0:2], "Chl a")
        chl_b_conc, chl_b_comp = compsAdder(chl_concents[2:4], chl_comps[2:4], "Chl b")
        chl_conc, chl_fit = compsAdder(chl_concents[0:4], chl_comps[0:4], "Chl fit")
        car_concents, car_comps = fitterCar(dataset, standards, chl_fit, algo)
        car_conc, car_fit = compsAdder(car_concents[0:5], car_comps[0:5], "Car fit")
        # choosen_subtracted = dataset.subtract(chl_fit) # doesn't matter here.
        tot_conc, tot_fit = compsAdder([chl_conc, car_conc], [chl_fit, car_fit], "Total fit")

        # calculate the goodness of the fit:
        goodness = calculateFttingError(dataset, tot_fit)
        goodness_red = goodness[0]
        goodness_blue = goodness[1]
                                                 
        samplerow = [dataset.label, goodness_blue, goodness_red,
               "", # skip one column
               round(chl_conc/car_conc, 3), round(chl_a_conc/chl_b_conc, 3),
               "", # skip one column
               # raw concetrations:
               round(chl_a_conc, 3), round(chl_b_conc, 3), round(car_conc, 3), 
               round(car_concents[0], 3), round(car_concents[1], 3), round(car_concents[2], 3), round(car_concents[3], 3), round(car_concents[4], 3), 
               # round(chl_concents[0], 3), round(chl_concents[1], 3), round(chl_concents[2], 3), round(chl_concents[3], 3), # not so useful for the final user!
               # normalized values:
               "", # skip one column
               round(norm * chl_a_conc /(chl_a_conc + chl_b_conc), 3), 
               round(norm * chl_b_conc /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_conc /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_concents[0] /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_concents[1] /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_concents[2] /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_concents[3] /(chl_a_conc + chl_b_conc), 3), 
               round(norm * car_concents[4] /(chl_a_conc + chl_b_conc), 3)]

        
        for col_id, data in enumerate(samplerow, start=1):
            db.ws(ws="chlorocarfitter").update_index(row=1+i, col=col_id, val=data)
        
        # incrment the progress bar:
        progress['value'] = (i)/len(datasets)*100
        progress.update_idletasks()
        i += 1
        
    # write out the pylightxl-db
    xl.writexl(db=db, fn=file_path)



def redSubsetter(dataset):
    
    # select lower en upper value (from 615.2-625.2) as described in manuscript:
    left_red1 = dataset.x.index(615.2)   
    right_red1 = dataset.x.index(625.6) # right end not included!
    subset_red1_nm = dataset.x[left_red1 : right_red1 : 4] # take 0.4nm interval
    subset_red1_au = dataset.y[left_red1 : right_red1 : 4]

    # select lower en upper value (from 635.6-650) as described in manuscript:
    left_red2 = dataset.x.index(635.6)   
    right_red2 = dataset.x.index(650.4) # right end not included!
    subset_red2_nm = dataset.x[left_red2 : right_red2 : 4] # take 0.4nm interval
    subset_red2_au = dataset.y[left_red2 : right_red2 : 4]

    # select lower en upper value (from 656-680) as described in manuscript:
    left_red3 = dataset.x.index(656.0)   
    right_red3 = dataset.x.index(680.4) # right end not included!
    subset_red3_nm = dataset.x[left_red3 : right_red3 : 4] # take 0.4nm interval
    subset_red3_au = dataset.y[left_red3 : right_red3 : 4]

    subset_red_nm = subset_red1_nm + subset_red2_nm + subset_red3_nm
    subset_red_au = subset_red1_au + subset_red2_au + subset_red3_au
    return ObjCoord(x = subset_red_nm, y = subset_red_au, label = dataset.label)



def fitterChl(dataset, standards, algo):
    
    chl_sub = {
        "chla70_sub" : redSubsetter(standards["chla70"]),
        "chla90_sub" : redSubsetter(standards["chla90"]),
        "chlb70_sub" : redSubsetter(standards["chlb70"]),
        "chlb90_sub" : redSubsetter(standards["chlb90"])
    }
    subsetted = redSubsetter(dataset) # the sample
    multip = [i * 1000000 for i in subsetted.y]
    
    a = ObjMatrix([multip]).transpose()
    E = ObjMatrix([chl_sub["chla70_sub"].y, chl_sub["chla90_sub"].y, chl_sub["chlb70_sub"].y, chl_sub["chlb90_sub"].y]).transpose()
    C = ObjMatrix()
    if algo == "OLS":
        C = libleasts.OLS(a, E)
    elif algo == "Caffarri":
        C = libleasts.NNLS(a, E, max_cycle = 10)
    else:
        #C = libleasts.OLS(a, E)
        C = libleasts.NNLS(a, E, max_cycle = 10)
    
    concents = C.transpose().rows[0]
    comps = []
    chla70_x = standards["chla70"].x
    chla70_y = [i * concents[0] / 1000000 for i in standards["chla70"].y]
    comps.append(ObjCoord(chla70_x, chla70_y, label = chl_sub["chla70_sub"].label, color = "SteelBlue1"))
    chla90_x = standards["chla90"].x
    chla90_y = [i * concents[1] / 1000000 for i in standards["chla90"].y]
    comps.append(ObjCoord(chla90_x, chla90_y, label = chl_sub["chla90_sub"].label, color = "SteelBlue3"))
    chlb70_x = standards["chlb70"].x
    chlb70_y = [i * concents[2] / 1000000 for i in standards["chlb70"].y]
    comps.append(ObjCoord(chlb70_x, chlb70_y, label = chl_sub["chlb70_sub"].label, color = "chartreuse2"))
    chlb90_x = standards["chlb90"].x
    chlb90_y = [i * concents[3] / 1000000 for i in standards["chlb90"].y]
    comps.append(ObjCoord(chlb90_x, chlb90_y, label = chl_sub["chlb90_sub"].label, color = "green3"))
        
    return concents, comps



def blueSubsetter(dataset):
    
    """
    left_blue1 = dataset.x.index(410.0) 
    right_blue1 = dataset.x.index(420.0)  
    subset_blue1_nm = dataset.x[left_blue1 : right_blue1]
    subset_blue1_au = dataset.y[left_blue1 : right_blue1]
    left_blue2 = dataset.x.index(432.0)   
    right_blue2 = dataset.x.index(444.0) 
    subset_blue2_nm = dataset.x[left_blue2 : right_blue2]
    subset_blue2_au = dataset.y[left_blue2 : right_blue2]
    left_blue3 = dataset.x.index(466.0)    
    right_blue3 = dataset.x.index(476.0)  
    subset_blue3_nm = dataset.x[left_blue3 : right_blue3]
    subset_blue3_au = dataset.y[left_blue3 : right_blue3]
    left_blue4 = dataset.x.index(484.0)    
    right_blue4 = dataset.x.index(505.0)   
    subset_blue4_nm = dataset.x[left_blue4 : right_blue4]
    subset_blue4_au = dataset.y[left_blue4 : right_blue4]
    subset_blue_nm = subset_blue1_nm + subset_blue2_nm + subset_blue3_nm + subset_blue4_nm
    subset_blue_au = subset_blue1_au + subset_blue2_au + subset_blue3_au + subset_blue4_au
    """
    # select lower en upper value (from 409.6 to 520) as described in manuscript:
    left_blue = dataset.x.index(409.6)
    right_blue = dataset.x.index(520.8) # right end not included!
    # take 0.8nm interval
    subset_blue_nm = dataset.x[left_blue : right_blue : 8]
    subset_blue_au = dataset.y[left_blue: right_blue : 8] 

    return ObjCoord(x = subset_blue_nm, y = subset_blue_au, label = dataset.label)



def fitterCar(dataset, standards, chl_fit, algo):
    
    car_sub = {
        "beta80_sub" : blueSubsetter(standards["beta80"]),
        "lute80_sub" : blueSubsetter(standards["lute80"]),
        "neo80_sub" : blueSubsetter(standards["neo80"]),
        "viola80_sub" : blueSubsetter(standards["viola80"]),
        "zea80_sub" : blueSubsetter(standards["zea80"])
    }
    dataset_subtracted = dataset.subtract(chl_fit, "subtracted", color = "gray60")
    subsetted = blueSubsetter(dataset_subtracted) # the sample
    multip = [i * 1000000 for i in subsetted.y]
    
    a = ObjMatrix([multip]).transpose()
    E = ObjMatrix([car_sub["beta80_sub"].y, car_sub["lute80_sub"].y, car_sub["neo80_sub"].y, car_sub["viola80_sub"].y, car_sub["zea80_sub"].y]).transpose()
    C = ObjMatrix()
    if algo == "OLS":
        C = libleasts.OLS(a, E)
    elif algo == "Caffarri":
        C = libleasts.NNLS(a, E, max_cycle = 10)
    else:
        #C = libleasts.OLS(a, E)
        C = libleasts.NNLS(a, E, max_cycle = 10)
    
    concents = C.transpose().rows[0]
    comps = []
    beta80_x = standards["beta80"].x
    beta80_y = [i * concents[0] / 1000000 for i in standards["beta80"].y]
    comps.append(ObjCoord(beta80_x, beta80_y, label = car_sub["beta80_sub"].label, color = "salmon"))
    lute80_x = standards["lute80"].x
    lute80_y = [i * concents[1] / 1000000 for i in standards["lute80"].y]
    comps.append(ObjCoord(lute80_x, lute80_y, label = car_sub["lute80_sub"].label, color = "orange"))
    neo80_x = standards["neo80"].x
    neo80_y = [i * concents[2] / 1000000 for i in standards["neo80"].y]
    comps.append(ObjCoord(neo80_x, neo80_y, label = car_sub["neo80_sub"].label, color = "gold"))
    viola80_x = standards["viola80"].x
    viola80_y = [i * concents[3] / 1000000 for i in standards["viola80"].y]
    comps.append(ObjCoord(viola80_x, viola80_y, label = car_sub["viola80_sub"].label, color = "plum3"))
    zea80_x = standards["zea80"].x
    zea80_y = [i * concents[4] / 1000000 for i in standards["zea80"].y]
    comps.append(ObjCoord(zea80_x, zea80_y, label = car_sub["zea80_sub"].label, color = "HotPink3"))
    
    return concents, comps



def compsAdder(concents, comps, label, color = "gainsboro"):
    
    total = [0 for i in comps[0].x]
    for i in range(len(total)):
        for comp in comps:
            total[i] += comp.y[i]            
    
    return sum(concents), ObjCoord(comps[0].x, total, label, color = color)



def calculatePorraEq(sample):
    
    A6636 = sample.y[sample.x.index(663.6)]
    A6466 = sample.y[sample.x.index(646.6)]
    
    # results for ug/mL
    Cchla_ug = 12.25 * A6636 - 2.55 * A6466
    Cchlb_ug = 20.31 * A6466 - 4.91 * A6636
    # results for nmol/mL
    Cchla_nmol = 13.713 * A6636 - 2.854 * A6466
    Cchlb_nmol = 22.386 * A6466 - 5.416 * A6636
    
    
    return round(Cchla_ug, 3), round(Cchlb_ug,3), round(Cchla_nmol, 3), round(Cchlb_nmol,3)


def calculateCaffarriEq(sample):
    
    A6636 = sample.y[sample.x.index(663.6)]
    A6466 = sample.y[sample.x.index(646.6)]
    
    # results for ug/mL
    Cchla_ug = 12.18 * A6636 - 2.36 * A6466
    Cchlb_ug = 20.19 * A6466 - 4.59 * A6636
    # results for nmol/mL
    Cchla_nmol = 13.63 * A6636 - 2.64 * A6466
    Cchlb_nmol = 22.25 * A6466 - 5.06 * A6636
    
    
    return round(Cchla_ug, 3), round(Cchlb_ug,3), round(Cchla_nmol, 3), round(Cchlb_nmol,3)
    
    
def calculateFttingError(measured, fitted):

    # Assume that datasets have the same length (4000, by construction):
    # So len(measured.y) is equal to len(fitted.y).

    # Below the old version of the goodness:
    """
    # Here we want to calculate the 1-RSE (relative squared error).
    # 1-RSE = 1 - sqrt(sum((yAi - yBi)^2)/sum((yAi - mean(yA))^2))
    # Where A is "measeured" and B is "fitted"

    sum_e = 0.0
    sum_m = 0.0
    mean_measured = statistics.mean(measured.y)
    for i in range(0, len(measured.x)):
        sum_e += (measured.y[i] - fitted.y[i])**2
        sum_m += (measured.y[i] - mean_measured)**2

    RSE = math.sqrt(sum_e / sum_m)
    
    return round(1.0 - RSE, 5) 
    """

    # Below the new version of the goodness:

    # Extract the red fitting region and the blue fitting region:
    measured_red = redSubsetter(measured)
    measured_blue = blueSubsetter(measured)
    fitted_red = redSubsetter(fitted)
    fitted_blue = blueSubsetter(fitted)

    # Here we want to calculate the normalized RMSE (root mean square error).
    # NRMSE = sqrt(sum((yAi - yBi)^2)/n)/mean(yA)
    # Where A is "measeured" and B is "fitted", n the number of points used for the fit.
    def NRMSE(meas, fit):
        sum_e = 0.0 
        mean_measured = statistics.mean( [ i*1000000 for i in meas.y ])
        for i in range(0, len(meas.x)):
            sum_e += (meas.y[i]*1000000 - fit.y[i]*1000000)**2

        # Now sum_e is equal to the Excel "square function minimised by solver"
        # (slightly different values are possible due to system's approximations)

        nrmse = math.sqrt(sum_e / len(meas.x)) / mean_measured
        # please note: len(meas.x) is constant: 124 for chls, 139 for cars.
        return nrmse

    # Since the RMSE value is very low, we chose to multiply by 500 (for Chls) and 
    # 200 (for Cars) to have number in the range of 1-2 for good fit and >3 for bad fit.
    # We report a similar message as the excel ("good fit < 2; bad fit > 3 --> check").
    goodness_red = round(NRMSE(measured_red, fitted_red) * 500, 2)
    goodness_blue = round(NRMSE(measured_blue, fitted_blue) * 200, 2)

    return goodness_red, goodness_blue
    