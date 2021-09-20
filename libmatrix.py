import copy


class ObjMatrix(object):
    
    
    def __init__(self, rows = [[0]]):
        
        self.r = len(rows)
        self.c = len(rows[0])
        # Validity check
        if any([len(row) != self.c for row in rows[1:]]):
            print("inconsistent row length")
        self.rows = rows

        
        
    def getString(self):
        
        s='\n'.join([' '.join([str(item) for item in row]) for row in self.rows])
        return s + '\n'
    
    
    
    def getMax(self):
        
        current_max = self.rows[0][0]
        for i in range(self.r):
           for j in range(self.c):
               if self.rows[i][j] > current_max:
                    current_max = self.rows[i][j]
        return current_max
    
    
    
    def getMin(self):
        
        current_min = self.rows[0][0]
        for i in range(self.r):
           for j in range(self.c):
               if self.rows[i][j] < current_min:
                   current_min = self.rows[i][j]
        return current_min
        


    def isEqual(self, mat):
        
        return (mat.rows == self.rows)
    
    
    
    def transpose(self):
        
        rows =  [list(item) for item in zip(*self.rows)]
        return ObjMatrix(rows)
    
    
    
    def summate(self, mat):
        
        if (self.r != mat.r or self.c != mat.c):
            print("Trying to summate ObjMatrixes of varying rank!")

        result = ObjMatrix.makeZero(self.r, self.c)
        
        for i in range(self.r):
           for j in range(self.c):
               result.rows[i][j] = self.rows[i][j] + mat.rows[i][j]

        return result



    def subtract(self, mat):
        
        if (self.r != mat.r or self.c != mat.c):
            print("Trying to subtract ObjMatrixes of varying rank!")

        result = ObjMatrix.makeZero(self.r, self.c)
        
        for i in range(self.r):
           for j in range(self.c):
               result.rows[i][j] = self.rows[i][j] - mat.rows[i][j]

        return result



    def multiply(self, mat):
        
        if (self.c != mat.r):
            print("Matrices cannot be multipled!")
        
        result = ObjMatrix.makeZero(self.r, mat.c)
        
        for i in range(self.r):
           for j in range(mat.c):
               for k in range(mat.r):
                   result.rows[i][j] += self.rows[i][k] * mat.rows[k][j]

        return result
    
    
    def multiplyScalar(self, scalar):
        
        listol = []
        for i in range(self.r):
            row = []
            for j in range(self.c):
                row.append(scalar * self.rows[i][j])
            listol.append(row)
        return ObjMatrix(listol)

   
   
    def makeZero(r, c):

        rows = [[0]*c for x in range(r)]
        return ObjMatrix(rows)

    
    
    def makeIdentity(r):
        
        rows = [[0]*r for x in range(r)]
        idx = 0
        
        for row in rows:
            row[idx] = 1
            idx += 1

        return ObjMatrix(rows)
    
    

    def __minor(matrix, i):
        
        minor = copy.deepcopy(matrix)
        del minor[0] # Delete first row
        for b in range(len(matrix)-1): # Delete column i
            del minor[b][i]
        return minor



    def __det(rows):
        
        if len(rows) == 1: # End of recursion
            return rows[0][0]
        else:
            result = 0
            for x in list(range(len(rows))): 
                
                result += rows[0][x] * (-1)**(2+x) * ObjMatrix.__det(ObjMatrix.__minor(rows,x)) 
                
            return result
        
        
        
    def determinant(self):
        if (self.r != self.c):
            print("Can't calculate determinant if the matrix is non squared!")
            return
        
        rows = copy.deepcopy(self.rows)
        return ObjMatrix.__det(rows)
    
    
    
    def __inv(rows):    

        rows = [rows[i]+[int(i==j) for j in range(len(rows))] for i in range(len(rows))]    
        for i in range(len(rows)):
            rows[i:] = sorted(rows[i:], key=lambda r: -abs(r[i]))
            rows[i] = [rows[i][j]/rows[i][i] for j in range(len(rows)*2)]
            rows = [[rows[j][k] if i==j else rows[j][k]-rows[i][k]*rows[j][i] for k in range(len(rows)*2)] for j in range(len(rows))]
        return [rows[i][-len(rows):] for i in range(len(rows))]
    
    
    
    def inverse(self):
        if self.r != self.c:
            print("Requested the inverse of non-squared matrix. Are you shure?")
        rows = copy.deepcopy(self.rows)
        return ObjMatrix(ObjMatrix.__inv(rows))
    
    
    
    def extractColumns(self, indexes):
        
        new = []
        for i in range(self.r):
            # iterate through columns
            new_row = []
            for j in range(self.c):
                if j in indexes:
                    new_row.append(self.rows[i][j])
            new.append(new_row)
                   
        return ObjMatrix(new)
    
    
    
    def extractRows(self, indexes):
        
        listol = []
        for i in range(self.r):
            if i in indexes:
                listol.append(self.rows[i])
            
        print("new: " + str(listol))
                   
        return ObjMatrix(listol)
    
    
    
    def getArgMax(self): # (of the flattened array)
        
        current_index = 0
        current_max = self.rows[0][0]
        for i in range(self.r):
           for j in range(self.c):
               if self.rows[i][j] > current_max:
                    current_max = self.rows[i][j]
                    current_index = j + self.c * i
        return current_index
    
    
    def getNormL1(self):
        
        partials = [0 for i in range(self.c)]
        for i in range(self.r):
            for j in range(self.c):
                partials[j] += abs(self.rows[i][j])
        return max(partials)
    
    
    


if __name__ == "__main__":
    # getString
    a = ObjMatrix([[4, 6, 3], [7, 5, 2], [6, 1, 0]])
    print(a.getString())
    # transpose
    b = a.transpose()
    print(b.getString())
    # makeIdentity
    d = ObjMatrix.makeIdentity(5)
    print(d.getString())
    # makeZero
    e = ObjMatrix.makeZero(5,3)
    print(e.getString())
    # multiply
    o1 = ObjMatrix([[5,1] ,[2, 0]])
    o2 = ObjMatrix([[2,1,0],[4,3,-1]])
    o3 = o1.multiply(o2)
    print(o3.getString())
    # subtract
    o1 = ObjMatrix([[5,1, -2] ,[0,4,1]])
    o2 = ObjMatrix([[0,-4,15],[8,0,0]])
    o3 = o1.subtract(o2)
    print(o3.getString())
    # determinant
    data = ObjMatrix([[1, 2, 3], [-5, 0, 4], [2, 4, 6]])
    data = ObjMatrix([[2]])
    data = ObjMatrix([[3,-1,0], [-2,1,1], [4,5,-4]])
    print(data.determinant())
    # inverse
    last = ObjMatrix([[3,0,2],[2,0,-2],[0,1,1]])
    print(last.inverse().getString())
    # getArgMax
    am = ObjMatrix([[0, 1, 2, 3],
                     [4, 5, 6, 7],
                     [100, 9, 10, 11]])
    print(am.getArgMax())
    print(am.getString())
    # extractColumns
    print(am.extractColumns([1,3]).getString())    
    
    