

update-rules:
	pipenv run python update_json.py && \
	git add rules.json rules/* && \
	git commit -m "Update rules.json" && \
	git push origin main