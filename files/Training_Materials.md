# GitHub Copilot · MCP · Databricks Genie — 3-Day Training Materials

> **Total Duration:** 5 hours  |  **Format:** Instructor-led with live demos

---

## Prerequisites

Before attending the training, ensure the following are in place.

### Required Accounts & Licenses

| Service | Requirement |
|---|---|
| GitHub | Account + active **Copilot Individual/Business** subscription |
| Azure | Active subscription with contributor access |
| Snowflake | Account (free trial sufficient for demos) |
| Databricks | Workspace with **Genie Code** feature enabled |

### Local Tools

```bash
# 1. VS Code (1.88+) with extensions
code --install-extension GitHub.copilot
code --install-extension GitHub.copilot-chat   # v1.200+ for Agent/MCP support

# 2. Node.js 18+
node --version  # should be >= 18.0.0
npm install -g @modelcontextprotocol/sdk

# 3. Python 3.10+
pip install databricks-sdk pyspark pandas --break-system-packages

# 4. Azure CLI + Databricks CLI
az login
databricks configure --host https://<your-workspace>.azuredatabricks.net
```

### Demo Project Quick Start

```bash
git clone https://github.com/your-org/copilot-mcp-demo
cd copilot-mcp-demo

# Install dependencies
npm install
pip install -r requirements.txt

# Set environment variables
export AZURE_CONNECTION_STRING="<your-adf-connection>"
export SNOWFLAKE_ACCOUNT="<your-account>"
export SNOWFLAKE_USER="<user>"
export SNOWFLAKE_PASSWORD="<password>"
export DATABRICKS_HOST="https://<workspace>.azuredatabricks.net"
export DATABRICKS_TOKEN="<your-pat>"
export GITHUB_TOKEN="<your-token>"

# Start the MCP server
node mcp-server/index.js   # Listens on localhost:3100

# Open in VS Code — Copilot connects automatically
code .
```

---

## Day 1 – GitHub Copilot Fundamentals → Agents (2 hrs)

**Objective:** Build a strong foundation and evolve from basic Copilot usage to Agent-based workflows.

---

### Session 1: Copilot Basics

#### What is GitHub Copilot?

GitHub Copilot is an AI pair programmer powered by OpenAI Codex. It integrates directly into VS Code and suggests code completions, whole functions, tests, and documentation based on context from your current file and open tabs.

#### Core Capabilities

**1. Code Generation**

Write a descriptive comment and let Copilot complete the function:

```python
# Python
# Function: validate an email address format
# Input : email string
# Output: True if valid, False otherwise
# Use a regex and check for domain with at least one dot

import re

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Test
print(validate_email("user@example.com"))   # True
print(validate_email("bad-email"))          # False
```

**2. Refactoring**

Select messy code, open Copilot Chat, and type:
`Refactor this function to remove nested loops and use list comprehensions`

Before:
```python
def get_active_users(users):
    result = []
    for u in users:
        if u['active']:
            result.append(u['name'])
    return result
```

After (Copilot-generated):
```python
def get_active_users(users: list[dict]) -> list[str]:
    return [u['name'] for u in users if u['active']]
```

**3. Unit Test Generation**

Highlight a function → Copilot Chat → `/tests`

```python
# Copilot auto-generates for the validate_email function above:
import pytest
from mymodule import validate_email

@pytest.mark.parametrize("email,expected", [
    ("user@example.com",   True),
    ("name+tag@sub.io",    True),
    ("bad-email",          False),
    ("@nodomain.com",      False),
    ("user@.com",          False),
    ("",                   False),
])
def test_validate_email(email, expected):
    assert validate_email(email) == expected
```

**4. Documentation**

Prompt: `Add a Google-style docstring to this function`

```python
def parse_sales_csv(file_path: str) -> dict:
    """Parse a sales CSV file and return monthly revenue totals.

    Args:
        file_path: Path to the CSV file with columns: date, product, amount.

    Returns:
        A dict mapping month strings (YYYY-MM) to total float revenue.

    Raises:
        FileNotFoundError: If the CSV file doesn't exist.
        KeyError: If required columns are missing.
    """
    ...
```

