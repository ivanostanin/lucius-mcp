# IssueDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**display_name** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**integration_type** | [**IntegrationTypeDto**](IntegrationTypeDto.md) |  | [optional] 
**name** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**summary** | **str** |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.issue_dto import IssueDto

# TODO update the JSON string below
json = "{}"
# create an instance of IssueDto from a JSON string
issue_dto_instance = IssueDto.from_json(json)
# print the JSON string representation of the object
print(IssueDto.to_json())

# convert the object into a dict
issue_dto_dict = issue_dto_instance.to_dict()
# create an instance of IssueDto from a dict
issue_dto_from_dict = IssueDto.from_dict(issue_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


