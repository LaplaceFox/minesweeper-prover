from dataclasses import dataclass

class Rule:
    #name: Rule name as string
    #type: Tuple of types in rule premise
    #applyfn: Takes props of correct types, returns (possibly empty) list of props
    
    def __init__(self,name,types,applyfn):
        self.name = name
        self.types = types
        self.applyfn = applyfn

    def typecheck(self,*args):
        assert len(args) == len(self.types), "Wrong number of arguments for %s" % (self.name)
        assert False not in [isinstance(args[i],self.types[i]) for i in range(len(self.types))], "Argument of wrong type"

    def apply(self,*args):
        self.typecheck(*args)
        return self.applyfn(*args)

@dataclass
class Mine:
    cell: int

    def __init__(self,cell):
        self.cell = cell

@dataclass
class Safe:
    cell: int

    def __init__(self,cell):
        self.cell = cell

@dataclass
class Total:
    bounds: "tuple[int,int]"
    region: "set[int]"

    def __init__(self,low,high,region):
        self.bounds = (low,high)
        self.region = region

### RULES ###

# Input is (Total,Total)
def apply_subset(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError
        
    match args[1]:
        case Total([c,d],T):
            pass
        case _:
            raise ValueError
        
    if S < T:
        return [Total(c-b, d-a, T-S)]
    else:
        return []

rule_subset = Rule("Subset", (Total,Total), apply_subset)


# Input is (Total,Total)
def apply_intersection(*args):
    match args[0]:
        case Total(_,S):
            pass
        case _:
            raise ValueError
        
    match args[1]:
        case Total(_,T):
            pass
        case _:
            raise ValueError
        
    if S != T: # conclusion would be redundant
        return [Total(0, len(S & T), S & T)]
    else:
        return []
    
rule_intersection = Rule("Intersection", (Total,Total), apply_intersection)


# Input is (Total)
def apply_allmine(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError

    if a == b == len(S):
        return [Mine(x) for x in S]
    else:
        return []

rule_allmine = Rule("AllMine", tuple([Total]), apply_allmine)


# Input is (Total)
def apply_allsafe(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError

    if a == b == 0:
        return [Safe(x) for x in S]
    else:
        return []

rule_allsafe = Rule("AllSafe", tuple([Total]), apply_allsafe)


# Input is (Total,Mine)
def apply_remmine(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError
    
    match args[1]:
        case Mine(x):
            pass
        case _:
            raise ValueError
    
    if x in S:
        return [Total(max(0,a-1), b-1, S-{x})]
    else:
        return []

rule_remmine = Rule("RemMine", (Total,Mine), apply_remmine)


# Input is (Total,Safe)
def apply_remsafe(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError
    
    match args[1]:
        case Safe(x):
            pass
        case _:
            raise ValueError
    
    if x in S:
        return [Total(a, min(b,len(S)-1), S-{x})]
    else:
        return []

rule_remsafe = Rule("RemSafe", (Total,Safe), apply_remsafe)


# for testing
v = Total(0,4,{1,2,3,4,5})
w = Total(0,0,{1,2,3,4,5,6})
x = Total(1,2,{1,2,3,4,5})
y = Total(5,6,{3,4,5,6,7,8})
z = Total(4,4,{1,2,3,4})