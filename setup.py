"""setup.py for Blenderfarm"""

from distutils.core import setup

setup(
    # User-facing application name.
    name="Blenderfarm",

    version="0.1.0",

    author="Jon Ross",
    author_email="jonross.zlsa@gmail.com",

    # See `blenderfarm/`.
    packages=["blenderfarm"],

    include_package_data=True,

    #license="LICENSE.txt",
    description="",

    #long_description=open("README.txt").read(),

    install_requires=[

    ]

)
