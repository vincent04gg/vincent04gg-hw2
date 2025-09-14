import pytest
import base64
import json
from api.index import app, text_to_number, number_to_text, base64_to_number, number_to_base64

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestTextToNumber:
    """Test the text_to_number function"""
    
    def test_simple_numbers(self):
        """Test conversion of simple number words"""
        assert text_to_number("one") == 1
        assert text_to_number("two") == 2
        assert text_to_number("three") == 3
        assert text_to_number("four") == 4
        assert text_to_number("five") == 5
        assert text_to_number("six") == 6
        assert text_to_number("seven") == 7
        assert text_to_number("eight") == 8
        assert text_to_number("nine") == 9
        assert text_to_number("ten") == 10
    
    def test_zero_variants(self):
        """Test zero and nil"""
        assert text_to_number("zero") == 0
        assert text_to_number("nil") == 0
    
    def test_case_insensitive(self):
        """Test that function is case insensitive"""
        assert text_to_number("ONE") == 1
        assert text_to_number("Two") == 2
        assert text_to_number("ZERO") == 0
    
    def test_with_special_characters(self):
        """Test that special characters are stripped"""
        assert text_to_number("one!") == 1
        assert text_to_number("two@") == 2
        assert text_to_number("three123") == 3
    
    def test_invalid_text(self):
        """Test that invalid text raises ValueError"""
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("eleven")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("invalid")
        with pytest.raises(ValueError, match="Unable to convert text to number"):
            text_to_number("")

class TestNumberToText:
    """Test the number_to_text function"""
    
    def test_simple_numbers(self):
        """Test conversion of simple numbers"""
        assert number_to_text(1) == "one"
        assert number_to_text(2) == "two"
        assert number_to_text(10) == "ten"
        assert number_to_text(0) == "zero"
    
    def test_larger_numbers(self):
        """Test conversion of larger numbers"""
        assert number_to_text(42) == "forty-two"
        assert number_to_text(100) == "one hundred"
        assert number_to_text(123) == "one hundred and twenty-three"
    
    def test_negative_numbers(self):
        """Test conversion of negative numbers"""
        assert number_to_text(-1) == "minus one"
        assert number_to_text(-42) == "minus forty-two"

class TestBase64Conversion:
    """Test base64 conversion functions"""
    
    def test_number_to_base64_simple(self):
        """Test converting simple numbers to base64"""
        # Test with 1 (should be 1 byte)
        result = number_to_base64(1)
        decoded = base64.b64decode(result)
        assert int.from_bytes(decoded, byteorder='big') == 1
    
    def test_base64_to_number_simple(self):
        """Test converting simple base64 to numbers"""
        # Test with 1
        b64_str = base64.b64encode((1).to_bytes(1, byteorder='big')).decode('utf-8')
        assert base64_to_number(b64_str) == 1
    
    def test_base64_roundtrip(self):
        """Test roundtrip conversion"""
        test_numbers = [0, 1, 42, 255, 256, 1000, 65535]
        for num in test_numbers:
            b64 = number_to_base64(num)
            result = base64_to_number(b64)
            assert result == num
    
    def test_base64_little_endian_requirement(self):
        """Test that base64 uses little-endian as specified in requirements"""
        # According to the instructions, base64 should use little-endian byte order
        # This test will fail with the current implementation which uses big-endian
        test_number = 0x1234  # 4660 in decimal
        
        # Expected implementation (little-endian)
        expected_bytes = test_number.to_bytes(2, byteorder='little')
        expected_b64 = base64.b64encode(expected_bytes).decode('utf-8')
        
        # Current implementation should match little-endian
        current_result = number_to_base64(test_number)
        assert current_result == expected_b64, f"Expected little-endian base64 {expected_b64}, got {current_result}"
    
    def test_base64_zero_handling(self):
        """Test that zero is handled correctly in base64 conversion"""
        # Zero should produce a valid base64 string, not empty
        zero_b64 = number_to_base64(0)
        assert zero_b64 != "", "Zero should not produce empty base64 string"
        
        # Should be able to decode it back to zero
        decoded_zero = base64_to_number(zero_b64)
        assert decoded_zero == 0, f"Expected 0, got {decoded_zero}"

