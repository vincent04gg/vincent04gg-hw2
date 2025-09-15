import pytest
import base64
from text2digits.text2digits import Text2Digits
from num2words import num2words
import sys

class TestLibraryBugs:
    """Test suite to detect bugs in imported/library code"""
    
    def test_text2digits_none_input_bug(self):
        """Test that text2digits handles None input gracefully"""
        t2d = Text2Digits()
        
        # This should not crash with TypeError
        with pytest.raises(TypeError, match="expected string or bytes-like object"):
            t2d.convert(None)
    
    def test_text2digits_very_long_text_bug(self):
        """Test that text2digits handles very long text without memory issues"""
        t2d = Text2Digits()
        
        # Create a very long text that could cause memory issues
        long_text = 'one ' * 10000 + 'thousand'
        
        # This should complete without hanging or crashing
        result = t2d.convert(long_text)
        
        # The result should be reasonable length
        assert len(result) < len(long_text) * 2, "Result should not be excessively long"
    
    def test_text2digits_empty_string_bug(self):
        """Test that text2digits handles empty string correctly"""
        t2d = Text2Digits()
        
        # Empty string should return empty string, not crash
        result = t2d.convert('')
        assert result == '', "Empty string should return empty string"
    
    def test_base64_padding_edge_cases_bug(self):
        """Test that base64 handles edge case padding correctly"""
        
        # Single character should fail with clear error
        with pytest.raises(Exception, match="Invalid base64-encoded string"):
            base64.b64decode('A')
        
        # Two characters should fail with clear error  
        with pytest.raises(Exception, match="Incorrect padding"):
            base64.b64decode('AA')
        
        # Three characters should fail with clear error
        with pytest.raises(Exception, match="Incorrect padding"):
            base64.b64decode('AAA')
    
    def test_base64_empty_string_bug(self):
        """Test that base64 handles empty string correctly"""
        
        # Empty string should decode to empty bytes
        result = base64.b64decode('')
        assert result == b'', "Empty string should decode to empty bytes"
    
    def test_base64_none_input_bug(self):
        """Test that base64 handles None input gracefully"""
        
        # None input should raise TypeError
        with pytest.raises(TypeError, match="argument should be a bytes-like object"):
            base64.b64decode(None)
    
    def test_num2words_infinity_bug(self):
        """Test that num2words handles infinity values correctly"""
        
        # Infinity should raise appropriate error
        with pytest.raises(OverflowError, match="cannot convert float infinity"):
            num2words(float('inf'))
        
        with pytest.raises(OverflowError, match="cannot convert float infinity"):
            num2words(float('-inf'))
    
    def test_num2words_very_large_numbers_bug(self):
        """Test that num2words handles very large numbers correctly"""
        
        # Very large numbers should work without crashing
        large_num = 10**15
        result = num2words(large_num)
        assert isinstance(result, str), "Should return string"
        assert len(result) > 0, "Should return non-empty string"
    
    def test_num2words_negative_numbers_bug(self):
        """Test that num2words handles negative numbers correctly"""
        
        # Negative numbers should work
        result = num2words(-42)
        assert result == "minus forty-two", "Should handle negative numbers"
    
    def test_num2words_zero_bug(self):
        """Test that num2words handles zero correctly"""
        
        # Zero should work
        result = num2words(0)
        assert result == "zero", "Should handle zero"
    
    def test_num2words_decimal_numbers_bug(self):
        """Test that num2words handles decimal numbers correctly"""
        
        # Decimal numbers should work
        result = num2words(0.5)
        assert result == "zero point five", "Should handle decimal numbers"
    
    def test_text2digits_special_characters_bug(self):
        """Test that text2digits handles special characters correctly"""
        t2d = Text2Digits()
        
        # Special characters should be handled gracefully
        result = t2d.convert('one hundred & twenty-three')
        assert '100' in result, "Should extract numbers from text with special characters"
    
    def test_text2digits_mixed_case_bug(self):
        """Test that text2digits handles mixed case correctly"""
        t2d = Text2Digits()
        
        # Mixed case should work
        result = t2d.convert('ONE Hundred Twenty-Three')
        assert result == '123', "Should handle mixed case correctly"
    
    def test_text2digits_invalid_text_bug(self):
        """Test that text2digits handles invalid text correctly"""
        t2d = Text2Digits()
        
        # Invalid text should return unchanged
        result = t2d.convert('not a number at all')
        assert result == 'not a number at all', "Should return unchanged text when no numbers found"