#### Prompt Engineering Tips

| Tip | Example |
|---|---|
| Be specific about language | `# Python 3.11, using dataclasses` |
| State input/output types | `# Input: list of dicts. Output: pandas DataFrame` |
| Mention constraints | `# No external libraries, stdlib only` |
| Provide examples | `# Example: parse("2024-01") → {"month": 1}` |

---

### Session 2: Advanced Copilot Usage

**Multi-file Understanding**

Open the relevant files in separate editor tabs — Copilot reads all open tabs as context.

```typescript
// models/User.ts (open tab #1)
export interface User {
  id: string;
  email: string;
  role: "admin" | "viewer";
}

// services/UserService.ts (open tab #2) — Copilot knows User interface
// Prompt: "method to find admin users by email domain"
import { User } from "../models/User";

export class UserService {
  constructor(private readonly users: User[]) {}

  findAdminsByDomain(domain: string): User[] {
    return this.users.filter(
      u => u.role === "admin" && u.email.endsWith(`@${domain}`)
    );
  }
}
```

**Debugging with Copilot Chat**

Select the buggy code → Chat: `Why does this fail and how do I fix it?`

```python
# Bug: off-by-one in pagination
def paginate(items, page, page_size):
    start = page * page_size       # Bug: page 1 should start at index 0
    end   = start + page_size
    return items[start:end]

# Copilot fix — 0-indexed pages are correct; if 1-indexed:
def paginate(items, page: int, page_size: int) -> list:
    """Return items for the given 1-indexed page."""
    start = (page - 1) * page_size
    return items[start : start + page_size]
```

---

### Session 3: Introduction to Copilot Agents

#### Prompt-Based vs Agent-Based

| Dimension | Prompt-Based | Agent-Based |
|---|---|---|
| Execution | Single response | Multi-step autonomous loop |
| Context | Current file | Entire repo + external tools |
| Planning | None | Breaks goal into sub-tasks |
| Tools | None | File I/O, terminal, browser, APIs |
| Best for | Autocomplete, small edits | Feature build, large refactors |

#### Enabling Agent Mode in VS Code

Open Copilot Chat panel → change mode dropdown from **Ask** to **Agent**.

#### Agent Demo: Build a REST Endpoint

**Prompt to Agent:**
```
Create a FastAPI endpoint POST /api/users that:
1. Accepts JSON body {name, email, role}
2. Validates email format
3. Saves to SQLite via SQLAlchemy
4. Returns 201 with the created user or 422 on validation error
Include unit tests using pytest and httpx.
```

The agent will:
1. Create `models.py` with SQLAlchemy model
2. Create `routes/users.py` with the endpoint
3. Create `database.py` with engine setup
4. Write `tests/test_users.py`
5. Run `pytest` and fix any failures

---

## Day 2 – MCP + Azure Data Stack + Agents (2 hrs)

**Objective:** Enable context-aware Copilot using MCP with Azure, Databricks, and Snowflake.

---

### Session 1: MCP Fundamentals

#### What is Model Context Protocol?

MCP is an open standard (2024) that lets AI assistants securely communicate with external data sources and tools. Instead of guessing your schema, Copilot queries your actual environment.

**Architecture:**
```
Developer (VS Code)
    │
    ▼
GitHub Copilot  ──────  MCP Client (built into Copilot Chat)
                              │
                              ▼
                         MCP Server  (your Node.js process)
                         /    |    \
                        /     |     \
                       ADF  Databricks  Snowflake
```

#### VS Code Configuration (`settings.json`)

