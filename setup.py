from distutils.core import setup

setup(
    name='rlisty',
    version='0.2',
    packages=['rlisty'],
    url='',
    license='',
    author='jeremiahd',
    author_email='jeremiahd@slalom.com',
    description='monitor lists/queue and clients on redis',
    entry_points={
        'console_scripts': [
            'rlisty = rlisty.main',
        ],
    }
)
