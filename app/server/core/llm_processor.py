import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from anthropic import Anthropic
from core.data_models import QueryRequest

def generate_sql_with_openai(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables
- NEVER include SQL comments (-- or /* */) in the query

SQL Query:"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a SQL expert. Convert natural language to SQL queries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        sql = response.choices[0].message.content.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with OpenAI: {str(e)}")

def generate_sql_with_anthropic(query_text: str, schema_info: Dict[str, Any]) -> str:
    """
    Generate SQL query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Convert this natural language query to SQL: "{query_text}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Handle date/time queries appropriately (e.g., "last week" = date('now', '-7 days'))
- Be careful with column names and table names
- If the query is ambiguous, make reasonable assumptions
- For multi-table queries, use proper JOIN conditions to avoid Cartesian products
- Limit results to reasonable amounts (e.g., add LIMIT 100 for large result sets)
- When joining tables, use meaningful relationships between tables
- NEVER include SQL comments (-- or /* */) in the query

SQL Query:"""
        
        # Call Anthropic API
        response = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        sql = response.content[0].text.strip()
        
        # Clean up the SQL (remove markdown if present)
        if sql.startswith("```sql"):
            sql = sql[6:]
        if sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        return sql.strip()
        
    except Exception as e:
        raise Exception(f"Error generating SQL with Anthropic: {str(e)}")

def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """
    Format database schema for LLM prompt
    """
    lines = []
    
    for table_name, table_info in schema_info.get('tables', {}).items():
        lines.append(f"Table: {table_name}")
        lines.append("Columns:")
        
        for col_name, col_type in table_info['columns'].items():
            lines.append(f"  - {col_name} ({col_type})")
        
        lines.append(f"Row count: {table_info['row_count']}")
        lines.append("")
    
    return "\n".join(lines)

def generate_random_query_with_openai(schema_info: Dict[str, Any]) -> str:
    """
    Generate a random natural language query using OpenAI API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        client = OpenAI(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Generate an interesting natural language query that someone might ask about this data. 
The query should be:
- Contextually relevant to the table structures and columns
- Natural and conversational
- Maximum two sentences
- Something that would demonstrate the capability of natural language to SQL conversion
- Varied in complexity (sometimes simple, sometimes complex with JOINs or aggregations)
- Do NOT include any SQL syntax, comments, or special characters

Examples of good queries:
- "What are the top 5 products by revenue?"
- "Show me all customers who ordered in the last month."
- "Which employees have the highest average sales? List their names and departments."

Natural language query:"""
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates interesting questions about data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        query = response.choices[0].message.content.strip()
        return query
        
    except Exception as e:
        raise Exception(f"Error generating random query with OpenAI: {str(e)}")

def generate_random_query_with_anthropic(schema_info: Dict[str, Any]) -> str:
    """
    Generate a random natural language query using Anthropic API
    """
    try:
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        client = Anthropic(api_key=api_key)
        
        # Format schema for prompt
        schema_description = format_schema_for_prompt(schema_info)
        
        # Create prompt
        prompt = f"""Given the following database schema:

{schema_description}

Generate an interesting natural language query that someone might ask about this data. 
The query should be:
- Contextually relevant to the table structures and columns
- Natural and conversational
- Maximum two sentences
- Something that would demonstrate the capability of natural language to SQL conversion
- Varied in complexity (sometimes simple, sometimes complex with JOINs or aggregations)
- Do NOT include any SQL syntax, comments, or special characters

Examples of good queries:
- "What are the top 5 products by revenue?"
- "Show me all customers who ordered in the last month."
- "Which employees have the highest average sales? List their names and departments."

Natural language query:"""
        
        # Call Anthropic API
        response = client.messages.create(
            model="claude-sonnet-4-0",
            max_tokens=100,
            temperature=0.8,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        query = response.content[0].text.strip()
        return query
        
    except Exception as e:
        raise Exception(f"Error generating random query with Anthropic: {str(e)}")

def generate_random_query(schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider for random query generation
    Priority: 1) OpenAI API key exists, 2) Anthropic API key exists
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Check API key availability (OpenAI priority)
    if openai_key:
        return generate_random_query_with_openai(schema_info)
    elif anthropic_key:
        return generate_random_query_with_anthropic(schema_info)
    else:
        raise ValueError("No LLM API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY")

