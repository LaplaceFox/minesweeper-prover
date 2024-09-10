from dataclasses import dataclass
from itertools import product

# TODO: Use rem field of Update

class Prop:
    def __hash__(self):
        return hash(str(self))

    def try_rule(self,props,rule):
        print("Applying %s" % rule.name)

        new_props = Update([],[])

        arity = len(rule.types)

        # Try to use prop in each slot in rule premise
        for i in range(arity):

            # If not applicable in this slot, try next
            if not isinstance(self,rule.types[i]):
                continue
            
            prop_domain = list(product(*[[p for p in props if isinstance(p, rule.types[j])] if i != j else [self] for j in range(arity)]))

            """ print("prop_domain")
            for p in prop_domain:
                print(p)
            """
            
            for inputs in prop_domain:
                print("Trying inputs", str(inputs))
                results = rule.apply(*inputs)

                print("Found:", str(results))

                new_props += results

        return new_props

    def try_all_rules(self,props,rules):
        new_props = Update([],[])
        for rule in rules:
            new_props += self.try_rule(props,rule)
            print()
        return new_props


@dataclass
class Mine(Prop):
    cell: int

    __hash__ = Prop.__hash__

    def __init__(self,cell):
        self.cell = cell

@dataclass
class Safe(Prop):
    cell: int

    __hash__ = Prop.__hash__

    def __init__(self,cell):
        self.cell = cell

@dataclass
class Total(Prop):
    bounds: "tuple[int,int]"
    region: "set[int]"

    __hash__ = Prop.__hash__

    def __init__(self,low,high,region):
        self.bounds = (low,high)
        self.region = region

@dataclass
class Update:
    add: "list[Prop]"
    rem: "list[Prop]"

    def __init__(self,add,rem):
        self.add = add
        self.rem = rem

    # Combine without duplicates
    def __add__(self,other):
        new_add = list(set(self.add + other.add))
        new_rem = list(set(self.rem + other.rem))

        return Update(new_add,new_rem)

class Rule:
    #name: Rule name as string
    #type: Tuple of types in rule premise
    #applyfn: Takes props of correct types, returns Update object
    
    def __init__(self,name,types,applyfn):
        self.name = name
        self.types = types
        self.applyfn = applyfn

    def typecheck(self,*args):
        assert len(args) == len(self.types), "Wrong number of arguments for %s" % (self.name)
        assert False not in [isinstance(args[i],self.types[i]) for i in range(len(self.types))], "Argument of wrong type"

    def apply(self,*args) -> Update:
        self.typecheck(*args)
        return self.applyfn(*args)

class LogicState:
    pass

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
        return Update([Total(c-b, d-a, T-S)],[])
    else:
        return Update([],[])

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

    if S <= T or S >= T: # conclusion would be redundant or handled by subset
        return Update([],[])        
    elif len(S & T) == 0: # disjoint
        return Update([],[])
    else:
        return Update([Total(0, len(S & T), S & T)],[])
    
rule_intersection = Rule("Intersection", (Total,Total), apply_intersection)


# Input is (Total)
def apply_allmine(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError

    if a == b == len(S):
        return Update([Mine(x) for x in S],[])
    else:
        return Update([],[])

rule_allmine = Rule("AllMine", tuple([Total]), apply_allmine)


# Input is (Total)
def apply_allsafe(*args):
    match args[0]:
        case Total([a,b],S):
            pass
        case _:
            raise ValueError

    if a == b == 0:
        return Update([Safe(x) for x in S],[])
    else:
        return Update([],[])

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
        return Update([Total(max(0,a-1), b-1, S-{x})],[])
    else:
        return Update([],[])

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
        return Update([Total(a, min(b,len(S)-1), S-{x})],[])
    else:
        return Update([],[])

rule_remsafe = Rule("RemSafe", (Total,Safe), apply_remsafe)

usable_rules = [rule_subset, rule_intersection, rule_allmine, rule_allsafe, rule_remmine, rule_remsafe]

# for testing
v = Total(0,4,{1,2,3,4,5})
w = Total(0,0,{1,2,3,4,5,6})
x = Total(1,2,{1,2,3,4,5})
y = Total(5,6,{3,4,5,6,7,8})
z = Total(4,4,{1,2,3,4})


#Example puzzle:
puzzle = \
    [
        Total(3,3,{1,2,3,6,7,8}),
        Total(4,4,{2,3,4,7,8,9,12,13,14}),
        Total(3,3,{5,6,7,10,11,12,15,16,17}),
        Total(3,3,{10,11,12,15,16,17,20,21,22}),
        Total(1,1,{15,16,17,20,21,22}),
        Safe(2), Safe(8), Safe(11), Safe(16), Safe(21)
    ]