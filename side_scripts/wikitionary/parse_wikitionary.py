import pickle
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

ARTICLES_FILE = Path("/Users/d-manakovskiy/Downloads/enwiktionary-20231101-pages-articles.xml")


def main():
    tree = ET.parse(ARTICLES_FILE.absolute())
    root = tree.getroot()

    a = 3


if __name__ == '__main__':
    main()
