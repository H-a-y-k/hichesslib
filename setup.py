from distutils.core import setup
import hichess

setup(
  name = "hichesslib",
  packages = ["hichess"],
  version = hichess.__version__,
  license="gpl-3.0+",
  description = hichess.__doc__.replace('\n', ' '),
  author = hichess.__author__,
  author_email = hichess.__email__,
  url = "https://github.com/H-a-y-k/hichesslib",
  download_url = "https://github.com/H-a-y-k/hichesslib/archive/1.2.3.tar.gz",
  keywords = ["chess", "Qt", "PySide2", "GUI"],
  install_requires= [
          "python_chess",
          "PySide2"
      ],
  classifiers=[
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Games/Entertainment :: Board Games",
    "Topic :: Games/Entertainment :: Turn Based Strategy",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3 :: Only",
  ],
  python_requires='>=3.6'
)