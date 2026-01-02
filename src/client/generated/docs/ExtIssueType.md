# ExtIssueType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_issue_type import ExtIssueType

# TODO update the JSON string below
json = "{}"
# create an instance of ExtIssueType from a JSON string
ext_issue_type_instance = ExtIssueType.from_json(json)
# print the JSON string representation of the object
print(ExtIssueType.to_json())

# convert the object into a dict
ext_issue_type_dict = ext_issue_type_instance.to_dict()
# create an instance of ExtIssueType from a dict
ext_issue_type_from_dict = ExtIssueType.from_dict(ext_issue_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


