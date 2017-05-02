from base import AsyBase

DEFAULT_IMPORTS = ['geometry', 'palette']

class AsyWriter(object) :

    def __init__(self, filename=None, size=(500,0), unitsize=None, imports=[], flip_y=False) :

        self.asy = AsyBase(filename)

        if size :
            self.asy.call('size', size[0], size[1])

        if unitsize :
            self.asy.call('unitsize', unitsize)

        for name in DEFAULT_IMPORTS + imports :
            self.asy.writeline('import %s;' % name)


        self.flip_y = flip_y


    def compile(self, *args, **kwargs) :
        return self.asy.compile(*args, **kwargs)


    def label(self, point, text, pen='black', transform=None) :
        self.asy.dot(self._quote(text), self._pair(point, transform), self._pen(pen))

    def dot(self, point, pen='black', label=None, transform=None) :
        self.asy.dot(self._quote(label), self._pair(point, transform), self._pen(pen))


    def dots(self, points, pen='black', label=None, transform=None) :
        self.asy.dot(self._quote(label), self._path(points, transform=transform), self._pen(pen))


    def line(self, points, pen='black', label=None, transform=None) :
        self.asy.draw(self._quote(label), self._path(points, transform=transform), self._pen(pen))


    def polygon(self, points, stroke='black', fill=None, label=None, transform=None) :
        self.complex_polygon([points], stroke, fill, label, transform)


    def complex_polygon(self, pointss, stroke='black', fill=None, label=None, transform=None) :
        call = self._which_filldraw(fill, stroke)
        if call :
            self.asy.call(call, self._quote(label),
                          self._complexpath(pointss, transform),
                          self._pen(fill), self._pen(stroke)
                         )


    def circle(self, center, radius, stroke='black', fill=None, label=None, transform=None) :
        call = self._which_filldraw(fill, stroke)
        if call :
            self.asy.call(call, self._quote(label),
                          self._circle(center, radius, transform),
                          self._pen(fill), self._pen(stroke)
                         )


    def _which_filldraw(self, fill, stroke) :
        return ('fill' if fill else '')+('draw' if stroke else '')


    def _complexpath(self, pointss, transform=None) :
        s = '^^'.join(self._path(points, cycle=True) for points in pointss)
        if transform :
            s = transform + '*(' + s + ')'
        return s


    def _path(self, points, cycle=False, transform=None) :
        s = '--'.join(self._pair(point) for point in points)
        if cycle :
            s += "--cycle"
        if transform :
            s = transform + '*(' + s + ')'
        return s


    def _pair(self, pt, transform=None) :
        if isinstance(pt, complex) :
            x,y = pt.real, pt.imag
        else :
            x,y = pt[:2]
        if self.flip_y :
            y = -y
        s = '(' + str(x) + ',' + str(y) + ')'
        if transform :
            s = transform + '*(' + s + ')'
        return s


    def _circle(self, center, radius, transform=None) :
        s = 'circle('+self._pair(center)+','+str(radius)+')'
        if transform :
            s = transform + '*(' + s + ')'
        return s


    def _pen(self, pen) :
        if not pen :
            return None
        if isinstance(pen, str) :
            return pen
        if isinstance(pen, tuple) :
            r,g,b = pen[:3]
            return 'rgb(%f,%f,%f)' % (r,g,b)


    def _quote(self, txt) :
        if txt is not None :
            return '"$' + str(txt) + '$"'
