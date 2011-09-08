from distutils.core import setup

setup(
      name='scrapy_lxmlselector',
      version='dev',
      description='Lxml Selector for Scrapy',
      author='smorin',
      author_email='steeve.morin@gmail.com',
      url='https://github.com/steeve/scrapy-lxmlselector',
      py_modules=['lxmlselector'],
      install_requires=[
        'lxml',
        'scrapy',
      ],
)
