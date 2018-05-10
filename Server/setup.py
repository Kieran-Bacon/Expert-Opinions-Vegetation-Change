from setuptools import setup

requires = [
    'google',
    'pyramid',
    'pyramid_jinja2',
    'pydrive'
]

setup(name='ExpertWebtool',
      install_requires=requires,
      version="1.0.0.1",
      entry_points="""\
      [paste.app_factory]
      main = ExpertWebtool:main
      """,
)