#!/usr/bin/python

import os, sys, string

###
#
# Implements a simple calculator.
#
# Reads lines from stdin (keyboard) and computes the answer.
# Lines can look like this:
#  1 + 2 * 3
#  (5-2)/3.0
#  5*2**3
#  0x7f - 0o7 + 0b101
#
# Unary operations include:
#  + Unary plus (positives)
#  - Unary minus (negatives)
#  ~ Unary bitwise negation
#
# Binary operations include:
#  + Addition
#  - Subtraction
#  * Multiplication
#  / Division
#  % Modulo
#  << Bitwise left shift
#  >> Bitwise right shift
#  &  Bitwise AND
#  ^  Bitwise XOR
#  |  Bitwise OR
#  ** Exponentiation
#
# Bitwise operations and modulo only work on integer arguments.
# All other operations should work on integers or floating point numbers.
# Division and exponentiation operations produce floating point results.
#
# Press Ctrl-D to exit the program cleanly.
#
###

UNARYOP  = 1
BINARYOP = 2
SUBEXPR  = 3

LEFT  = 'L'
RIGHT = 'R'

Op_Sets: tuple[int, str, list[str]] = [
	( BINARYOP, LEFT,  ["|"] ),			# Bitwise OR
	( BINARYOP, LEFT,  ["^"] ),			# Bitwise XOR
	( BINARYOP, LEFT,  ["&"] ),			# Bitwise AND
	( BINARYOP, LEFT,  ["<<", ">>"] ),		# Bit shifts
	( BINARYOP, LEFT,  ["+", "-"] ),		# Addition and Subtraction
	( BINARYOP, LEFT,  ["*", "/", "%"] ),		# Multiplication, Division, Modulo
	( UNARYOP,  RIGHT, ["+ x", "- x", "~ x"] ),	# Positive, Negative, Bitwise NOT
	( BINARYOP, RIGHT, ["**"] ),			# Exponentiation
]

Op_Table = {}
def build_Op_Table():
	precedence = 0
	for kind, associativity, ops in Op_Sets:
		precedence += 1
		for op in ops:
			Op_Table[op] = (kind, associativity, precedence)

# Note the following are listed in order of longest to shortest.
Predefined_Tokens: list[str] = [
	"**",
	"<<", ">>",
	"(", ")",
	"~",
	"+", "-", "*", "/", "%",
	"|", "^", "&",
]

# Break the line into a list of string tokens.
# E.g. "(3+17<<2)" becomes ["(", "3", "+", "17", "<<", "2", ")"]
def tokenise(line: str) -> list[str]:
	tokens = []
	start = 0
	while start < len(line):
		# Skip whitespace.
		if line[start:start+1] in " \t\n":
			start += 1
			continue

		# Remember any predefined token.
		found_punct = False
		for tok in Predefined_Tokens:
			finish = start + len(tok)
			if line[start:finish] == tok:
				tokens.append(tok)
				start = finish
				found_punct = True
				break
		if found_punct:
			continue

		# Remember any numbers.
		i = start
		while i < len(line) and line[i] in "0123456789abcdefABCDEF.xXbo":
			i += 1
		if i > start:
			tok = line[start:i]
			tokens.append(tok)
			start = i
			continue

		# Incomprehensible character?
		break

	return tokens

class Expr:
	def __init__(self, tok: str = None, op: str = None, left=None, right=None):
		self.tok   = tok
		self.op    = op
		self.left  = left
		self.right = right

	def __str__(self) -> str:
		s = "("
		if self.tok:   s += "Token: " + str(self.tok) + " "
		if self.left:  s += "Left: "  + str(self.left) + " "
		if self.op:    s += "Op: "    + str(self.op) + " "
		if self.right: s += "Right: " + str(self.right) + " "
		return s[:-1] + ")"

	def __repr__(self) -> str:
		return str(self)

	def is_empty(self) -> bool:
		if self.tok:   return False
		if self.op:    return False
		if self.left:  return False
		if self.right: return False
		return True

	def is_token(self) -> bool:
		if self.tok: return True
		return False

	def is_unary_expr(self) -> bool:
		if self.op and not self.left and self.right:
			return True
		return False

	def is_parenth_expr(self) -> bool:
		if not self.op and not self.left and self.right:
			return True
		return False

	def is_binary_exprs(self) -> bool:
		if self.op and self.left and self.right:
			return True
		return False

	def evaluate(self):
		if self.is_token() and type(self.tok) == type(''):
			return to_number(self.tok)
		if self.is_token() and type(self.tok) in [type(0.0), type(0)]:
			return self.tok
		if self.is_parenth_expr():
			return self.right.evaluate()
		if self.op and not self.left and not self.right:
			print("Error:", repr(self), "has too few items.")
			return None

		if not self.left:
			x = None
		elif self.left.is_empty():
			x = None
		else:
			x = self.left.evaluate()

		if not self.right:
			return x
		elif self.right.is_empty():
			y = None
		else:
			y = self.right.evaluate()

		if not self.op:
			# Leaf node.
			if x: x = float(x)
			if y: x = float(y)
			print("Parse error: leaf node wasn't a literal number.")
			return
		elif self.op == '|':    return x | y
		elif self.op == '^':    return x ^ y
		elif self.op == '&':    return x & y
		elif self.op == '<<':   return x << y
		elif self.op == '>>':   return x >> y
		elif self.op == '+':    return x + y
		elif self.op == '-':    return x + y #- initially 
		elif self.op == '*':    return x * y
		elif self.op == '/':
			if y:
				return x / float(y)
			else:
				print("Error: division by zero.")
				return None
		elif self.op == '%':
			if y:
				return x % int(y)
			else:
				print("Error: modulo by zero.")
				return
		elif self.op == '+ x':  return +y
		elif self.op == '- x':  return -y
		elif self.op == '~ x':  return ~int(y)
		elif self.op == '**':   return float(x) ** float(y)
		else:
			print("Error: evaluating")
			return None