```json
{
  "github.copilot.advanced": {
    "mcp": {
      "servers": [
        {
          "name": "azure-data-platform",
          "command": "node",
          "args": ["./mcp-server/index.js"],
          "env": {
            "AZURE_CONNECTION_STRING": "${env:AZURE_CONNECTION_STRING}",
            "SNOWFLAKE_ACCOUNT":       "${env:SNOWFLAKE_ACCOUNT}",
            "DATABRICKS_HOST":         "${env:DATABRICKS_HOST}",
            "DATABRICKS_TOKEN":        "${env:DATABRICKS_TOKEN}"
          }
        }
      ]
    }
  }
}
```

#### MCP Server Skeleton

```javascript
// mcp-server/index.js
const { MCPServer, Resource } = require("@modelcontextprotocol/sdk");
const { DataFactoryManagementClient } = require("@azure/arm-datafactory");
const { DefaultAzureCredential } = require("@azure/identity");

const server = new MCPServer({ name: "azure-data-platform", version: "1.0.0" });

// ── Resource: ADF Pipeline list ──────────────────────────────────────────
server.addResource("adf_pipelines", async (ctx) => {
  const credential = new DefaultAzureCredential();
  const client = new DataFactoryManagementClient(credential, process.env.AZURE_SUBSCRIPTION_ID);
  const pipelines = [];
  for await (const p of client.pipelines.listByFactory(
    process.env.ADF_RESOURCE_GROUP,
    process.env.ADF_FACTORY_NAME
  )) {
    pipelines.push({ name: p.name, activities: p.activities?.length ?? 0 });
  }
  return { pipelines };
});

// ── Resource: Databricks table schemas ───────────────────────────────────
server.addResource("databricks_schemas", async (ctx) => {
  const { WorkspaceClient } = require("@databricks/sdk");
  const w = new WorkspaceClient();
  const schemas = await w.schemas.list({ catalog_name: "prod" });
  return { schemas: schemas.map(s => s.full_name) };
});

server.start();
console.log("MCP server running on stdio");
```

---

### Session 2: MCP with Azure Data Engineering

#### Azure Data Factory — Pipeline Generation

**Copilot Prompt (with MCP context active):**
```
Generate an ADF pipeline JSON that:
- Sources: Azure Blob Storage (CSV files, daily partition by date)
- Transforms: Remove nulls in 'amount', cast 'date' to DateTime
- Sink: Azure SQL Database table 'dbo.sales_cleaned'
- Add retry policy (3 attempts, 30s interval)
```

**Copilot-generated ADF pipeline snippet:**
```json
{
  "name": "pl_sales_blob_to_sql",
  "properties": {
    "activities": [
      {
        "name": "Copy_Sales_Data",
        "type": "Copy",
        "typeProperties": {
          "source": {
            "type": "DelimitedTextSource",
            "storeSettings": { "type": "AzureBlobStorageReadSettings", "recursive": false }
          },
          "sink": {
            "type": "AzureSqlSink",
            "writeBehavior": "insert",
            "preCopyScript": "DELETE FROM dbo.sales_cleaned WHERE load_date = '@{formatDateTime(pipeline().parameters.runDate, 'yyyy-MM-dd')}'"
          }
        },
        "policy": { "retry": 3, "retryIntervalInSeconds": 30 }
      }
    ],
    "parameters": { "runDate": { "type": "String" } }
  }
}
```

#### Databricks — Context-Aware PySpark

```python
# Copilot knows your Delta table schema via MCP
# Prompt: "Join daily_sales with customer_dim, compute monthly revenue by region, write Delta"

from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("monthly_revenue").getOrCreate()

df_sales = spark.table("prod.gold.daily_sales")     # MCP surfaced schema
df_cust  = spark.table("prod.gold.customer_dim")

result = (
  df_sales
  .join(df_cust, "customer_id", "left")
  .withColumn("month", F.date_trunc("month", "sale_date"))
  .groupBy("region", "month")
  .agg(
    F.sum("amount").alias("total_revenue"),
    F.countDistinct("customer_id").alias("unique_customers"),
    F.avg("amount").alias("avg_order_value")
  )
  .orderBy("month", "region")
)

(result.write
  .format("delta")
  .mode("overwrite")
  .partitionBy("month")
  .option("mergeSchema", "true")
  .saveAsTable("prod.gold.monthly_revenue_by_region"))

print(f"Written {result.count()} rows")
```

