import pickle
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

WORDNET_DIR = Path("/Users/d-manakovskiy/Downloads/WordNet-3.0/glosstag/merged")


@dataclass
class DictEntry:
    terms: list[str]
    meanings: list[str]
    examples: list[str]


def parse_words(file: Path):
    dictionary = []
    tree = ET.parse(file.absolute())
    root = tree.getroot()
    for synset in root:
        terms = [t.text for t in synset[0]]
        meaning_node = None
        for child in synset:
            if child.tag == "gloss" and child.attrib['desc'] == 'orig':
                meaning_node = child
                break
        else:
            print(f"Did not find meaning_node for {terms[0]}")
            continue
        meanings_and_examples = [
            s.strip()
            for s in  meaning_node[0].text.split(";")
            if s.strip()
        ]
        meanings = []
        examples = []
        for entry in meanings_and_examples:
            if entry[0] == '"':
                examples.append(entry)
            else:
                meanings.append(entry)
        dictionary.append([terms, meanings, examples])

    with open(file.name+".pick", 'wb') as f:
        pickle.dump(dictionary, f)

def main():
    # for file in WORDNET_DIR.glob('*'):
    #     parse_words(file)

    corpus = []
    for file in Path('./').glob('*.pick'):
        with file.open('rb') as f:
            corpus.extend(pickle.load(f))

    a = 3

if __name__ == '__main__':
    main()
