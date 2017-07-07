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

    def linecomment(self, txt, pad=0) :
        comment = '// '+txt.replace('\n','')+ ' '
        self.writeline(comment.ljust(pad, '/'))


    def declare_variable(self, datatype, name, value) :
        self.writeline('%s %s = %s;' % (datatype, name, value))


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


    def write(self, txt) :
        self.file.write(txt)

    def writeline(self, txt='') :
        self.file.write(txt + '\n')


    def compile(self, filename=None, include=None, asy_path='asy') :
        if not filename :
            filename = self.filename.replace('.asy', '') + '.pdf'

        compile_cmd = [
            asy_path,
            '-f', 'pdf',
            '-o', filename,
            self.filename
        ]

        if include is not None:
            if isinstance(include, str) :
                include = [include]
            with tempfile.NamedTemporaryFile('w', suffix='.asy', delete=False) as cfg :
                print >>cfg, 'import settings;'
                print >>cfg, 'dir = "' + ':'.join(map(os.path.abspath, include)) + '";'
                compile_cmd += ['-config', cfg.name]

        self.file.flush()
        process = subprocess.Popen(
            compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out,err = process.communicate()
        if process.returncode != 0 :
            raise AsyError(err)

        #TODO cleanup temp file if any


class AsyError(StandardError) :
    pass
