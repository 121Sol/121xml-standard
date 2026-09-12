# 121xml-banking

**Description:** Banking workflow plugin for SWIFT and ISO 20022 payments

**Triggers:** 121xml-banking, banking

**Implementation:**
```

Initialize MCP Server: 121xml-banking

Capabilities:
[
  "tools",
  "resources",
  "prompts",
  "content_addressing",
  "schema_discovery",
  "lossless_compression"
]

Available Tools: 2
[
  "swift_wire_transfer",
  "iso20022_credit_transfer"
]

Available Resources: 2
[
  "banking://schema/swift-mt103",
  "banking://schema/iso20022-pacs008"
]

Available Prompts: 1
[
  "payment_workflow"
]

```

Generated: 2026-08-06T21:08:11.674241Z

---
*© 2026 121 Solutions USA. All rights reserved. The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive property of 121 Solutions USA. Unauthorized use, reproduction, or distribution of this material is strictly prohibited without prior written permission.*