#### Snowflake — Schema-Aware SQL

```sql
-- Copilot prompt: "Top 10 customers by LTV in last 90 days, exclude test accounts"
-- MCP provides: ORDERS schema, CUSTOMERS schema, test email patterns

SELECT
  c.customer_id,
  c.name,
  c.email,
  SUM(o.amount)          AS ltv_90d,
  COUNT(o.order_id)      AS order_count,
  AVG(o.amount)          AS avg_order_value,
  MAX(o.order_date)      AS last_order_date
FROM PROD.PUBLIC.ORDERS o
JOIN PROD.PUBLIC.CUSTOMERS c ON o.customer_id = c.customer_id
WHERE o.order_date >= DATEADD(day, -90, CURRENT_DATE)
  AND o.status = 'completed'
  AND c.email NOT LIKE '%@test.%'
  AND c.email NOT LIKE '%@example.%'
GROUP BY 1, 2, 3
ORDER BY ltv_90d DESC
LIMIT 10;
```

---

### Session 3: MCP + Agents (Advanced)

#### Enterprise Automation Pattern

**Prompt to Copilot Agent (with MCP active):**
```
Audit our ADF pipelines for:
1. Missing retry policies
2. Pipelines that haven't run in 30+ days
3. Missing monitoring alerts
Generate a report and create GitHub issues for each finding.
```

The Agent + MCP combination:
1. Calls MCP → fetches all ADF pipeline configs
2. Calls MCP → fetches run history from Azure Monitor
3. Analyzes each pipeline against the checklist
4. Generates a markdown report
5. Uses the GitHub tool to create labelled issues

---

## Day 3 – Databricks Genie Code Enablement (1 hr)

**Objective:** Equip teams to position and leverage Databricks Genie Code for AI-driven data engineering.

---

### Session 1: Foundations of Genie Code

#### What is Genie Code?

Genie Code is Databricks' AI coding assistant embedded in the Databricks IDE, notebooks, and CLI. It understands your Unity Catalog schemas, Delta tables, and cluster configurations natively.

#### AI/BI Genie Space vs. Genie Code

| Dimension | AI/BI Genie Space | Genie Code |
|---|---|---|
| Audience | Analysts, Executives | Engineers, ML, Architects |
| Interface | Chat / NL Q&A | IDE, Notebook, CLI |
| Output | Charts, dashboards | PySpark, SQL, pipelines |
| Depth | Business insights | Production-grade code |

---

### Session 2: The Multiplier Effect

#### Role-Based Use Cases

**Data Engineer**
```python
# Prompt: "Create a Bronze→Silver→Gold pipeline for raw_events table"
# Genie generates full medallion architecture:

# bronze_ingest.py
from pyspark.sql import functions as F
raw = spark.read.format("cloudFiles").option("cloudFiles.format", "json").load("/raw/events/")
(raw.withColumn("_ingest_ts", F.current_timestamp())
    .write.format("delta").mode("append").saveAsTable("bronze.raw_events"))

# silver_clean.py  
bronze = spark.table("bronze.raw_events")
silver = (bronze
  .dropDuplicates(["event_id"])
  .filter(F.col("event_type").isNotNull())
  .withColumn("event_date", F.to_date("event_timestamp")))
silver.write.format("delta").mode("overwrite").saveAsTable("silver.events_clean")

# gold_aggregate.py
(spark.table("silver.events_clean")
  .groupBy("event_type", "event_date")
  .agg(F.count("*").alias("event_count"))
  .write.format("delta").mode("overwrite").saveAsTable("gold.daily_event_summary"))
```

