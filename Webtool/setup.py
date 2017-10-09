from setuptools import setup

requires = [
    'pyramid',
]

setup(name='ExpertWebtool',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ExpertWebtool:main
      """,
)