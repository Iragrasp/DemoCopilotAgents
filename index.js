#!/usr/bin/env node
/**
 * DAY 2 · SESSION 1 — MCP Server (Demo / Local Mode)
 * =====================================================
 * This server uses LOCAL mock data so the demo runs WITHOUT
 * real Azure / Databricks credentials.
 *
 * It implements the full MCP protocol over stdio so VS Code
 * Copilot Chat can connect to it and show context-aware completions.
 *
 * DEMO START COMMAND:
 *   node mcp-server/index.js
 *
 * VS Code auto-connects via .vscode/settings.json (already configured).
 *
 * HOW TO SHOW IT WORKING:
 *   1. Start this server
 *   2. Open VS Code → Copilot Chat
 *   3. Type:  "List our ADF pipelines"
 *   4. Copilot reads resources from this server and answers with real names
 */

const readline = require("readline");

// ── Mock data (mirrors what real Azure/Databricks SDKs return) ────────────────
const MOCK_ADF_PIPELINES = [
  { name: "pl_sales_blob_to_sql",    activities: 3, last_run: "2024-05-20", status: "Succeeded" },
  { name: "pl_customer_dim_refresh", activities: 2, last_run: "2024-05-21", status: "Succeeded" },
  { name: "pl_events_raw_ingest",    activities: 4, last_run: "2024-04-10", status: "Succeeded", retry_policy: false },
  { name: "pl_monthly_rollup",       activities: 5, last_run: "2024-05-22", status: "Failed"    },
];

const MOCK_DATABRICKS_SCHEMAS = [
  { catalog: "prod", schema: "bronze", tables: ["raw_events", "raw_orders", "raw_customers"] },
  { catalog: "prod", schema: "silver", tables: ["events_clean", "orders_valid", "customers_enriched"] },
  { catalog: "prod", schema: "gold",   tables: ["daily_sales", "customer_dim", "monthly_revenue_by_region"] },
];

const MOCK_SNOWFLAKE_SCHEMAS = {
  database: "PROD",
  schemas: {
    PUBLIC: {
      ORDERS:    ["order_id VARCHAR", "customer_id VARCHAR", "amount FLOAT", "order_date DATE", "status VARCHAR"],
      CUSTOMERS: ["customer_id VARCHAR", "name VARCHAR", "email VARCHAR", "subscription_tier VARCHAR"],
    }
  }
};

// ── MCP Protocol handler ──────────────────────────────────────────────────────
const RESOURCES = {
  "adf://pipelines": {
    uri:         "adf://pipelines",
    name:        "ADF Pipelines",
    description: "Azure Data Factory pipeline metadata",
    mimeType:    "application/json",
    contents: () => JSON.stringify({ pipelines: MOCK_ADF_PIPELINES }, null, 2),
  },
  "databricks://schemas": {
    uri:         "databricks://schemas",
    name:        "Databricks Unity Catalog",
    description: "Table schemas across bronze/silver/gold layers",
    mimeType:    "application/json",
    contents: () => JSON.stringify({ schemas: MOCK_DATABRICKS_SCHEMAS }, null, 2),
  },
  "snowflake://schema": {
    uri:         "snowflake://schema",
    name:        "Snowflake Schema",
    description: "Snowflake PROD database table definitions",
    mimeType:    "application/json",
    contents: () => JSON.stringify(MOCK_SNOWFLAKE_SCHEMAS, null, 2),
  },
};

const TOOLS = {
  audit_pipelines: {
    name:        "audit_pipelines",
    description: "Audit ADF pipelines for missing retry policies or stale runs (>30 days)",
    inputSchema: { type: "object", properties: {}, required: [] },
    handler: () => {
      const issues = [];
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
      for (const p of MOCK_ADF_PIPELINES) {
        if (p.retry_policy === false) issues.push({ pipeline: p.name, issue: "Missing retry policy" });
        if (new Date(p.last_run) < thirtyDaysAgo) issues.push({ pipeline: p.name, issue: `Stale: last run ${p.last_run}` });
        if (p.status === "Failed") issues.push({ pipeline: p.name, issue: "Last run failed" });
      }
      return { total_pipelines: MOCK_ADF_PIPELINES.length, issues_found: issues.length, issues };
    },
  },
  query_sales: {
    name:        "query_sales",
    description: "Query mock sales data — returns monthly totals",
    inputSchema: { type: "object", properties: { year: { type: "string" } }, required: [] },
    handler: (args) => {
      return {
        query: args.year ? `Sales for ${args.year}` : "All sales",
        results: [
          { month: "2024-01", total: 640.50,  region: "Mixed" },
          { month: "2024-02", total: 795.00,  region: "Mixed" },
          { month: "2024-03", total: 815.00,  region: "Mixed" },
          { month: "2024-04", total: 835.00,  region: "Mixed" },
          { month: "2024-05", total: 865.00,  region: "Mixed" },
        ],
      };
    },
  },
};

// ── JSON-RPC over stdio ───────────────────────────────────────────────────────
function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

function handleRequest(req) {
  const { id, method, params } = req;

  if (method === "initialize") {
    return send({ jsonrpc: "2.0", id, result: {
      protocolVersion: "2024-11-05",
      capabilities: { resources: { subscribe: false }, tools: {} },
      serverInfo: { name: "demo-mcp-server", version: "1.0.0" },
    }});
  }

  if (method === "resources/list") {
    return send({ jsonrpc: "2.0", id, result: {
      resources: Object.values(RESOURCES).map(r => ({ uri: r.uri, name: r.name, description: r.description, mimeType: r.mimeType }))
    }});
  }

  if (method === "resources/read") {
    const r = RESOURCES[params?.uri];
    if (!r) return send({ jsonrpc: "2.0", id, error: { code: -32602, message: "Unknown resource" } });
    return send({ jsonrpc: "2.0", id, result: {
      contents: [{ uri: r.uri, mimeType: r.mimeType, text: r.contents() }]
    }});
  }

  if (method === "tools/list") {
    return send({ jsonrpc: "2.0", id, result: {
      tools: Object.values(TOOLS).map(t => ({ name: t.name, description: t.description, inputSchema: t.inputSchema }))
    }});
  }

  if (method === "tools/call") {
    const tool = TOOLS[params?.name];
    if (!tool) return send({ jsonrpc: "2.0", id, error: { code: -32602, message: "Unknown tool" } });
    const result = tool.handler(params?.arguments || {});
    return send({ jsonrpc: "2.0", id, result: {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }]
    }});
  }

  if (method === "notifications/initialized") return; // no response needed

  send({ jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${method}` } });
}

// ── Start ─────────────────────────────────────────────────────────────────────
const rl = readline.createInterface({ input: process.stdin, terminal: false });
rl.on("line", line => {
  try { handleRequest(JSON.parse(line.trim())); }
  catch (e) { process.stderr.write(`MCP parse error: ${e.message}\n`); }
});

process.stderr.write("✅ MCP Demo Server started — listening on stdio\n");
process.stderr.write("   Resources: adf://pipelines, databricks://schemas, snowflake://schema\n");
process.stderr.write("   Tools:     audit_pipelines, query_sales\n");
