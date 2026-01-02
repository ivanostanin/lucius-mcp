# ExtIssueLink


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**key** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**summary** | **str** |  | [optional] 
**url** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.ext_issue_link import ExtIssueLink

# TODO update the JSON string below
json = "{}"
# create an instance of ExtIssueLink from a JSON string
ext_issue_link_instance = ExtIssueLink.from_json(json)
# print the JSON string representation of the object
print(ExtIssueLink.to_json())

# convert the object into a dict
ext_issue_link_dict = ext_issue_link_instance.to_dict()
# create an instance of ExtIssueLink from a dict
ext_issue_link_from_dict = ExtIssueLink.from_dict(ext_issue_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


