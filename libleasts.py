from libmatrix import ObjMatrix
import copy


def OLS(A, E):
        
        # C = (Et * E)-1 * Et * A
        Et = E.transpose()
        EtE = Et.multiply(E)
        EtE1 = EtE.inverse()
        EtE1Et = EtE1.multiply(Et)
        C = EtE1Et.multiply(A)
        return C
    
    
def NNLS(y, A, tol = None, max_cycle = None):
        
    if tol == None:
        eps = 2.22e-16 ; tol = 10 * eps * A.getNormL1() * (max(A.r, A.c) +1)
            
    if max_cycle == None:
        max_cycle = 30 * A.c # 150
        
    # Algorithm by Lawson and Hanson
    P = []
    R = [i for i in range(A.c)]
            
    x = ObjMatrix.makeZero(A.c, 1)
        
    # resid = y - A*x
    resid = y.subtract(A.multiply(x))
    # w = At * (y - Ax)
    w = A.transpose().multiply(resid)
        
    cycle = 0          
    while (R != [] and w.getMax() > tol and cycle < max_cycle):
            
        j = w.getArgMax()
            
        if not j in P:
            P.append(j)   
            R.remove(j)   

        s = ObjMatrix.makeZero(A.c, 1)
            
        # sP = ((AP)t * AP)−1 * (AP)t * y
        AP = A.extractColumns(P)
        sP = OLS(y, AP)
        k = 0
        for i in range(A.c):
            if i in P:
                s.rows[i] = sP.rows[k]
                k += 1
            else:
                s.rows[i] = [0.0]
            
        inn_cycle = 0
        
        while sP.getMin() <= 0.0:

            found = []
            for i in P:
                if s.rows[i][0] <= 0.0:
                    found.append(x.rows[i][0]/(x.rows[i][0] - s.rows[i][0]))
            alpha = min(found)

            # x = x + a*(s - x)
            x = x.summate(s.subtract(x).multiplyScalar(alpha))
                
            for j in P:
                if x.rows[j][0] == 0.0: 
                    R.append(j) 
                    P.remove(j)
                
            # sP = ((AP)t * AP)−1 * (AP)t * y
            AP = A.extractColumns(P)
            sP = OLS(y, AP)
            k = 0
            for i in range(A.c):
                if i in P:
                    s.rows[i] = copy.deepcopy(sP.rows[k])
                    k += 1
                else:
                    s.rows[i] = [0.0]
                
            inn_cycle += 1
                    
        x = s   
        # resid = y - A*x
        resid = y.subtract(A.multiply(x))
        # w = At * (y - Ax)
        w = A.transpose().multiply(resid)
            
        cycle += 1
    
    return x



if __name__ == "__main__":

    x = ObjMatrix([[0.8587], [0.1781], [0.0747], [0.8405]])
    Z = ObjMatrix([[0.0372, 0.2869, 0.4],
                    [0.6861, 0.7071, 0.3],
                    [0.6233, 0.6245, 0.1],
                    [0.6344, 0.6170, 0.5]])
    
    d = NNLS(x, Z)
    print(d.getString())

    
    
    
    