class TestWebAPI:
    """Test the web API endpoints"""
    
    def test_index_page(self, client):
        """Test that the index page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Numeric Converter' in response.data
    
    def test_convert_text_to_decimal(self, client):
        """Test converting text to decimal via API"""
        response = client.post('/convert', 
                             json={'input': 'one', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '1'
        assert data['error'] is None
    
    def test_convert_decimal_to_text(self, client):
        """Test converting decimal to text via API"""
        response = client.post('/convert', 
                             json={'input': '42', 'inputType': 'decimal', 'outputType': 'text'})
        data = json.loads(response.data)
        assert data['result'] == 'forty-two'
        assert data['error'] is None
    
    def test_convert_binary_to_decimal(self, client):
        """Test converting binary to decimal via API"""
        response = client.post('/convert', 
                             json={'input': '1010', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '10'
        assert data['error'] is None
    
    def test_convert_octal_to_decimal(self, client):
        """Test converting octal to decimal via API"""
        response = client.post('/convert', 
                             json={'input': '52', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_convert_hexadecimal_to_decimal(self, client):
        """Test converting hexadecimal to decimal via API"""
        response = client.post('/convert', 
                             json={'input': '2a', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] == '42'
        assert data['error'] is None
    
    def test_convert_decimal_to_binary(self, client):
        """Test converting decimal to binary via API"""
        response = client.post('/convert', 
                             json={'input': '10', 'inputType': 'decimal', 'outputType': 'binary'})
        data = json.loads(response.data)
        assert data['result'] == '1010'
        assert data['error'] is None
    
    def test_convert_decimal_to_octal(self, client):
        """Test converting decimal to octal via API"""
        response = client.post('/convert', 
                             json={'input': '42', 'inputType': 'decimal', 'outputType': 'octal'})
        data = json.loads(response.data)
        assert data['result'] == '52'
        assert data['error'] is None
    
    def test_convert_decimal_to_hexadecimal(self, client):
        """Test converting decimal to hexadecimal via API"""
        response = client.post('/convert', 
                             json={'input': '42', 'inputType': 'decimal', 'outputType': 'hexadecimal'})
        data = json.loads(response.data)
        assert data['result'] == '2a'
        assert data['error'] is None
    
    def test_convert_base64_roundtrip(self, client):
        """Test base64 conversion roundtrip via API"""
        # Convert decimal to base64
        response1 = client.post('/convert', 
                               json={'input': '42', 'inputType': 'decimal', 'outputType': 'base64'})
        data1 = json.loads(response1.data)
        assert data1['error'] is None
        
        # Convert base64 back to decimal
        response2 = client.post('/convert', 
                               json={'input': data1['result'], 'inputType': 'base64', 'outputType': 'decimal'})
        data2 = json.loads(response2.data)
        assert data2['result'] == '42'
        assert data2['error'] is None
    
    def test_invalid_input_type(self, client):
        """Test error handling for invalid input type"""
        response = client.post('/convert', 
                             json={'input': '42', 'inputType': 'invalid', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid input type' in data['error']
    
    def test_invalid_output_type(self, client):
        """Test error handling for invalid output type"""
        response = client.post('/convert', 
                             json={'input': '42', 'inputType': 'decimal', 'outputType': 'invalid'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid output type' in data['error']
    
    def test_invalid_text_input(self, client):
        """Test error handling for invalid text input"""
        response = client.post('/convert', 
                             json={'input': 'eleven', 'inputType': 'text', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Unable to convert text to number' in data['error']
    
    def test_invalid_binary_input(self, client):
        """Test error handling for invalid binary input"""
        response = client.post('/convert', 
                             json={'input': '102', 'inputType': 'binary', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int()' in data['error']
    
    def test_invalid_octal_input(self, client):
        """Test error handling for invalid octal input"""
        response = client.post('/convert', 
                             json={'input': '89', 'inputType': 'octal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int()' in data['error']
    
    def test_invalid_hexadecimal_input(self, client):
        """Test error handling for invalid hexadecimal input"""
        response = client.post('/convert', 
                             json={'input': 'gh', 'inputType': 'hexadecimal', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'invalid literal for int()' in data['error']
    
    def test_invalid_base64_input(self, client):
        """Test error handling for invalid base64 input"""
        response = client.post('/convert', 
                             json={'input': 'invalid_base64!', 'inputType': 'base64', 'outputType': 'decimal'})
        data = json.loads(response.data)
        assert data['result'] is None
        assert 'Invalid base64 input' in data['error']

class TestComprehensiveConversions:
    """Test all possible input/output type combinations"""
    
    def test_all_conversions_from_decimal(self, client):
        """Test converting decimal to all output types"""
        test_value = 42
        expected_results = {
            'text': 'forty-two',
            'binary': '101010',
            'octal': '52',
            'decimal': '42',
            'hexadecimal': '2a',
            'base64': None  # Will be tested separately
        }
        
        for output_type, expected in expected_results.items():
            if expected is not None:
                response = client.post('/convert', 
                                     json={'input': str(test_value), 'inputType': 'decimal', 'outputType': output_type})
                data = json.loads(response.data)
                assert data['error'] is None, f"Error converting decimal to {output_type}: {data['error']}"
                assert data['result'] == expected, f"Expected {expected} for decimal to {output_type}, got {data['result']}"
    
    def test_all_conversions_to_decimal(self, client):
        """Test converting all input types to decimal"""
        test_cases = [
            ('one', 'text', 1),
            ('1010', 'binary', 10),
            ('52', 'octal', 42),
            ('42', 'decimal', 42),
            ('2a', 'hexadecimal', 42),
        ]
        
        for input_value, input_type, expected in test_cases:
            response = client.post('/convert', 
                                 json={'input': input_value, 'inputType': input_type, 'outputType': 'decimal'})
            data = json.loads(response.data)
            assert data['error'] is None, f"Error converting {input_type} to decimal: {data['error']}"
            assert data['result'] == str(expected), f"Expected {expected} for {input_type} to decimal, got {data['result']}"
