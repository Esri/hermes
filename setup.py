from setuptools import setup,find_packages


with open('src/hermes/version.py') as fin: exec(fin.read())

setup(
    name='esri-hermes',
    version=__version__,

    package_dir={'':'src'},
    packages=find_packages('src'),
    include_package_data=True,

    # PyPI MetaData
    author='achapkowski',
    author_email='achapkowski@esri.com',
    description='Collection of Utilities to Read/Write a Dataset\'s Metadata',
    license='Apache License - 2.0',
    keywords='esri,arcpy,metadata',
    url='https://github.com/Esri/hermes',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ),

    zip_safe=False,
)
