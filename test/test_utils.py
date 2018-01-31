from argschema import utils
import pytest
import operator
from argschema.schemas import ArgSchema, DefaultSchema
from argschema import fields, ArgSchemaParser
import marshmallow as mm

def test_merge_value_add():
    a = {'key':['a']}
    b = {'key':['b']}
    c=utils.merge_value(a,b,'key')
    assert(len(c)==2)

def test_merge_value_subtract():
    a = {'key':10}
    b = {'key':2}
    c=utils.merge_value(a,b,'key',operator.sub)
    assert(c==8)

def test_merge_value_fail():
    a = {'key':5}
    b = {}
    with pytest.raises(Exception):
        c=utils.merge_value(a,b,'key')

def test_smart_merge():
    a = {'a':5,'b':8}
    b = {'a':10}
    c = utils.smart_merge(a,b)
    assert(c['a']==10)
    assert(c['b']==8)

def test_smart_merge_same():
    a = {'a':3,'b':8}
    b = {'a':3}
    c = utils.smart_merge(a,b)
    assert(c['a']==3)
    assert(c['b']==8)

def test_smart_merge_add():
    a = {'a':[1],'b':8}
    b = {'a':[2]}
    c = utils.smart_merge(a,b,merge_keys=['a'])
    assert(len(c['a'])==2)
    assert(1 in c['a'])
    assert(2 in c['a'])

def test_smart_merge_not_none():
    a = {'a':1,'b':8}
    b = {'a':None,'c':9}
    c = utils.smart_merge(a,b,merge_keys=['a'])
    assert(c['a']==1)
    assert(c['c']==9)

def test_smart_merge_none():
    a = {'a':1,'b':8,'c':5}
    b = {'c':None,'d':None}
    c = utils.smart_merge(a,b,overwrite_with_none=True)
    assert(c['c'] is None)
    assert(c['d'] is None)


def test_smart_merge_nested():
    a = {'a':1,'b':{'c':4}}
    b = {'b':{'c':5,'d':9}}
    c = utils.smart_merge(a,b)
    assert(c['a']==1)
    assert(c['b']['c']==5)
    assert(c['b']['d']==9)


class Player(DefaultSchema):
    """player information"""
    name = fields.Str(required=True,description="players name")
    number = fields.Int(required=True,validators = (lambda x: x>=0), description="player's number (must be >0)")

class BaseballSituation(ArgSchema):
    """A description of a baseball situation"""
    inning = fields.Int(required=True,description="inning (1-9)",validate = mm.validate.OneOf(range(1,10)))
    bottom = fields.Bool(required=True,description="is it the bottom of the inning")
    score_home = fields.Int(required=True,description="home team score (non-negative)",validate=(lambda x:x>=0))
    score_away = fields.Int(required=True,description="away team score (non-negative)",validate=(lambda x:x>=0))
    outs = fields.Int(required=True, description="number of outs (0-2)",validate=mm.validate.OneOf([0,1,2]))
    balls = fields.Int(required=False,default=0,description="number of balls (0-4)",validate = mm.validate.OneOf([0,1,2,3]))
    strikes = fields.Int(required=True,description="how many strikes (0-2)",validate = mm.validate.OneOf([0,1,2]))
    bases_occupied = fields.List(fields.Int,description="which bases are occupied",validate = mm.validate.ContainsOnly([1,2,3]))
    batter = fields.Nested(Player,required=True,description="who is batting")
    pitcher = fields.Nested(Player,required=True,description="who is pitching")


def test_schema_argparser_with_baseball():
    example_situation = {
        'batter':{
            'name':'Barry Bonds',
            'number':25
        },
        'pitcher':{
            'name':'Roger Clemens',
            'number':21
        },
        'based_occupied':[1,2,3],
        'outs':2,
        'strikes':2,
        'balls':3,
        'inning':9,
        'bottom':True,
        'score_home':2,
        'score_away':3
    }
    schema = BaseballSituation()
    mod = ArgSchemaParser(input_data = example_situation, schema_type=BaseballSituation,args=[])
    parser = utils.schema_argparser(schema)
    help = parser.format_help()
    help = help.replace('\n','').replace(' ','')
    assert('--strikesSTRIKEShowmanystrikes(0-2)(REQUIRED)(validoptionsare[0,1,2])' in help)
    assert('--bases_occupied[BASES_OCCUPIED[BASES_OCCUPIED...]]whichbasesareoccupied(constrainedlist)(validoptionsare[1,2,3])' in help)
    assert('--ballsBALLSnumberofballs(0-4)(default=0)(validoptionsare[0,1,2,3])' in help)
    assert("--pitcher.numberPITCHER.NUMBERplayer'snumber(mustbe>0)(REQUIRED)" in help)
