import os
import tempfile
import subprocess



class AsyBase(object) :
    def __init__(self, filename=None) :

        if filename :
            self.file = open(filename, 'w')
            self.filename = filename
        else :
            self.file = tempfile.NamedTemporaryFile(suffix='.asy', delete=False)
            self.filename = self.file.name


    def call(self, cmd, *args) :
        self.writeline(cmd + '(' + ', '.join(str(arg) for arg in args if arg) + ');')


    def comment(self, txt) :
        self.writeline('/* ' + txt + ' */')


    def draw(self, *args) :
        self.call('draw', *args)


    def fill(self, *args) :
        self.call('fill', *args)


    def filldraw(self, *args) :
        self.call('filldraw', *args)


    def label(self, *args) :
        self.call('label', *args)


    def dot(self, *args) :
        self.call('dot', *args)


    def writeline(self, line) :
        self.file.write(line + '\n')


    def compile(self, filename=None, asy_path='asy') :
        if not filename :
            filename = self.filename.replace('.asy', '') + '.pdf'

        compile_cmd = [
            asy_path,
            '-f', 'pdf',
            '-o', filename,
            self.filename
        ]

        self.file.flush()
        process = subprocess.Popen(
            compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out,err = process.communicate()
        if process.returncode != 0 :
            raise AsyError(err)


class AsyError(StandardError) :
    pass
