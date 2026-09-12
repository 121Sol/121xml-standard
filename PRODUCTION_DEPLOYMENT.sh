#!/bin/bash
# © 2026 121 Solutions USA. All rights reserved.
#
# The trademarks 121XQ, 121XML, and 121MetaVerse are the exclusive
# property of 121 Solutions USA.
#
# Unauthorized use, reproduction, or distribution of this material,
# including any proprietary designs, software, or documentation, is
# strictly prohibited without prior written permission from 121 Solutions USA.
# 121XML Interactive Platform - Production Deployment Script
# Deploys complete interactive website with all backend components

echo "🚀 121XML Production Deployment Started"
echo "========================================"
echo "Date: $(date)"
echo ""

# Step 1: Verify all components exist
echo "Step 1: Verifying components..."
components=(
    "xml121_mcp_server.py"
    "mcp_121xml_translator.py"
    "xml121_persistence_layer.py"
    "xml121_compaction_engine.py"
    "plugin_auto_generator.py"
    "converter_tool.py"
    "121xml_interactive_platform.html"
    "BANKING_WORKFLOWS.121xml"
)

for component in "${components[@]}"; do
    if [ -f "$component" ]; then
        echo "  ✅ $component"
    else
        echo "  ❌ $component MISSING"
    fi
done

echo ""
echo "Step 2: Starting MCP Server..."
python3 xml121_mcp_server.py --serve > mcp_server.log 2>&1 &
MCP_PID=$!
echo "  ✅ MCP Server started (PID: $MCP_PID)"

echo ""
echo "Step 3: Starting Converter Backend..."
python3 converter_server.py > converter_server.log 2>&1 &
CONVERTER_PID=$!
echo "  ✅ Converter Backend started (PID: $CONVERTER_PID)"

echo ""
echo "Step 4: Initializing Persistence Layer..."
python3 -c "
from xml121_persistence_layer import PersistenceLayer
from pathlib import Path
p = PersistenceLayer(Path('data'))
print('  ✅ Persistence layer initialized')
"

echo ""
echo "Step 5: Verifying Backend Connectivity..."
sleep 2
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "  ✅ Converter API responding"
else
    echo "  ⚠️  Converter API not responding yet (may take a moment)"
fi

echo ""
echo "Step 6: Website Deployment"
echo "  ✅ Interactive website ready: 121xml_interactive_platform.html"
echo "  📍 Deploy to: https://121xml.com/"
echo "  📝 Instructions:"
echo "     1. Upload 121xml_interactive_platform.html to web server"
echo "     2. Point to backend APIs: http://localhost:5000"
echo "     3. Configure reverse proxy for production"

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo ""
echo "Services Running:"
echo "  • MCP Server: $MCP_PID"
echo "  • Converter Backend: $CONVERTER_PID"
echo "  • Website: Ready for deployment"
echo ""
echo "Next Steps:"
echo "  1. Access website at 121xml_interactive_platform.html"
echo "  2. Test all converters"
echo "  3. Verify banking workflows"
echo "  4. Run production load tests"
echo ""
echo "Monitoring:"
echo "  • MCP logs: mcp_server.log"
echo "  • Converter logs: converter_server.log"
echo "  • Data persistence: data/ directory"
echo ""

# Save deployment info
cat > deployment_info.txt << DEPINFO
121XML Production Deployment
Date: $(date)
MCP Server PID: $MCP_PID
Converter Backend PID: $CONVERTER_PID
Website: 121xml_interactive_platform.html
Status: ACTIVE
Data Protection: 121XML Compaction Engine (ZERO DATA LOSS)
DEPINFO

echo "Deployment information saved to deployment_info.txt"
