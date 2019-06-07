import copy
import itertools
import pickle
from sympy.combinatorics import Permutation
from sympy import simplify, fraction,  Symbol

class Averager:
    def __init__(self, rms = ("U","V"),                 
                 brackets= ("[","]","(",")"), 
                 powers_dic = {"transpose":"+","conjugate":"-","adjoint":"*"}, 
                 limit = 4):
        self.rms = rms
        self.brackets = brackets
        self.powers_dic = powers_dic
        self.powers = tuple(powers_dic.values())
        self.limit = limit
        
    def __call__(self, Mats):
        self.Mats = Mats
        List_tidied = self.TidyUp(self.Mats)
        if type(List_tidied) == str:
            return List_tidied, None
        List_regularized = self.Regularizer(List_tidied)
        List_tagged = self.Tagging(List_regularized)
        Edges = self.EdgeMaker(List_tagged)
        Dic_edges, List_nr, Dic_sizes= self.Sorting(Edges)
        if type(Dic_sizes) == str:
            return Dic_sizes, None
        Dic_Ave = self.Connecter(Dic_edges, List_nr, Dic_sizes)
        Dic_tidied = {}
        for key, value in Dic_Ave.items():
            List_tensor, List_trace, number_emptyloops = self.Looper(value)
            Tensors, Traces = self.TransposeInterpreter(List_tensor, List_trace)
            Dic_tidied[key] = (Tensors, Traces, number_emptyloops)
        Dic_final = self.WFConverter(Dic_tidied)
        
        Speach = ""
        for key, value in Dic_final.items():
            Summands_list = [self.AsciiMathConverter_each(x[1],x[0])  for x in value]
   
            Statement = ""
            for term in Summands_list:
                Statement += term + " + "
            Statement = Statement[:-3]
            key_AM = self.AsciiMathConverter_fraction(key)
            add = "`+`" + "`"+ key_AM + "[" + Statement + "]` <br>"
            Speach += add
        Speach = Speach[3:]
        return Dic_final , Speach
    
    def TidyUp(self, String):
        String = copy.deepcopy(String)
        String = String.replace(" ","") 
        
        if String == "":
            return "Enter something."                
        
        if not String[-1] in self.brackets:
            return "Something wrong with the structure."

        for l in String:
            if l == "I":
                return "The letter I is reserved for the internal calculation."
            elif  not l.isalpha() and not l in self.brackets and not l in self.powers:
                return "Use alphabets to represent matrices, please."
            
        List_neat = []
        for i,x in enumerate(String):
            if x in self.powers:
                pass
            elif x in self.brackets:
                List_neat.append(x+" ")
            elif String[i+1] in self.powers:
                List_neat.append(String[i:i+2])
            else:
                List_neat.append(x+" ")
                
        Bs = [[x[0],i] for i, x in enumerate(List_neat) if x[0] in self.brackets]
        if len(Bs)%2 != 0:
            return "Something wrong with the structure."
        for i in range(int(len(Bs)/2)):
            if not Bs[2*i][0] + Bs[2*i+1][0] in ["()" ,"[]"]:
                return "Something wrong with the structure."
            elif Bs[2*i][1] -  Bs[2*i+1][1] == -1:
                return "Something wrong with the structure."
                
        return List_neat
    
    def Regularizer(self,List):
        List = copy.deepcopy(List)
        Position = []
        for i, x in enumerate(List):
            if x == "[ " and List[i+1][0] in self.rms:
                Position.append(i+1)
            elif x[0] in self.rms and List[i+1][0] in self.rms:
                Position.append(i+1)
            else:
                pass
        Position_reverse = Position[::-1]
        for i in Position_reverse:
            List.insert(i, "? ")
        return List
    
    def Tagging(self,List):
        List_new = []
        for x in List:
            if x[0] in self.brackets:
                List_new.append(x)
            else:
                if x[1] == " ":
                    List_new.append([x[0], [1, 1]])
                elif x[1] == self.powers_dic["transpose"]:
                    List_new.append([x[0], [-1, 1]])
                elif x[1] == self.powers_dic["conjugate"]:
                    List_new.append([x[0], [1, -1]])        
                elif x[1] == self.powers_dic["adjoint"]:
                    List_new.append([x[0], [-1, -1]])               
        Stats = {}
        List_out = copy.deepcopy(List_new)
        for i, x in enumerate(List_new):
            if x[0] in self.brackets or x[0] in self.rms:
                pass
            else:
                if x[0] in Stats:
                    Stats[x[0]] += 1
                    List_out[i][0] += str(Stats[x[0]])
                else:
                    List_out[i][0] += "0"
                    Stats[x[0]] = 0
        return List_out    
    
    def Flip_rm(self,List):
        List = copy.deepcopy(List)
        if List[0][0][0] in self.rms and List[0][1][0] == -1:
            List[0][1][0] *= -1
            List[1] *= -1
        return List
    
    def Flip_LR(self,List):
        List = copy.deepcopy(List)
        List[1] *= -1
        return List

    def Flip_transpoce(self,List):
        List = copy.deepcopy(List)
        List[0][1][0] *= -1
        return List

    def EdgeMaker(self,List):
        List = copy.deepcopy(List)
        Edges = []
        mark = None
        Length = len(List)
        for i,x in enumerate(List):
            y = List[i+1]
            if x == "[ ":
                mark = i
            elif y == "] ":
                Edges.append([[x,1],[List[mark +1],-1]])
                mark = None
            elif x == "( ":
                Edges.append([[["@"+y[0],y[1]], 1],[y, -1]])
            elif y == ") ":
                Edges.append([[x, 1],[["@"+x[0],x[1]], -1]])
            elif x == ") ":
                pass
            elif x == "] ":
                pass
            else:
                Edges.append([[x,1],[y,-1]])

            if i == Length - 2:
                break

        Edges = [ [self.Flip_rm(y) for y in x] for x in Edges]

        return Edges
    

    def Sorting(self,List):
        List = copy.deepcopy(List)

        Dic_How2Connect = {(x,side,conjugation): [] for x in self.rms for side in [-1,1] for conjugation in [-1,1]}
        List_nr = []
        Sizes_SG = {}

        for i, x in enumerate(List):
            if x[1][0][0] in self.rms:
                List[i] = x[::-1]

        for x in List:
            if x[0][0][0] not in self.rms:
                List_nr.append(x)
            else: 
                Dic_How2Connect[(x[0][0][0],x[0][1],x[0][0][1][1])].append(x[1])
        
        def factorial(n):
            if n == 0:
                return 1
            else:
                return n * factorial(n-1)  
        
        Stats = [ [x,[ len(Dic_How2Connect[( x, 1, conjugation)]) for conjugation in [-1,1]]] for x in self.rms] 
        complexity = 1
        for x in Stats:
            if x[1][0] != x[1][1]:
                Dic_How2Connect = {}
                List_nr = []
                Sizes_SG = "The average is trivially zero."
                break
            elif x[1][0] != 0:
                Sizes_SG[x[0]] = x[1][0]
                complexity *= factorial(x[1][0])
                
        if complexity > self.limit:
            Dic_How2Connect = {}
            List_nr = []
            Sizes_SG = "Too many matrices."     
                    
        return Dic_How2Connect, List_nr, Sizes_SG

    # generating all possible connections and making a dictionary of them.
    def Connecter(self, Dic_edges, List_nr, Dic_sizes):
        List_rms = tuple([x for x in  Dic_sizes])
        List_arms = tuple([ [x, i] for x in List_rms  for i in [-1,1]])
        Perms = [itertools.permutations(list(range( Dic_sizes[x]))) for x in List_rms]

        Perms_doubled = [ list(copy.deepcopy(x))  for x in Perms for i in range(2)]
        Perms_all = itertools.product(*Perms_doubled)

        Dic_average = {x:[] for x in list(Perms_all)}
        for x in Dic_average:
            for j,y in enumerate(x):
                p = Permutation(y)
                original = Dic_edges[tuple(List_arms[j]+[1])]
                conjugate = p(Dic_edges[tuple(List_arms[j]+[-1])])
                pairs_zipped = zip( original, conjugate )
                pairs = [ list(x) for x in pairs_zipped]
                Dic_average[x] += pairs
            Dic_average[x] += List_nr
        return Dic_average
    
    ### sub-structure ###
    ### seb-sub-structure ###
    
    # collecting tensor structures in the average and
    # return them and the rest, which is supposed to be traces, which is a number.
    def Collector_tensor(self, List,Ends):
        List = copy.deepcopy(List)
        List_tensor = []
        for x in Ends:
            List_each = [x]
            while True:
                for j,y in enumerate(List):
                    if y[0] == List_each[-1]:
                        List_each.append(self.Flip_LR(y[1]))
                        del List[j]
                    elif y[1] == List_each[-1]:
                        List_each.append(self.Flip_LR(y[0]))
                        del List[j]
                if List_each[-1][0][0][0] == "@":
                    List_each[-1][1] *= -1
                    break
            if len(List_each) >1:
                List_tensor.append(List_each)
            else:
                pass

        List_tensor_noQM = [[m for m in l if m[0][0][0] !="?"] for l in List_tensor]
        return List_tensor_noQM, List
    
    def Collector_trace(self,List):
        List = copy.deepcopy(List)
        List_trace = []
        while List != []:
            Head = List[0][0]
            List_each = [Head]
            while True:
                for j,y in enumerate(List):
                    if y[0] == List_each[-1]:
                        List_each.append(self.Flip_LR(y[1]))
                        del List[j]
                    elif y[1] == List_each[-1]:
                        List_each.append(self.Flip_LR(y[0]))
                        del List[j]
                if List_each[-1] == Head:
                    del List_each[-1]
                    break                
            List_trace.append(List_each)
        
        List_trace_noQM = [[m for m in l if m[0][0][0] !="?"] for l in List_trace]
        number_emptyloops = List_trace_noQM.count([])
        List_trace_noQM_noEmpty = [l for l in List_trace_noQM if l !=[] ]
        return List_trace_noQM_noEmpty, number_emptyloops
    
    def Looper(self,List):
        List= copy.deepcopy(List)
        #Ends = [ y for x in List for y in x if y[0][0][0] == "@"]
        # making the program user friendly:
        Ends = [ y for x in List for y in x if y[0][0][0] == "@" and y[1] == 1]\
        + [ y for x in List for y in x if y[0][0][0] == "@" and y[1] == -1]
        if Ends == []:
            List_tensor = []
            List_rest = List
        else:
            List_tensor, List_rest = self.Collector_tensor(List, Ends)

        if List_rest == []:
            List_trace = []
            number_emptyloops = 0
        else:
            List_trace, number_emptyloops  = self.Collector_trace(List_rest)

        return List_tensor, List_trace, number_emptyloops 
    
    def TransposeInterpreter(self,List_tensor, List_trace):
        List_tensor = copy.deepcopy(List_tensor)
        List_trace = copy.deepcopy(List_trace)
        List_tensor_new = [[y[0] if y[0][0][0] == "@" else 
                            self.Flip_transpoce(y)[0] if y[1] == -1 else y[0] for y in x] for x in List_tensor]
        List_trace_new =[[ self.Flip_transpoce(y)[0] if y[1] == -1 else y[0] for y in x] for x in List_trace]
        return List_tensor_new, List_trace_new
    
    ### up to here ###
    
    def WFConverter(self,Dic):
        sample = list(Dic)[0][0::2]
        counts = [len(x) for x in sample]
        Dics_W = []
        for size in counts:
            with open("Weingarten_dictionary/functions{}.pkl".format(size), 'rb') as file:
                    Dic_W = pickle.load(file) 
                    Dics_W.append(Dic_W)

        Dic_out = {}
        for key, value in Dic.items():
            W_each = 1
            for i ,x in enumerate(counts):
                a = list(key[2*i])
                b = list(key[2*i+1])
                b_inv = [b.index(i) for i in range(x)] 
                perm_each =  Permutation(a) * Permutation(b_inv)
                cycles = sorted([ len(cycle) for cycle in perm_each.full_cyclic_form], reverse=True)    
                n = Symbol("n")
                W_each *= Dics_W[i][tuple(cycles)] * n** value[2]
            W_each_simplified = copy.deepcopy(simplify(W_each))
            if W_each_simplified in Dic_out:
                Dic_out[W_each_simplified].append(value[:2])
            else:
                Dic_out[W_each_simplified] = [value[:2]]

        return Dic_out  
    
    def AsciiMathConverter_each(self,Traces, Tensors):
        
        def PowerFinder(List):
            if List == [-1,-1]:
                power = "^(**)"  
            elif List == [-1,1]:
                power = "^(T)"
            elif List == [1,-1]:
                power = "^(-)"
            else:
                power = ""
            return power       
        
        AMTrace = []
        for word in Traces:
            word_new = ""
            for x in word:
                word_new += " " + x[0][0]+ PowerFinder(x[1])
            word_new = " `Trace`[ " + word_new  + " ]"
            AMTrace.append(word_new)
            AMTrace.append(" xx ")

        AMTensor = []
        for word in Tensors:
            word_new = ""
            for x in word:
                if x[0][0] == "@":         
                    word_new += "(" + x[0][1] + PowerFinder(x[1])+ ")" 
                else:
                    word_new +=  " " + x[0][0]+ PowerFinder(x[1]) 
            AMTensor.append(" ox ")
            AMTensor.append(word_new)

        if len(AMTrace) >0 and len(AMTensor) ==0:
            Phrase_list = AMTrace[:-1]
        elif len(AMTensor) >0:
            Phrase_list = AMTrace + AMTensor[1:]
        else:
            Phrase_list = ["0"]
        Phrase = ""
        for x in Phrase_list:
            Phrase += x

        return Phrase
    
    def AsciiMathConverter_fraction(self,f):
        numerator, denominator = fraction(f)
        numerator_string = str(numerator).replace("**","^")
        denominator_string = str(denominator).replace("**","^")
        fraction_AM = "frac{" + numerator_string+"}{" +denominator_string +"}"
        return fraction_AM    

def AM2Plain(String):
    if String == None:
        return None
    String = String.replace("`", "").replace("^(T) ","+ ").replace("^(-)","- ").replace("^(**)","* ").replace("<br>","\n")
    return String

def RTNI_light(Integrand, rms = ("U","V") , powers_dic = {"transpose":"+","conjugate":"-","adjoint":"*"}, limit = 4):
    pythonic, asciimath = Averager(rms = rms, powers_dic = powers_dic, limit = limit)(Integrand)
    plain = AM2Plain(asciimath)
    return plain, pythonic
    
    