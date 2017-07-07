import os
from collections import defaultdict, Iterable
import itertools

from base import AsyBase, AsyError


class AsyWriter(object) :

    def __init__(self, filename=None, size=(500,0), unitsize=None, imports=[], flip_y=False) :

        self.asy = AsyBase(filename)

        self.asy.linecomment('setup', 80)
        if size :
            self.asy.call('size', size[0], size[1])

        if unitsize :
            self.asy.call('unitsize', unitsize)
        self.asy.writeline()

        self.asy.linecomment('asywriter preamble', 80)
        for line in open(os.path.join(os.path.dirname(__file__), 'preamble.asy')) :
            self.asy.write(line)
        self.asy.writeline()

        if imports :
            self.asy.linecomment('user imports', 80)
            for name in imports :
                self.asy.writeline('import %s;' % name)
            self.asy.writeline()


        self.asy.linecomment('generated drawing', 80)

        self.flip_y = flip_y
        self.declared_var_count = 0


    def compile(self, *args, **kwargs) :
        return self.asy.compile(*args, **kwargs)


    def label(self, obj, text, pen='black', transform=None) :
        drawable_code = self._drawable_code(obj)
        if drawable_code :
            self.asy.label(self._quote(text),
                           self._apply_transforms(drawable_code, transform=transform),
                           self._pen_code(pen))

    def dot(self, obj, pen='black', label=None, transform=None) :
        drawable_code = self._drawable_code(obj)
        if drawable_code :
            self.asy.dot(self._quote(label),
                         self._apply_transforms(drawable_code, transform=transform),
                         self._pen_code(pen))

    def draw(self, obj, stroke='black', fill=None, label=None, transform=None) :
        call = ('fill' if fill else '') + ('draw' if stroke else '')
        drawable_code = self._drawable_code(obj)
        if call and drawable_code :
            if fill :
                drawable_code = 'make_cyclic(%s)' % drawable_code
            self.asy.call(call, self._quote(label),
                          self._apply_transforms(drawable_code, transform=transform),
                          self._pen_code(fill), self._pen_code(stroke))


    def declare_variable(self, obj, name=None) :
        drawable = self._convert_to_drawable(obj)
        if drawable :
            datatype, code = drawable

            if not name :
                name = '_var_%d' % self.declared_var_count
                self.declared_var_count += 1

            self.asy.declare_variable(datatype, name, code)
            return name

        else :
            raise AsyError('could not convert to drawable', o)


    def _transforms_code(self, transform=None) :
        all_transforms = [transform] if transform else []
        return '*'.join(all_transforms)

    def _apply_transforms(self, code, transform=None) :
        transforms_code = self._transforms_code(transform=transform)
        if transforms_code :
            return '%s*(%s)' % (transforms_code, code)
        else :
            return code

    def _convert_to_drawable(self, obj) :
        drawable = convert_to_drawable(obj)
        if drawable :
            datatype, code = drawable
            if self.flip_y :
                return datatype, 'scale(1,-1)*(%s)' % code
            else :
                return datatype, code

    def _drawable_code(self, obj) :
        if obj :
            drawable = self._convert_to_drawable(obj)
            if drawable :
                return drawable[1]

            elif isinstance(obj, str) :
                return obj

            elif obj :
                raise AsyError('could not convert to drawable', obj)

    def _pen_code(self, obj) :
        if obj :
            pen = convert_to_pen(obj)
            if pen :
                return pen

            if isinstance(obj, str) :
                return obj

            elif obj :
                raise AsyError('could not convert to pen', obj)


    def _quote(self, txt) :
        if txt is not None :
            return '"$' + str(txt) + '$"'


DRAWABLE_CONVERTERS = defaultdict(list)
PEN_CONVERTERS = defaultdict(list)

def drawable_converter(*types) :
    def decorator(f):
        if types :
            for t in types :
                DRAWABLE_CONVERTERS[t].append(f)
        else :
            DRAWABLE_CONVERTERS[None].append(f)
        return f
    return decorator

def pen_converter(*types) :
    def decorator(f):
        if types :
            for t in types :
                PEN_CONVERTERS[t].append(f)
        else :
            PEN_CONVERTERS[None].append(f)
        return f
    return decorator


def convert_to_drawable(o) :
    def convert(o) :
        return try_converters(DRAWABLE_CONVERTERS, o)

    drawable = convert(o)
    if drawable :
        return drawable

    # if list/iterable, and can convert 1st element : make a path
    if isinstance(o, Iterable) :
        o = list(o)
    if isinstance(o, list) and o :
        if convert(o[0]) :
            return 'path', '--'.join(convert(e)[1] for e in o)

        # if nested list/iterable, and can convert 1st element : make a complex path
        if isinstance(o[0], Iterable) :
            o[0] = list(o[0])
        if isinstance(o[0], list) and o[0] :
            if convert(o[0][0]) :
                return 'path[]', '^^'.join('--'.join(convert(e)[1] for e in es) for es in o)


def convert_to_pen(o) :
    def convert(o) :
        pen = try_converters(PEN_CONVERTERS, o)
        if pen :
            return pen
        elif isinstance(o, str) :
            return o

    pen = convert(o)
    if pen :
        return pen

    # if list/iterable, and can convert 1st element : return sum
    if isinstance(o, Iterable) :
        o = list(o)
    if (isinstance(o, list) or isinstance(o, tuple)) and o :
        if convert(o[0]) :
            return '+'.join(map(convert, o))



def try_converters(all_converters, o) :
    # try converters registered for exact type
    for converter in all_converters.get(type(o),[]) :
        drawable = converter(o)
        if drawable :
            return drawable

    # try all converters (input may be a subclass of a registered type)
    for t, converters in all_converters.iteritems() :
        if t == None or isinstance(o,t) :
            for converter in converters :
                drawable = converter(o)
                if drawable :
                    return drawable
