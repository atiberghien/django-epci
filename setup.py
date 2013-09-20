from distutils.core import setup

setup(
    name='django-epci',
    version = '0.x',
    
    author = 'Alban Tiberghien (@atiberghien)',
    description = 'Geographic data (cities and epci boundaries) for France sub-regions',
    license = 'GNU GPL V3',
    
    packages = ['epci', 'epci/management', 'epci/fixtures']
)