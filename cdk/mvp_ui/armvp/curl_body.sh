#!/bin/bash
curl --request POST \
  --url https://9so3ptq53i.execute-api.us-west-2.amazonaws.com/prod/click \
  --header 'content-type: application/json' \
  --data '{
    "resource": "test_login",
	"user_id": "zay",
	"gender": "0",
	"age": "22",
	"occupation": "12",
    "movie_id": "3094"
}'
	# "movie_id": [
	# 	3045,
	# 	1221,
	# 	3092,
	# 	3374
	# ]