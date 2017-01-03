CREATE OR REPLACE VIEW insights_insight_history_summary AS
SELECT max(ii.id) as id,
	ii.user_id,
	ii.insight_model_id,
	count(ii.insight_model_id) as count_insights,
	max(ii.created) as most_recent
FROM insights_insight ii
GROUP BY ii.insight_model_id, ii.user_id;