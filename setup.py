from distutils.core import setup

setup(
      name='scrapy_lxmlselector',
      version='dev',
      description='Lxml Selector for Scrapy',
      author='smorin',
      author_email='steeve.morin@gmail.com',
      url='https://github.com/steeve/scrapy-lxmlselector',
      packages=['lxmlselector.py'],
      install_requires=[
        'lxml',
        'scrapy',
      ],
)
