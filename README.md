# japanese-number-converter

Converts [Japanese kanji numerals](https://en.wikipedia.org/wiki/Japanese_numerals) into full-width numerals and arabic numbers.

Based on
[kitagawa-hr/japanese-number-converter](https://github.com/kitagawa-hr/japanese-numbers-converter) which is based on
[twada/japanese-numerals-to-number](https://github.com/twada/japanese-numerals-to-number).

## Usage

### Original Usage

```py
import jnc

assert jnc.ja_to_arabic("九千七兆千九百九十二億五千四百七十四万九百九十一") == 9007199254740991
```

For detail, see [test cases](./test_jnc.py).

### My modifications
#### Ignore non-numerals mode
```py
assert jnc.ja_to_arabic("亜県水戸郡余市東町十二線四号", ignore_non_numerals=True) == "亜県水戸郡余市東町12線4号"
```

#### Output full-width numerals
```py
assert jnc.ja_to_arabic("亜県水戸郡余市東町十二線四号", ignore_non_numerals=True, full_width_output=True) == "亜県水戸郡余市東町１２線４号"
```

## Installation

```sh
pip install "git+https://github.com/Flurrywinde/japanese-numbers-converter.git"
```

## Supported formats

### numbers 0 to 9

- `〇`, `一`, `二`, `三`, `四`, `五`, `六`, `七`, `八`, `九`

### names of powers of 10

- `十`, `百`, `千`, `万`, `億`, `兆`

### [formal numerals (daiji) used in legal documents](https://en.wikipedia.org/wiki/Japanese_numerals#Formal_numbers)

- `壱`, `弐`, `参`, `拾`
