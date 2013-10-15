from distutils.core import setup
setup(
    name = 'DictLiteStore',
    packages = ['DictLiteStore'],
    version = '0.9.1',
    description = 'A (Dynamic-Schema) dict -> sqlite3 library',
    author = 'Daniel Fairhead',
    author_email = 'danthedeckie@gmail.com',
    url = 'https://github.com/danthedeckie/DictLiteStore',
    download_url = 'https://github.com/danthedeckie/DictLiteStore/tarball/0.9.1',
    keywords = ['json', 'dict', 'persistance', 'sqlite', 'dynamic schema'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Licence :: OSI Approved :: GNU General Purpose Public Licence v3 (GPLv3)',
                   'Topic :: Database',
                   'Programming Language :: Python 2.7',

                  ],
    )
