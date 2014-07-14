#!/usr/bin/env python
#encoding: UTF-8

"""
__   ___________________________________________
| \  ||______   |   |______|_____||______|______
|  \_||______   |   |______|     |______||______
                                                
________     __________________________  _____ _     _
|  |  ||     ||______  |  |      |_____]|     | \___/ 
|  |  ||_____|______|__|__|_____ |_____]|_____|_/   \_


+ ------------------------------------------ +
|   NetEase-MusicBox               320kbps   |
+ ------------------------------------------ +
|                                            |
|   ++++++++++++++++++++++++++++++++++++++   | 
|   ++++++++++++++++++++++++++++++++++++++   |
|   ++++++++++++++++++++++++++++++++++++++   |
|   ++++++++++++++++++++++++++++++++++++++   |
|   ++++++++++++++++++++++++++++++++++++++   |
|                                            |
|   A sexy cli musicbox based on Python      |
|   Music resource from music.163.com        |
|                                            |
|   Built with love to music by @vellow      |
|                                            |
+ ------------------------------------------ +

"""


from setuptools import setup, find_packages


setup(
    name = "NetEase-MusicBox",
    version = "0.1",
    packages = find_packages(),

    include_package_data = True,

    install_requires = {
        "curses",
        "locale",
        "sys",
        "os",
        "json",
        "time",
        "subprocess",
        "threading",
        "signal",
        "re",
        "requests",
        "hashlib",
        "webbrowser"
    },

    entry_points = {
        "console_scripts" : [
            "musicbox = src:start"
        ],
    },

    author = "vellow",
    author_email = "i@vellow.net",
    url = "https://github.com/vellow/NetEase-MusicBox",
    description = "A sexy command line interface musicbox"
)