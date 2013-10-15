from distutils.core import setup
from dictlitestore import __version__

setup(
    name = 'DictLiteStore',
    py_modules = ['dictlitestore'],
    version = __version__,
    description = 'A (Dynamic-Schema) dict -> sqlite3 library',
    long_description=open('README.rst','r').read(),
    author = 'Daniel Fairhead',
    author_email = 'danthedeckie@gmail.com',
    url = 'https://github.com/danthedeckie/DictLiteStore',
    download_url = 'https://github.com/danthedeckie/DictLiteStore/tarball/' + __version__,
    keywords = ['json', 'dict', 'persistance', 'sqlite', 'dynamic schema'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Topic :: Database',
                   'Programming Language :: Python :: 2.7',

                  ],
    )
