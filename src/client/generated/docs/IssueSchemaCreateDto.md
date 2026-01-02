# IssueSchemaCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 
**key** | **str** |  | 
**project_id** | **int** |  | 

## Example

```python
from src.client.generated.models.issue_schema_create_dto import IssueSchemaCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of IssueSchemaCreateDto from a JSON string
issue_schema_create_dto_instance = IssueSchemaCreateDto.from_json(json)
# print the JSON string representation of the object
print(IssueSchemaCreateDto.to_json())

# convert the object into a dict
issue_schema_create_dto_dict = issue_schema_create_dto_instance.to_dict()
# create an instance of IssueSchemaCreateDto from a dict
issue_schema_create_dto_from_dict = IssueSchemaCreateDto.from_dict(issue_schema_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


