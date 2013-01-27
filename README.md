Twitter misspellings
======

Enter a name and search twitter to find instances in which it is misspelled.

Example:
    python scripts/search.py --name=Barack+Obama --max=5
    
For each name, we make two searches: One for the correct first name followed by variants of the last name, and vice versa
At the moment, a variant consists of any word that begins with the same letter as the correct name. In the future, it will include a more sophisticated Levenshtein distance

