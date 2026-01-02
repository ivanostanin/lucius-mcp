# IssueSchemaDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**key** | **str** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.issue_schema_dto import IssueSchemaDto

# TODO update the JSON string below
json = "{}"
# create an instance of IssueSchemaDto from a JSON string
issue_schema_dto_instance = IssueSchemaDto.from_json(json)
# print the JSON string representation of the object
print(IssueSchemaDto.to_json())

# convert the object into a dict
issue_schema_dto_dict = issue_schema_dto_instance.to_dict()
# create an instance of IssueSchemaDto from a dict
issue_schema_dto_from_dict = IssueSchemaDto.from_dict(issue_schema_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


