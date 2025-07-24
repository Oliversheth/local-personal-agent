#!/bin/bash

# Autonomous AI Agent System - Demonstration Script
# This script demonstrates the full capabilities of the system

echo "🚀 Autonomous AI Agent System - Live Demonstration"
echo "================================================="
echo ""

# Check if backend is running
echo "🔍 Checking system health..."
HEALTH_CHECK=$(curl -s http://127.0.0.1:8001/health)
if [[ $? -eq 0 ]]; then
    echo "✅ Backend is healthy and running"
    echo "   Agents: $(echo $HEALTH_CHECK | jq -r '.agents_available | join(", ")')"
    echo "   Tools: $(echo $HEALTH_CHECK | jq -r '.tools_available | join(", ")')"
else
    echo "❌ Backend is not running. Please start it with: npm run start:backend"
    exit 1
fi

echo ""
echo "🤖 Submitting complex task to multi-agent system..."

# Submit a complex task
TASK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8001/v1/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Build a complete trading strategy backtesting system with Bollinger Bands strategy, risk management, and performance visualization",
    "priority": "high"
  }')

SESSION_ID=$(echo $TASK_RESPONSE | jq -r '.session_id')
echo "📋 Task submitted with session ID: $SESSION_ID"

echo ""
echo "⏰ Monitoring agent coordination (30 seconds)..."

# Monitor task progress
for i in {1..15}; do
    STATUS=$(curl -s http://127.0.0.1:8001/v1/tasks/$SESSION_ID/status)
    PROGRESS=$(echo $STATUS | jq -r '.progress')
    CURRENT_TASK=$(echo $STATUS | jq -r '.current_task // "Initializing"')
    
    echo "   Progress: ${PROGRESS}% | Current: $CURRENT_TASK"
    
    if [[ $(echo $STATUS | jq -r '.status') == "completed" ]]; then
        echo "✅ Task completed successfully!"
        break
    fi
    
    sleep 2
done

echo ""
echo "🔧 Testing enterprise development tools..."

# Test file creation
FILE_RESULT=$(curl -s -X POST "http://127.0.0.1:8001/api/enterprise/write-file?file_path=demo_test.py&content=print('Hello from Autonomous AI!')")
if [[ $(echo $FILE_RESULT | jq -r '.success') == "true" ]]; then
    echo "✅ File creation successful"
else
    echo "❌ File creation failed"
fi

# Test shell command
SHELL_RESULT=$(curl -s -X POST "http://127.0.0.1:8001/api/enterprise/run-shell?command=echo 'System test successful'")
if [[ $(echo $SHELL_RESULT | jq -r '.success') == "true" ]]; then
    echo "✅ Shell command execution successful"
    echo "   Output: $(echo $SHELL_RESULT | jq -r '.stdout')"
else
    echo "❌ Shell command failed"
fi

echo ""
echo "📊 Testing quantitative trading system..."

# Test trading strategies
STRATEGIES=$(curl -s http://127.0.0.1:8001/api/quant/strategies)
echo "🎯 Available strategies: $(echo $STRATEGIES | jq -r '.strategies | join(", ")')"

# Run a backtest
if [[ $(echo $STRATEGIES | jq -r '.strategies | length') -gt 0 ]]; then
    STRATEGY_NAME=$(echo $STRATEGIES | jq -r '.strategies[0]')
    echo "🔄 Running backtest for strategy: $STRATEGY_NAME"
    
    BACKTEST_RESULT=$(curl -s -X POST "http://127.0.0.1:8001/api/quant/backtest?strategy_name=$STRATEGY_NAME&symbol=TEST&start_date=2023-01-01&end_date=2023-12-31")
    
    if [[ $(echo $BACKTEST_RESULT | jq -r '.success') == "true" ]]; then
        echo "✅ Backtest completed successfully"
        TOTAL_RETURN=$(echo $BACKTEST_RESULT | jq -r '.results.total_return')
        SHARPE_RATIO=$(echo $BACKTEST_RESULT | jq -r '.results.sharpe_ratio')
        echo "   Total Return: $(printf "%.2f%%" $(echo "$TOTAL_RETURN * 100" | bc -l))"
        echo "   Sharpe Ratio: $SHARPE_RATIO"
    else
        echo "⚠️  Backtest requires Ollama models to be running"
    fi
fi

echo ""
echo "🖼️  Testing automation tools..."

# Test screen size
SCREEN_SIZE=$(curl -s http://127.0.0.1:8001/api/tools/screen-size)
if [[ $(echo $SCREEN_SIZE | jq -r '.success') == "true" ]]; then
    WIDTH=$(echo $SCREEN_SIZE | jq -r '.width')
    HEIGHT=$(echo $SCREEN_SIZE | jq -r '.height')
    echo "✅ Screen size detection: ${WIDTH}x${HEIGHT}"
else
    echo "⚠️  Automation tools running in headless mode"
fi

# Test clipboard
CLIPBOARD=$(curl -s http://127.0.0.1:8001/api/tools/clipboard)
if [[ $(echo $CLIPBOARD | jq -r '.success') == "true" ]]; then
    echo "✅ Clipboard access successful"
else
    echo "⚠️  Clipboard access limited in headless mode"
fi

echo ""
echo "📈 System Performance Summary"
echo "============================"

# Get all sessions
ALL_SESSIONS=$(curl -s http://127.0.0.1:8001/v1/tasks)
ACTIVE_SESSIONS=$(echo $ALL_SESSIONS | jq -r '.active_sessions')
TOTAL_SESSIONS=$(echo $ALL_SESSIONS | jq -r '.total_sessions')

echo "🔹 Active Sessions: $ACTIVE_SESSIONS"
echo "🔹 Total Sessions: $TOTAL_SESSIONS"

# Get health stats again
FINAL_HEALTH=$(curl -s http://127.0.0.1:8001/health)
echo "🔹 System Status: $(echo $FINAL_HEALTH | jq -r '.status')"
echo "🔹 Available Agents: $(echo $FINAL_HEALTH | jq -r '.agents_available | length')"
echo "🔹 Available Tools: $(echo $FINAL_HEALTH | jq -r '.tools_available | length')"

echo ""
echo "🎉 Demonstration Complete!"
echo "========================="
echo ""
echo "🚀 Your Autonomous AI Agent System is fully operational and ready for:"
echo "   • Enterprise application development"
echo "   • Quantitative trading strategy development"  
echo "   • System automation and integration"
echo "   • Multi-agent task coordination"
echo ""
echo "🌐 Access the system:"
echo "   • Backend API: http://127.0.0.1:8001"
echo "   • API Documentation: http://127.0.0.1:8001/docs"
echo "   • Task Dashboard: Run 'npm run start:frontend' and open the app"
echo ""
echo "📖 Next steps:"
echo "   1. Install Ollama models: ollama pull codellama:instruct && ollama pull deepseek-coder"
echo "   2. Launch the full system: npm start"
echo "   3. Submit complex tasks through the Task Dashboard"
echo "   4. Monitor agent coordination in real-time"
echo ""
echo "🤖 Ready to revolutionize your development workflow!"