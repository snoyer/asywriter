from base import AsyBase
from writer import AsyWriter, drawable_converter, pen_converter, convert_to_drawable



@drawable_converter(tuple)
def tuple_pair(o) :
        return 'pair', '(' + str(o[0]) + ',' + str(o[1]) + ')'

@drawable_converter(complex)
def complex_pair(o) :
    return 'pair', '(' + str(o.real) + ',' + str(o.imag) + ')'


@pen_converter(tuple)
def rgb_pen(o) :
    if len(o) == 3 :
        return 'rgb(%f,%f,%f)' % o

    if len(o) == 4 :
        return 'rgb(%f,%f,%f)+opacity(%f)' % o

@pen_converter(float, int)
def number_pen(o) :
    if o :
        return str(o)