class Parser:
	def __init__(self, tokens: list[str] = []):
		self.current_tokens = tokens[:]
		self.current_index = 0

	def set_tokens(self, tokens: list[str] = []):
		self.current_tokens = tokens[:]
		self.current_index = 0

	def parse_error(self, s: str):
		print("Parse error:", s)

	def get_curr_token(self) -> str:
		if self.current_index < len(self.current_tokens):
			return self.current_tokens[self.current_index]
		else:
			return None

	def get_next_token(self) -> str:
		self.current_index += 1
		return self.get_curr_token()

	def parse_atom(self, min_prec: int) -> Expr:
		tok = self.get_curr_token()
		while True:
			if tok is None:
				self.parse_error('source ended unexpectedly')
				return Expr()
			elif tok == '(':
				self.get_next_token()
				subexpr = self.parse_expr()
				if self.get_curr_token() != ')':
					self.parse_error('unmatched "("')
				self.get_next_token()
				return Expr(right=subexpr)
			elif tok in ['-', '+', '~', 'not']:
				op = tok + " x"
				kind, associativity, precedence = Op_Table[op]
				self.get_next_token()
				subexpr = self.parse_expr(precedence)
				return Expr(op=op, right=subexpr)
			elif tok in Op_Table:
				self.parse_error('expected an atom, not an operator "%s"' % tok)
				return Expr()
			else:
				self.get_next_token()
				return Expr(tok=tok)

	def parse_expr(self, min_prec: int = 0) -> Expr:
		lhs = self.parse_atom(min_prec)
		ops = []

		while True:
			if lhs.is_token() and lhs.tok in Op_Table:
				op = lhs.tok
				lhs = None
			else:
				tok = self.get_curr_token()
				if tok is None:
					break
				if tok not in Op_Table:
					break
				op = tok
			# Get the operator's precedence and associativity.
			kind, associativity, precedence = Op_Table[op]
			if precedence < min_prec:
				break

			# Compute a minimal precedence for the recursive call.
			if associativity == LEFT:
				next_min_prec = precedence + 1
			else:
				next_min_prec = precedence

			# Consume the current token and prepare the next one for the
			# recursive call.
			self.get_next_token()
			rhs = self.parse_expr(next_min_prec)

			# Update lhs with the new value.
			if kind == UNARYOP:
				lhs = Expr(op=op, right=rhs) # UNARYOP
			elif lhs.is_token():
				lhs = Expr(op=op, left=lhs, right=rhs) # BINARYOP
			elif lhs.is_parenth_expr():
				lhs = Expr(op=op, left=lhs.right, right=rhs) # BINARYOP
			else:
				prev_op = lhs.op
				prev_kind, prev_associativity, prev_precedence = Op_Table[prev_op]
				if prev_kind == BINARYOP and prev_associativity == associativity and prev_precedence == precedence:
					lhs = Expr(op=op, left=lhs, right=rhs)
				elif kind == UNARYOP:
					lhs = Expr(ops=op, right=rhs) # UNARYOP
				elif kind == BINARYOP:
					lhs = Expr(op=op, left=lhs, right=rhs) # BINARYOP

		return lhs

def to_number(tok: str) -> int | float:
	if tok[:2] == "0x":
		return int(tok[2:], 16)
	if tok[:2] == "0X":
		return int(tok[2:], 16)
	if tok[:2] == "0o":
		return int(tok[2:], 8)
	if tok[:2] == "0b":
		return int(tok[2:], 2)
	if '.' in tok:
		return float(tok)
	if 'e' in tok:
		return float(tok)
	if 'E' in tok:
		return float(tok)
	return int(tok)

def parse_and_print(line: str):
	tokens = tokenise(line)
	if not tokens:
		return

	parser = Parser(tokens)
	expr = parser.parse_expr()
	print(expr.evaluate())

def parse(line: str):
	tokens = tokenise(line)
	if not tokens:
		return None

	parser = Parser(tokens)
	expr = parser.parse_expr()
	return expr.evaluate()

def setup():
	build_Op_Table()

def main():
	setup()
	if len(sys.argv) > 1:
		lines = sys.argv[1:]
		for line in lines:
			parse_and_print(line)
	else:
		line = sys.stdin.readline()
		while line:
			parse_and_print(line)
			line = sys.stdin.readline()

if __name__ == '__main__':
	main()
