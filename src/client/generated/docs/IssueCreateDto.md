# IssueCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.issue_create_dto import IssueCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of IssueCreateDto from a JSON string
issue_create_dto_instance = IssueCreateDto.from_json(json)
# print the JSON string representation of the object
print(IssueCreateDto.to_json())

# convert the object into a dict
issue_create_dto_dict = issue_create_dto_instance.to_dict()
# create an instance of IssueCreateDto from a dict
issue_create_dto_from_dict = IssueCreateDto.from_dict(issue_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


