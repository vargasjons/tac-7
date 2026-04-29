import json
import pytest
import sqlite3
import pandas as pd
from io import StringIO
from core.export_utils import generate_csv_from_data, generate_csv_from_table, generate_json_from_data, generate_json_from_table


class TestExportUtils:
    
    def test_generate_csv_from_data_empty(self):
        """Test CSV generation with empty data"""
        result = generate_csv_from_data([], [])
        assert result == b""
        
    def test_generate_csv_from_data_with_columns_no_data(self):
        """Test CSV generation with columns but no data"""
        columns = ['id', 'name', 'value']
        result = generate_csv_from_data([], columns)
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert list(df.columns) == columns
        assert len(df) == 0
        
    def test_generate_csv_from_data_with_data(self):
        """Test CSV generation with actual data"""
        data = [
            {'id': 1, 'name': 'Test 1', 'value': 100},
            {'id': 2, 'name': 'Test 2', 'value': 200}
        ]
        columns = ['id', 'name', 'value']
        
        result = generate_csv_from_data(data, columns)
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert list(df.columns) == columns
        assert len(df) == 2
        assert df.iloc[0]['name'] == 'Test 1'
        assert df.iloc[1]['value'] == 200
        
    def test_generate_csv_from_data_auto_columns(self):
        """Test CSV generation with automatic column detection"""
        data = [
            {'id': 1, 'name': 'Test 1'},
            {'id': 2, 'name': 'Test 2'}
        ]
        
        result = generate_csv_from_data(data, [])
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert 'id' in df.columns
        assert 'name' in df.columns
        assert len(df) == 2
        
    def test_generate_csv_from_data_various_types(self):
        """Test CSV generation with various data types"""
        data = [
            {'int': 1, 'float': 1.5, 'string': 'test', 'bool': True, 'none': None},
            {'int': 2, 'float': 2.5, 'string': 'test2', 'bool': False, 'none': None}
        ]
        columns = ['int', 'float', 'string', 'bool', 'none']
        
        result = generate_csv_from_data(data, columns)
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert df.iloc[0]['int'] == 1
        assert df.iloc[0]['float'] == 1.5
        assert df.iloc[0]['string'] == 'test'
        assert df.iloc[0]['bool']
        assert pd.isna(df.iloc[0]['none'])
        
    def test_generate_csv_from_data_special_characters(self):
        """Test CSV generation with special characters"""
        data = [
            {'name': 'Test, with comma', 'desc': 'Quote "test"'},
            {'name': 'New\nline', 'desc': 'Tab\there'}
        ]
        columns = ['name', 'desc']
        
        result = generate_csv_from_data(data, columns)
        
        # Parse the CSV to verify proper escaping
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert df.iloc[0]['name'] == 'Test, with comma'
        assert df.iloc[0]['desc'] == 'Quote "test"'
        assert df.iloc[1]['name'] == 'New\nline'
        
    def test_generate_csv_from_data_unicode(self):
        """Test CSV generation with Unicode characters"""
        data = [
            {'name': 'Test 测试', 'emoji': '😀🎉'},
            {'name': 'Café', 'emoji': '☕'}
        ]
        columns = ['name', 'emoji']
        
        result = generate_csv_from_data(data, columns)
        
        # Parse the CSV to verify Unicode handling
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert df.iloc[0]['name'] == 'Test 测试'
        assert df.iloc[0]['emoji'] == '😀🎉'
        assert df.iloc[1]['name'] == 'Café'
        
    def test_generate_csv_from_table_nonexistent(self):
        """Test CSV generation from non-existent table"""
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        
        with pytest.raises(ValueError, match="Table 'nonexistent' does not exist"):
            generate_csv_from_table(conn, 'nonexistent')
            
        conn.close()
        
    def test_generate_csv_from_table_empty(self):
        """Test CSV generation from empty table"""
        # Create in-memory database with empty table
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL
            )
        ''')
        conn.commit()
        
        result = generate_csv_from_table(conn, 'test_table')
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert 'id' in df.columns
        assert 'name' in df.columns
        assert 'value' in df.columns
        assert len(df) == 0
        
        conn.close()
        
    def test_generate_csv_from_table_with_data(self):
        """Test CSV generation from table with data"""
        # Create in-memory database with data
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value REAL,
                created_date TEXT
            )
        ''')
        
        cursor.executemany('''
            INSERT INTO test_table (name, value, created_date) 
            VALUES (?, ?, ?)
        ''', [
            ('Item 1', 100.5, '2024-01-01'),
            ('Item 2', 200.75, '2024-01-02'),
            ('Item 3', None, '2024-01-03')
        ])
        conn.commit()
        
        result = generate_csv_from_table(conn, 'test_table')
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert len(df) == 3
        assert df.iloc[0]['name'] == 'Item 1'
        assert df.iloc[1]['value'] == 200.75
        assert pd.isna(df.iloc[2]['value'])
        assert df.iloc[2]['created_date'] == '2024-01-03'
        
        conn.close()
        
    def test_generate_csv_from_table_special_name(self):
        """Test CSV generation from table with special characters in name"""
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE "special-table-name" (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        
        cursor.execute('INSERT INTO "special-table-name" (data) VALUES (?)', ('test data',))
        conn.commit()
        
        result = generate_csv_from_table(conn, 'special-table-name')
        
        # Parse the CSV to verify
        csv_str = result.decode('utf-8')
        df = pd.read_csv(StringIO(csv_str))
        
        assert len(df) == 1
        assert df.iloc[0]['data'] == 'test data'

        conn.close()


class TestJsonExportUtils:

    def test_generate_json_from_data_empty(self):
        """Empty data returns a JSON array []"""
        result = generate_json_from_data([], [])
        parsed = json.loads(result.decode('utf-8'))
        assert parsed == []

    def test_generate_json_from_data_basic(self):
        """Column names appear as keys and values are correct"""
        data = [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ]
        columns = ['id', 'name']
        result = generate_json_from_data(data, columns)
        parsed = json.loads(result.decode('utf-8'))
        assert len(parsed) == 2
        assert parsed[0] == {'id': 1, 'name': 'Alice'}
        assert parsed[1] == {'id': 2, 'name': 'Bob'}

    def test_generate_json_from_data_types(self):
        """int, float, string, bool, None round-trip correctly"""
        data = [{'i': 42, 'f': 3.14, 's': 'hello', 'b': True, 'n': None}]
        columns = ['i', 'f', 's', 'b', 'n']
        result = generate_json_from_data(data, columns)
        parsed = json.loads(result.decode('utf-8'))
        row = parsed[0]
        assert row['i'] == 42
        assert abs(row['f'] - 3.14) < 1e-9
        assert row['s'] == 'hello'
        assert row['b'] is True
        assert row['n'] is None

    def test_generate_json_from_data_unicode(self):
        """Emoji, Chinese characters, accented letters survive round-trip"""
        data = [{'name': 'Test 测试', 'emoji': '😀🎉'}, {'name': 'Café', 'emoji': '☕'}]
        columns = ['name', 'emoji']
        result = generate_json_from_data(data, columns)
        parsed = json.loads(result.decode('utf-8'))
        assert parsed[0]['name'] == 'Test 测试'
        assert parsed[0]['emoji'] == '😀🎉'
        assert parsed[1]['name'] == 'Café'

    def test_generate_json_from_data_special_chars(self):
        """Strings containing quotes, newlines, tabs are properly escaped"""
        data = [{'val': 'say "hi"'}, {'val': 'line1\nline2'}, {'val': 'col1\tcol2'}]
        columns = ['val']
        result = generate_json_from_data(data, columns)
        parsed = json.loads(result.decode('utf-8'))
        assert parsed[0]['val'] == 'say "hi"'
        assert parsed[1]['val'] == 'line1\nline2'
        assert parsed[2]['val'] == 'col1\tcol2'

    def test_generate_json_from_table_basic(self):
        """Reads a SQLite table and returns correct JSON"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT)')
        cursor.executemany('INSERT INTO t (name) VALUES (?)', [('Alice',), ('Bob',)])
        conn.commit()

        result = generate_json_from_table(conn, 't')
        parsed = json.loads(result.decode('utf-8'))
        assert len(parsed) == 2
        names = {row['name'] for row in parsed}
        assert names == {'Alice', 'Bob'}
        conn.close()

    def test_generate_json_from_table_empty(self):
        """Empty table returns JSON []"""
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE empty_t (id INTEGER PRIMARY KEY, val TEXT)')
        conn.commit()

        result = generate_json_from_table(conn, 'empty_t')
        parsed = json.loads(result.decode('utf-8'))
        assert parsed == []
        conn.close()

    def test_generate_json_from_table_nonexistent(self):
        """Non-existent table raises ValueError"""
        conn = sqlite3.connect(':memory:')
        with pytest.raises(ValueError, match="Table 'nope' does not exist"):
            generate_json_from_table(conn, 'nope')
        conn.close()