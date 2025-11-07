# ⚠️ IMPORTANT: Missing Secret in Orchestrator

The orchestrator code expects `SAFETY_API` instead of `MONITORING_API`.

## Add this secret to the Orchestrator:

**URL:** https://huggingface.co/spaces/harithkavish/harithkavish-nlweb-orchestrator/settings

**Secret:**
- **Name:** `SAFETY_API`
- **Value:** `https://harithkavish-harithkavish-nlweb-monitoring.hf.space`

## Complete Orchestrator Secrets List:

You should have these 6 secrets configured:

1. `PERCEPTION_API` = `https://harithkavish-harithkavish-nlweb-perception.hf.space`
2. `MEMORY_API` = `https://harithkavish-harithkavish-nlweb-memory.hf.space`
3. `REASONING_API` = `https://harithkavish-harithkavish-nlweb-reasoning.hf.space`
4. `EXECUTION_API` = `https://harithkavish-harithkavish-nlweb-execution.hf.space`
5. `MONITORING_API` = `https://harithkavish-harithkavish-nlweb-monitoring.hf.space` *(optional, not used)*
6. **`SAFETY_API`** = `https://harithkavish-harithkavish-nlweb-monitoring.hf.space` ✅ **ADD THIS ONE**

After adding `SAFETY_API`, the orchestrator will restart and the full system will work!
