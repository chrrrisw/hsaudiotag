from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
]

setup(
    name='hsaudiotag',
    version='1.0.0',
    author='Hardcoded Software',
    author_email='hsoft@hardcoded.net',
    packages=['hsaudiotag'],
    scripts=[],
    url='http://hg.hardcoded.net/hsaudiotag/',
    license='BSD License',
    description='Read metdata (tags) of mp3, mp4, wma, ogg, flac and aiff files.',
    long_description=open('README').read(),
    classifiers=CLASSIFIERS,
)