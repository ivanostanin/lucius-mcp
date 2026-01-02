# IssuePatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.issue_patch_dto import IssuePatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of IssuePatchDto from a JSON string
issue_patch_dto_instance = IssuePatchDto.from_json(json)
# print the JSON string representation of the object
print(IssuePatchDto.to_json())

# convert the object into a dict
issue_patch_dto_dict = issue_patch_dto_instance.to_dict()
# create an instance of IssuePatchDto from a dict
issue_patch_dto_from_dict = IssuePatchDto.from_dict(issue_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


