

update-rules:
	pipenv run python update_json.py && \
	git add rules.json && \
	git commit -m "Update rules.json" && \
	git push origin main