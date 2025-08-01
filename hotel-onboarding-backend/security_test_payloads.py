"""
Security Test Payloads for Hotel Onboarding System
Comprehensive collection of attack vectors for security testing
"""

# XSS Attack Payloads
XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(1)",
    "<svg onload=alert(1)>",
    "<iframe src=javascript:alert('xss')>",
    "<body onload=alert('xss')>",
    "<input onfocus=alert('xss') autofocus>",
    "<select onfocus=alert('xss') autofocus>",
    "<textarea onfocus=alert('xss') autofocus>",
    "<keygen onfocus=alert('xss') autofocus>",
    "<video><source onerror=alert('xss')>",
    "<audio src=x onerror=alert('xss')>",
    "<marquee onstart=alert('xss')>",
    "<meter onmouseover=alert('xss')>alert</meter>",
    "'-alert(1)-'",
    "\"-alert(1)-\"",
    "';alert(1);//",
    "\";alert(1);//",
    "</script><script>alert(1)</script>",
    "'><script>alert(1)</script>"
]

# SQL Injection Payloads
SQL_INJECTION_PAYLOADS = [
    "'; DROP TABLE users; --",
    "' OR '1'='1",
    "' OR '1'='1' --",
    "' OR '1'='1' /*",
    "UNION SELECT * FROM users",
    "admin'--",
    "admin' #",
    "admin'/*",
    "' or 1=1#",
    "' or 1=1--",
    "' or 1=1/*",
    "') or '1'='1--",
    "') or ('1'='1--",
    "1' ORDER BY 1--+",
    "1' ORDER BY 2--+",
    "1' ORDER BY 3--+",
    "1' UNION SELECT null--",
    "1' UNION SELECT null,null--",
    "' AND 1=2 UNION SELECT 1,2,3--",
    "1' AND 1=2 UNION ALL SELECT 'admin',null,null--"
]

# Buffer Overflow Attempts
BUFFER_OVERFLOW_PAYLOADS = [
    "A" * 100,
    "A" * 1000,
    "A" * 10000,
    "A" * 100000,
    "A" * 1000000,
    "X" * 255,
    "X" * 256,
    "X" * 65535,
    "X" * 65536
]

# Special Characters
SPECIAL_CHARACTERS = [
    "< > & % $ # @ ! ' \" \\ / | { } [ ] ( ) = + - * _ ~ ` ^ ; : , . ?",
    "<<<>>>",
    "{{{{}}}}",
    "[[[[]]]]",
    "(((()))))",
    ";;;;;;;;",
    ":::::::::",
    ".........",
    "////////",
    "\\\\\\\\\\\\\\\\",
    "||||||||",
    "~~~~~~~~",
    "````````",
    "^^^^^^^^",
    "********",
    "++++++++",
    "--------",
    "========",
    "________",
    "@@@@@@@@",
    "########",
    "$$$$$$$$",
    "%%%%%%%%",
    "&&&&&&&&",
    "????????",
    "!!!!!!!!",
]

# Unicode and Emoji Payloads
UNICODE_PAYLOADS = [
    "😀🔥💀",
    "🚨🎯🔓",
    "\u202e\u202d\u202c",  # RTL override characters
    "\u200b\u200c\u200d",  # Zero-width characters
    "‏מימין לשמאל‏",  # Hebrew RTL text
    "العربية",  # Arabic text
    "中文字符",  # Chinese characters
    "日本語",  # Japanese characters
    "한국어",  # Korean characters
    "Ω≈ç√∫˜µ≤≥÷",  # Mathematical symbols
]

# Format Bypass Attempts
FORMAT_BYPASS = {
    "email": [
        "test@test",
        "@test.com",
        "test@",
        "test@@test.com",
        "test@test..com",
        "test.@test.com",
        ".test@test.com",
        "test@test.com.",
        "test @test.com",
        "test@ test.com",
        "test@test .com",
        "test@test\"><script>alert(1)</script>",
        "test+<script>alert(1)</script>@test.com",
        "test@test.com<script>alert(1)</script>",
        "\"'><script>alert(1)</script>\"@test.com",
        "test@[127.0.0.1]",
        "test@localhost",
        "test@-test.com",
        "test@test-.com",
    ],
    "phone": [
        "1234567890",
        "(123)456-7890",
        "123-456-7890",
        "123.456.7890",
        "123 456 7890",
        "+1 (123) 456-7890",
        "1-123-456-7890",
        "(123) 456-7890 x123",
        "123456789",  # Too short
        "12345678901",  # Too long
        "(abc) def-ghij",  # Letters
        "(123) 456-<script>",
        "';DROP TABLE--",
        "😀😀😀-😀😀😀-😀😀😀😀",
    ],
    "zip": [
        "1234",  # Too short
        "123456",  # Too long
        "abcde",  # Letters
        "12 34",  # Space
        "12-34",  # Dash
        "<script>",
        "' OR '1'='1",
        "12345<script>alert(1)</script>",
        "AAAAA",
        "00000",
        "99999",
        "-12345",
        "+12345",
    ],
    "ssn": [
        "123456789",  # No dashes
        "123-456789",  # Wrong format
        "12-34-5678",  # Wrong format
        "abc-de-fghi",  # Letters
        "123-45-678",  # Too short
        "123-45-67890",  # Too long
        "000-00-0000",  # Invalid
        "666-66-6666",  # Invalid
        "123-00-0000",  # Invalid middle
        "123-45-0000",  # Invalid last
        "<script>-45-6789",
        "';DROP--TABLE",
    ]
}

