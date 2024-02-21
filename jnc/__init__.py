import re

__version__ = "1.0.1"


class BaseJapaneseNumeralsException(Exception):
	pass


class ValidationError(BaseJapaneseNumeralsException):
	pass


class ParseError(BaseJapaneseNumeralsException):
	pass


class NotSupportedError(BaseJapaneseNumeralsException):
	pass


UNITS = [
	("兆", 10 ** 12),
	("億", 10 ** 8),
	("万", 10 ** 4),
	("千", 10 ** 3),
	("百", 10 ** 2),
	("十", 10),
]

JAPANESE_DIGITS = {
	"〇": 0,
	"一": 1,
	"二": 2,
	"三": 3,
	"四": 4,
	"五": 5,
	"六": 6,
	"七": 7,
	"八": 8,
	"九": 9,
}


DAIJI_TRANS = str.maketrans(
	{
		"零": "〇",
		"壱": "一",
		"弐": "二",
		"参": "三",
		"拾": "十",
	}
)

UNIT_CHARS = "".join(u for (u, _) in UNITS)
JAPANESE_DIGIT_CHARS = "".join(JAPANESE_DIGITS)
SUPPORTED_CHARS = UNIT_CHARS + JAPANESE_DIGIT_CHARS
SUPPORTED_REGEX = re.compile(rf"^[{SUPPORTED_CHARS}]+$")

def single2double(s):
	trans = str.maketrans('0123456789', '０１２３４５６７８９')
	return s.translate(trans)

def validate(s: str) -> None:
	if s == "":
		raise ValidationError("Empty string")
	if re.search(r"一[百十]", s):
		raise ValidationError("'一百' and '一十' are invalid in common writing. 100 is just '百', and 10 is just '十'")
	if re.search(rf"([^{JAPANESE_DIGIT_CHARS}]|^)千[万億兆]", s):
		raise ValidationError(
			"if '千' directly precedes the name of powers of myriad, '一' is normally attached before '千'"
		)
	if re.search(rf"[{JAPANESE_DIGIT_CHARS}]{{2,}}[十百千]", s):
		raise ValidationError("Each place (十,百,千) should not have more than one digit")
	if re.search(r"([万億兆]{2,}|^[万億兆])", s):
		raise ValidationError("万,億,兆 cannot be adjacent to each other or be the first character of the sequence")


def parse(s: str, index: int = 0) -> int:
	if len(s) == 0:
		return 0
	if index >= len(UNITS):
		if s.startswith("〇"):
			raise ParseError("Positional notation or place of '一' should not start with zero")
		if not re.match(rf"^[{JAPANESE_DIGIT_CHARS}]+$", s):
			raise ParseError("throws Error when name of powers of 10 appears more than once in subsequence")
		return int("".join(str(JAPANESE_DIGITS[c]) for c in s))
	(unit_str, unit_number) = UNITS[index]
	splitted = s.split(unit_str)
	if len(splitted) == 1:
		# unit_str not found
		return parse(splitted[0], index + 1)
	if len(splitted) == 2:
		# one unit_str found
		if splitted[0] == "":
			return unit_number + parse(splitted[1], index + 1)
		if unit_str in {"兆", "億", "万"}:
			# units over 千 is forbid in the left of (兆, 億, 万)
			return unit_number * parse(splitted[0], 3) + parse(splitted[1], index + 1)
		return unit_number * parse(splitted[0], len(UNITS)) + parse(splitted[1], index + 1)
	raise ParseError(f"{unit_str} appears more than once in subsequence {s}")


def ja_to_arabic(s: str, enable_validation: bool = True, accept_daiji: bool = True, ignore_non_numerals: bool = False, full_width_output: bool = False) -> int:
	"""convert japanese number to arabic number

	Args:
		s (str): number in japanese format
		enable_validation (bool, optional): Whether to enable validation or not. Defaults to True.
		accept_daiji (bool, optional): Whether to accept daiji or not. Defaults to True.

	Raises:
		TypeError: raises if s is not str.
		NotSupportedError: raises if s is too long or contains unsupported chars.
		ValidationError: raises if s is uncommon expression like ``千万, 二〇千, 一万兆``.
		ParseError: raises if s is not parsable. (e.g.)``十十, 〇十, 四万三億``

	Returns:
		int: arabic number
	"""
	if not isinstance(s, str):
		raise TypeError(f"{s} is not string")
	if len(s) == 1 and s == "〇":
		# treat zero as special case
		return 0
	if len(s) > 32:
		raise NotSupportedError(f"{s} is too long.")
	if enable_validation:
		validate(s)
	if accept_daiji:
		s = s.translate(DAIJI_TRANS)
	if not ignore_non_numerals:
		# Original mode: raises an error if input contains unsupported characters
		if not SUPPORTED_REGEX.match(s):
			raise NotSupportedError(f"{s} contains unsupported characters. Supported format: {SUPPORTED_REGEX.pattern}")
		if full_width_output:
			return single2double(str(parse(s)))
		else:
			return parse(s)
	else:
		# Ignore non-numerals mode
		ret = ""
		jnum = ""
		for char in s:
			if char in SUPPORTED_CHARS:
				# It's a Japanese numeral
				jnum += char
			else:
				if jnum:
					ret += str(parse(jnum))
				jnum = ""
				ret += char
		if full_width_output:
			ret = single2double(ret)
		return ret