def _build_synthetic_data_prompt(table_name: str, schema_info: Dict[str, Any], sample_rows: List[Dict[str, Any]], row_count: int) -> str:
    table_schema = schema_info.get('tables', {}).get(table_name, {})
    columns_desc = []
    for col_name, col_type in table_schema.get('columns', {}).items():
        columns_desc.append(f"  - {col_name} ({col_type})")
    schema_text = "\n".join(columns_desc) if columns_desc else "  (no columns found)"

    if sample_rows:
        sample_text = json.dumps(sample_rows, indent=2, default=str)
        data_section = f"Sample rows from the table (use these to understand data patterns):\n{sample_text}"
    else:
        data_section = "The table currently has no rows. Generate realistic data based purely on the column names and types."

    return f"""You are a synthetic data generator. Generate exactly {row_count} new realistic data rows for the table "{table_name}".

Table schema:
{schema_text}

{data_section}

Requirements:
- Return ONLY a valid JSON array of {row_count} objects, no markdown, no explanations, no code fences
- Each object must use the exact column names from the schema
- Match the data formats from the samples (emails, phone numbers, dates, IDs, etc.)
- Respect value ranges and distributions observed in the samples
- Keep relationships between columns coherent (e.g., city matches country)
- Generate varied, realistic values — not copies of the sample rows
- For nullable columns, occasionally use null values
- Do NOT include auto-increment or index columns

JSON array:"""


def _parse_json_response(raw: str) -> List[Dict[str, Any]]:
    text = raw.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def generate_synthetic_data_with_openai(
    table_name: str,
    schema_info: Dict[str, Any],
    sample_rows: List[Dict[str, Any]],
    row_count: int
) -> List[Dict[str, Any]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)
    prompt = _build_synthetic_data_prompt(table_name, schema_info, sample_rows, row_count)

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "system", "content": "You are a synthetic data generator. Return only valid JSON arrays."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    return _parse_json_response(raw)


def generate_synthetic_data_with_anthropic(
    table_name: str,
    schema_info: Dict[str, Any],
    sample_rows: List[Dict[str, Any]],
    row_count: int
) -> List[Dict[str, Any]]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = Anthropic(api_key=api_key)
    prompt = _build_synthetic_data_prompt(table_name, schema_info, sample_rows, row_count)

    response = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=2000,
        temperature=0.8,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.content[0].text.strip()
    return _parse_json_response(raw)


def generate_synthetic_data(
    table_name: str,
    schema_info: Dict[str, Any],
    sample_rows: List[Dict[str, Any]],
    row_count: int
) -> List[Dict[str, Any]]:
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if openai_key:
        return generate_synthetic_data_with_openai(table_name, schema_info, sample_rows, row_count)
    elif anthropic_key:
        return generate_synthetic_data_with_anthropic(table_name, schema_info, sample_rows, row_count)
    else:
        raise ValueError("No LLM API key found. Please set either OPENAI_API_KEY or ANTHROPIC_API_KEY")


def generate_sql(request: QueryRequest, schema_info: Dict[str, Any]) -> str:
    """
    Route to appropriate LLM provider based on API key availability and request preference.
    Priority: 1) OpenAI API key exists, 2) Anthropic API key exists, 3) request.llm_provider
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Check API key availability first (OpenAI priority)
    if openai_key:
        return generate_sql_with_openai(request.query, schema_info)
    elif anthropic_key:
        return generate_sql_with_anthropic(request.query, schema_info)
    
    # Fall back to request preference if both keys available or neither available
    if request.llm_provider == "openai":
        return generate_sql_with_openai(request.query, schema_info)
    else:
        return generate_sql_with_anthropic(request.query, schema_info)