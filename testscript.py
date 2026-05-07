#!/usr/local/bin/python

import sys
import Calc

def test_parse_function():
	num_tests = 0
	num_passed = 0

	for expected_success, expected_output, input_data in [
		( True ,	3,	"3" ),
		( True ,	5,	"3+2" ),
		( False,	None,	"3+a" ),
		( True ,	7,	"3+2*2" ),
		( True ,	5,	"14/7+3" ),
        ( True ,	28,	"9*2+10" ),
		(True, 125, "0x7f - 0o7 + 0b101")

	]:
		num_tests += 1
		try:
			actual_output = Calc.parse(input_data)
			actual_success = True
		except:
			actual_output = None
			actual_success = False

		if expected_success != actual_success:
			print("FAIL: %s expected_success=%s actual=%s" %
				(input_data, expected_success, actual_success))
			continue
		if expected_success and expected_output != actual_output:
			print("FAIL: %s expected_output=%s actual=%s" %
				(input_data, expected_output, actual_output))
			continue
		print("PASS: " + input_data)
		num_passed += 1

	return num_tests, num_passed

def main():
	Calc.setup()
	num_tests, num_passed = test_parse_function()
	if num_tests > num_passed:
		print("BAD: %d / %d tests passed." % (num_passed, num_tests))
		sys.exit(1)
	print("GOOD: %d / %d tests passed." % (num_passed, num_tests))

if __name__ == "__main__":
	main()

