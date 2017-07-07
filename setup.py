from setuptools import setup

setup(name='asywriter',
    version='0.0.1',
    description='write and compile Asymptote files',
    url='https://github.com/snoyer/asywriter',
    author='snoyer',
    author_email='reach me on github',
    packages=['asywriter'],
    package_data={'asywriter': ['*.asy']},
    include_package_data=True,
    zip_safe=False,
)
