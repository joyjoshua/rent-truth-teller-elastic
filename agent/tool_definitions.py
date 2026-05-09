"""Bedrock tool-use schema definitions for the Rental Truth-Teller agent."""

TOOLS = [
    {
        "toolSpec": {
            "name": "search_listings",
            "description": (
                "Search rental listings in Bengaluru by meaning. Use when the user "
                "describes what they're looking for in natural language — e.g. "
                "'affordable flat near tech parks' or 'spacious family apartment in "
                "a quiet area' or when they ask about specific listings. Returns "
                "listing details including rent, deposit, locality, furnishing, "
                "and area. Do NOT use for price benchmarking or deposit checks."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query describing what the user wants",
                        }
                    },
                    "required": ["query"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "get_price_benchmark",
            "description": (
                "Returns rent statistics (median, 25th percentile, 75th percentile, "
                "average deposit in months, and listing count) for a given locality "
                "and BHK type. Use when the user asks if a quoted rent is fair, wants "
                "to know the going rate in an area, or asks 'is X amount reasonable "
                "for a Y BHK in Z locality?' Do NOT use for deposit-specific questions."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "locality": {
                            "type": "string",
                            "description": "Micro-market / neighbourhood name (e.g. 'Koramangala', 'HSR Layout')",
                        },
                        "bhk": {
                            "type": "integer",
                            "description": "Number of bedrooms (1, 2, or 3)",
                        },
                    },
                    "required": ["locality", "bhk"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "check_deposit_norm",
            "description": (
                "Returns deposit statistics for a locality and BHK type — median "
                "deposit in months, average, maximum, and total listing count. Use "
                "when the user asks if a quoted deposit amount is reasonable, when a "
                "broker's deposit demand seems high, or when someone mentions a "
                "deposit of more than 3 months."
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "locality": {
                            "type": "string",
                            "description": "Micro-market / neighbourhood name",
                        },
                        "bhk": {
                            "type": "integer",
                            "description": "Number of bedrooms (1, 2, or 3)",
                        },
                    },
                    "required": ["locality", "bhk"],
                }
            },
        }
    },
    {
        "toolSpec": {
            "name": "compare_neighbourhoods",
            "description": (
                "Compares two Bengaluru neighbourhoods side by side on median rent, "
                "median deposit in months, average apartment size, and listing count. "
                "Use when the user is choosing between two areas or asks 'should I "
                "live in X or Y?' or 'X vs Y for renting.'"
            ),
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "area_a": {
                            "type": "string",
                            "description": "First neighbourhood to compare",
                        },
                        "area_b": {
                            "type": "string",
                            "description": "Second neighbourhood to compare",
                        },
                    },
                    "required": ["area_a", "area_b"],
                }
            },
        }
    },
]