**ML Engineer**
```python
# Prompt: "Feature engineering for customer churn: recency, frequency, monetary from orders table"
from pyspark.sql import functions as F, Window

orders = spark.table("prod.gold.orders")
snapshot_date = F.lit("2024-12-31").cast("date")

features = (orders
  .groupBy("customer_id")
  .agg(
    F.datediff(snapshot_date, F.max("order_date")).alias("recency_days"),
    F.count("order_id").alias("frequency"),
    F.sum("amount").alias("monetary_value"),
    F.avg("amount").alias("avg_order_value"),
    F.stddev("amount").alias("stddev_order_value"),
  ))

features.write.format("delta").mode("overwrite").saveAsTable("ml.customer_rfm_features")
```

**Analyst**
```python
# Using Genie SDK — NL to SQL
from databricks.sdk import WorkspaceClient
import time

w = WorkspaceClient()

prompt = """
Show monthly active users for the past 12 months.
An active user made at least one purchase in the month.
Break down by subscription tier. Show MoM change %.
"""

response = w.genie.execute_message_query(
    space_id="YOUR_GENIE_SPACE_ID",
    conversation_id="session-001",
    message=prompt
)

# Poll for result
while True:
    status = w.genie.get_message_query_result(
        space_id="YOUR_GENIE_SPACE_ID",
        conversation_id="session-001",
        message_id=response.message_id
    )
    if status.status.query_state in ("SUCCEEDED", "FAILED"):
        break
    time.sleep(1)

df = status.result.as_pandas()
print(df)
```

**Architect**
```hcl
# Prompt: "Terraform for Databricks workspace with Unity Catalog and private networking"
# Genie generates:
resource "databricks_metastore" "main" {
  name          = "prod-metastore"
  region        = var.region
  owner         = var.admin_group
  force_destroy = false
}

resource "databricks_workspace" "main" {
  resource_group_name = var.resource_group
  location            = var.location
  sku                 = "premium"

  custom_private_subnet_name         = azurerm_subnet.private.name
  custom_virtual_network_id          = azurerm_virtual_network.main.id
  no_public_ip                       = true
  public_network_access_enabled      = false
}
```

---

### Session 3: Workspace Readiness & Getting Started

#### Checklist Before Going Live

- [ ] Databricks Runtime 14.3 LTS or later (Genie Code requires this)
- [ ] Unity Catalog enabled on workspace
- [ ] Genie feature flag enabled (Settings → Preview Features → Genie Code)
- [ ] Databricks SDK installed: `pip install databricks-sdk>=0.28`
- [ ] IAM: users assigned `CAN_USE` on Genie space

#### Delta Table Performance Tips (Genie-Suggested)

```sql
-- Optimize and index your most-queried tables
OPTIMIZE prod.gold.orders ZORDER BY (order_date, customer_id);

-- Vacuum old files (default 7-day retention)
VACUUM prod.gold.orders RETAIN 168 HOURS;

-- Auto-optimize on write (set at table level)
ALTER TABLE prod.gold.orders
SET TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true',
                   'delta.autoOptimize.autoCompact'   = 'true');
```

---

## Quick Reference Card

### Copilot Shortcuts

| Action | Shortcut |
|---|---|
| Accept suggestion | `Tab` |
| Dismiss suggestion | `Esc` |
| Next suggestion | `Alt + ]` |
| Open Copilot Chat | `Ctrl + Shift + I` |
| Inline chat | `Ctrl + I` |
| Switch to Agent mode | Chat panel → mode dropdown → Agent |

### MCP Troubleshooting

```bash
# Check MCP server is running
curl http://localhost:3100/health

# View MCP logs in VS Code
# Output panel → GitHub Copilot (MCP)

# Restart MCP server
pkill -f "node mcp-server/index.js"
node mcp-server/index.js &
```

### Useful Genie Code Prompts

| Goal | Prompt |
|---|---|
| Understand a table | "Describe the schema and typical use of `gold.orders`" |
| Find slow queries | "Which queries against `gold.orders` ran > 5 min in the last week?" |
| Optimize a pipeline | "Review this PySpark job for performance bottlenecks" |
| Generate tests | "Write data quality tests for the `silver.events_clean` table" |

---

*Training materials version 1.0 — Generated from Training_v1.docx*
