# project description
allure testops mcp server

allure testops api
- description - https://docs.qameta.io/allure-testops/advanced/api/
- openapi 3.1 spec json - openapi/allure-testops-service/rs.json

# requirements
## p0
- CRUD for test cases with all related metadata except shared steps
- python code to access testops api is denerated from openapi spec
- stdio, streamable http support 
- testops api token, project id could be set on start or traversed from llm input as an optional parameters
- all functions are thoroughly documented to be understandable by llms
- prompts explained
- test case create and update functions should allow doing all necessary operations to have complete test case. i.e. it should have:
  - name
  - description, precondition
  - steps
  - checks and expected results
  - tags
  - custom fields
  - attachments
- allure id should be returned after successful test case creation
- code is properly tested, test coverage is > 85%
- fully typed
- existing test cases as resources
- shared steps crud, shared step support in testcase crud


## p1
- ci/cd in github
- docker image, helm chart
- test search
- test hierarchy 
- launches crud
-

## p2
- test plans crud
- defects crud
- tls termination
- oauth/api keys
- skills

# tech stack
server:
python, uv, ruff, mcp
uvicorn, starlette
pydantic

tests:
pytest, allure

ci/cd
github, act

