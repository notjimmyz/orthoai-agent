# Troubleshooting AgentBeats Assessment Errors

## Error: `assert cagent_id is not None`

This error occurs when AgentBeats tries to gather agent instances for an assessment but cannot identify one of the agents.

### Common Causes

1. **Agents Not Properly Registered**
   - Both agents (green and white) must be submitted/registered to AgentBeats before running assessments
   - Verify both agents appear in your AgentBeats dashboard

2. **Incorrect Agent URLs in Assessment Configuration**
   - The assessment configuration must reference the correct agent URLs
   - URLs must match exactly what was registered (including protocol: `https://` vs `http://`)
   - Check that URLs are accessible (not localhost unless running locally)

3. **Agents Not Accessible**
   - Agents must be running and accessible at their registered URLs
   - Test agent cards are accessible:
     ```bash
     curl https://your-green-agent-url/.well-known/agent-card.json
     curl https://your-white-agent-url/.well-known/agent-card.json
     ```

4. **AgentBeats Controller Not Running**
   - If using the controller, ensure it's running: `agentbeats run_ctrl`
   - The controller manages agent lifecycle and proxying

### Steps to Fix

1. **Verify Agent Registration**
   - Log into AgentBeats dashboard
   - Check that both green and white agents are listed
   - Verify agent URLs are correct and accessible

2. **Check Assessment Configuration**
   - In AgentBeats, verify the assessment references:
     - Green agent URL (controller URL if using controller)
     - White agent URL (controller URL if using controller)
   - Ensure URLs match registered agent URLs exactly

3. **Verify Agents Are Running**
   - Green agent should be running (port 9001 or configured port)
   - White agent should be running (port 9002 or configured port)
   - If using controller, controller should be running (port 8030 or configured port)

4. **Test Agent Accessibility**
   ```bash
   # Test green agent card
   curl https://your-green-agent-url/.well-known/agent-card.json
   
   # Test white agent card
   curl https://your-white-agent-url/.well-known/agent-card.json
   
   # Both should return valid JSON
   ```

5. **Check Environment Variables**
   - `CLOUDRUN_HOST`: Should match your tunnel URL (if using Cloudflare tunnel)
   - `HOST`: Should be set by controller (usually "localhost")
   - `AGENT_PORT`: Should be set by controller (usually 9001 or 9002)
   - `PORT`: Controller port (usually 8030)

### Using AgentBeats Controller

If you're using the AgentBeats controller:

1. **Start Controller**
   ```bash
   agentbeats run_ctrl
   ```

2. **Ensure run.sh is Executable**
   ```bash
   chmod +x run.sh
   ```

3. **Controller Will:**
   - Start agents using `run.sh`
   - Set `HOST` and `AGENT_PORT` environment variables
   - Proxy requests to agents
   - Provide management UI

4. **Use Controller URL in Assessment**
   - Assessment should reference controller URL, not direct agent URLs
   - Controller URL format: `https://your-controller-url`

### Debugging Checklist

- [ ] Both agents are registered in AgentBeats dashboard
- [ ] Agent URLs in assessment match registered URLs exactly
- [ ] Agents are running and accessible
- [ ] Agent cards are accessible at `/.well-known/agent-card.json`
- [ ] Controller is running (if using controller)
- [ ] Environment variables are set correctly
- [ ] Cloudflare tunnel is running (if using tunnel)
- [ ] No firewall blocking access to agent ports

### Getting More Information

If the error persists:

1. Check AgentBeats logs for more details
2. Verify agent registration IDs match assessment configuration
3. Test agent connectivity manually using curl
4. Check if agents respond to health checks (if implemented)
5. Contact AgentBeats support: `sec+agentbeats@berkeley.edu`

