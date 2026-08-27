# 121XML Interactive Website - Backend Integration Guide

## Production Architecture

The interactive website (`121xml_interactive_platform.html`) connects to:

1. **MCP Server** (`xml121_mcp_server.py`) - Core operations
2. **Converter Engine** (`converter_tool.py`) - Format transformations
3. **Compaction Engine** (`xml121_compaction_engine.py`) - Lossless compression
4. **Persistence Layer** (`xml121_persistence_layer.py`) - Data storage
5. **Plugin System** (`plugin_auto_generator.py`) - Schema management

## API Endpoints Required

### Converter Endpoints

```
POST /api/convert
  - source_format: "SWIFT" | "ISO20022" | "JSON" | "HL7" | "GraphQL" | "Protobuf"
  - target_format: "121XML" | original format
  - data: raw input data
  - Returns: { status, converted_data, data_loss_percent, content_address }

POST /api/validate
  - schema_uri: "urn:121xml:payment/1.0"
  - data: object to validate
  - Returns: { valid, errors, warnings }

POST /api/address
  - data: object to address
  - type: object type
  - Returns: { address, hash, properties }

POST /api/compress
  - data: context data
  - target_tokens: desired token count
  - Returns: { compressed, tokens_freed, archived_content, reconstruction_proof }
```

### Banking Endpoints

```
POST /api/banking/simulate-swift
  - sender_account, receiver_account
  - amount, currency
  - Returns: payment flow with routing

POST /api/banking/simulate-iso20022
  - debtor_iban, creditor_iban
  - amount, currency
  - Returns: payment flow visualization
```

## Integration Steps

1. **Connect Frontend to Backend**
   ```javascript
   // Example: Connect converter to backend
   async function convertWithBackend(format, data) {
     const response = await fetch('/api/convert', {
       method: 'POST',
       body: JSON.stringify({
         source_format: format,
         target_format: '121XML',
         data: data
       })
     });
     return response.json();
   }
   ```

2. **Enable Real-time Validation**
   - Wire schema explorer to `/api/validate`
   - Show validation results live
   - Highlight errors/warnings

3. **Activate Compression Demo**
   - Connect to `/api/compress`
   - Show before/after metrics
   - Prove zero data loss with reconstruction

4. **Banking Workflow Integration**
   - Connect payment simulators to real bank data
   - Show complete routing paths
   - Demonstrate fee calculations

## Data Protection (121XML Systems)

All website operations protected by:

- **Content Addressing**: Every conversion result gets SHA256 address
- **Lossless Compression**: Automatic archive of full data
- **Persistence Layer**: All transformations stored with recovery capability
- **Audit Trail**: Immutable log of all operations

## Deployment Checklist

- [ ] Backend API server running (converter_server.py)
- [ ] MCP Server connected and responding
- [ ] Database/persistence layer initialized
- [ ] All converters tested with real data
- [ ] Authentication configured
- [ ] Rate limiting enabled
- [ ] Error handling in place
- [ ] Logging configured
- [ ] Performance tested (under load)
- [ ] Security audit passed

## Example: Complete Payment Flow

```
User Flow:
1. User enters SWIFT message in converter
2. Website calls /api/convert (SWIFT → 121XML)
3. Backend applies schema validation
4. Content address generated (SHA256)
5. Full data archived to persistence layer
6. Sparse references kept in context
7. User sees result + address + compression metrics
8. Perfect reconstruction guaranteed via archive
```

## Production Readiness

When ready to deploy:
1. Start MCP server: `python3 xml121_mcp_server.py --serve`
2. Start converter backend: `python3 converter_server.py`
3. Deploy website to 121xml.com
4. Verify all endpoints responding
5. Run integration tests
6. Monitor performance metrics

## Zero Data Loss Guarantee

Every operation:
- Preserves original data via content addressing
- Archives full state with reconstruction proof
- Enables perfect recovery
- Prevents any information loss during transformation

All protected by 121XML's lossless compaction engine.

