UPDATE answer_graph_hsitory
SET message = $1, tag = $2
WHERE answer_id = $3;