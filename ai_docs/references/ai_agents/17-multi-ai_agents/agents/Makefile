spending-snapshot:
	uv run adk api_server spending_snapshot_agent --allow_origins="*" --port=8081

spending-snapshot-dev:
	uv run adk web spending_snapshot_agent

perks-snapshot:
	uv run adk api_server perks_snapshot_agent --allow_origins="*" --port=8082

perks-snapshot-dev:
	uv run adk web perks_snapshot_agent

portfolio-snapshot:
	uv run adk api_server portfolio_snapshot_agent --allow_origins="*" --port=8083

portfolio-snapshot-dev:
	uv run adk web portfolio_snapshot_agent

goals-snapshot:
	uv run adk api_server goals_snapshot_agent --allow_origins="*" --port=8084

goals-snapshot-dev:
	uv run adk web goals_snapshot_agent

advisors-snapshot:
	uv run adk api_server advisors_snapshot_agent --allow_origins="*" --port=8085

advisors-snapshot-dev:
	uv run adk web advisors_snapshot_agent

chat-agent:
	uv run adk api_server chat --allow_origins="*" --port=8090

chat-agent-dev:
	uv run adk web chat 

agents:
	make spending-snapshot & make chat-agent & make perks-snapshot & make portfolio-snapshot & make advisors-snapshot