# Combined Attack Payloads for General Text Fields
COMBINED_ATTACKS = [
    # XSS + SQLi
    "' OR '1'='1' <script>alert(1)</script>",
    "\"><script>alert(1)</script>'; DROP TABLE users--",
    
    # XSS + Unicode
    "<script>alert('😀')</script>",
    "‏<script>alert(1)</script>‏",
    
    # SQLi + Special Chars
    "'; DROP TABLE users; -- <>&%$#@!",
    
    # All combined
    "<script>alert('xss')</script>'; DROP TABLE users; -- 😀🔥💀 ‏מימין לשמאל‏ \u200b",
]

# Field-specific edge cases
FIELD_EDGE_CASES = {
    "first_name": [
        "",  # Empty
        " ",  # Space only
        "A",  # Single char
        "A-B",  # Hyphen
        "O'Brien",  # Apostrophe
        "José",  # Accented
        "Mary Jane",  # Space
        "X Æ A-12",  # Elon's kid
    ],
    "last_name": [
        "",  # Empty
        " ",  # Space only
        "A",  # Single char
        "Smith-Jones",  # Hyphen
        "O'Connor",  # Apostrophe
        "López",  # Accented
        "Van Der Berg",  # Multiple parts
        "李",  # Chinese
    ],
    "date_of_birth": [
        "2030-01-01",  # Future
        "1800-01-01",  # Too old
        "2024-02-30",  # Invalid date
        "2024-13-01",  # Invalid month
        "2024-00-01",  # Invalid month
        "2024-01-32",  # Invalid day
        "2024-01-00",  # Invalid day
        "0000-01-01",  # Invalid year
        "9999-12-31",  # Max date
        "not-a-date",  # Invalid format
    ]
}

def get_all_payloads():
    """Get all payloads in a structured format"""
    return {
        "xss": XSS_PAYLOADS,
        "sql_injection": SQL_INJECTION_PAYLOADS,
        "buffer_overflow": BUFFER_OVERFLOW_PAYLOADS,
        "special_chars": SPECIAL_CHARACTERS,
        "unicode": UNICODE_PAYLOADS,
        "format_bypass": FORMAT_BYPASS,
        "combined": COMBINED_ATTACKS,
        "edge_cases": FIELD_EDGE_CASES
    }

def get_payloads_for_field(field_name, field_type="text"):
    """Get relevant payloads for a specific field type"""
    payloads = []
    
    # Add general attacks for all fields
    payloads.extend(XSS_PAYLOADS)
    payloads.extend(SQL_INJECTION_PAYLOADS)
    payloads.extend(SPECIAL_CHARACTERS)
    payloads.extend(UNICODE_PAYLOADS)
    
    # Add field-specific payloads
    if field_name in FORMAT_BYPASS:
        payloads.extend(FORMAT_BYPASS[field_name])
    
    if field_name in FIELD_EDGE_CASES:
        payloads.extend(FIELD_EDGE_CASES[field_name])
    
    # Add buffer overflow for text fields
    if field_type == "text":
        payloads.extend(BUFFER_OVERFLOW_PAYLOADS)
    
    return payloads

if __name__ == "__main__":
    # Print payload statistics
    all_payloads = get_all_payloads()
    print("Security Test Payload Statistics:")
    print("-" * 40)
    for category, payloads in all_payloads.items():
        if isinstance(payloads, dict):
            total = sum(len(v) for v in payloads.values())
            print(f"{category}: {total} payloads")
        else:
            print(f"{category}: {len(payloads)} payloads")
    
    # Total count
    total_count = sum(
        len(p) if isinstance(p, list) else sum(len(v) for v in p.values())
        for p in all_payloads.values()
    )
    print("-" * 40)
    print(f"Total payloads: {total_count}")