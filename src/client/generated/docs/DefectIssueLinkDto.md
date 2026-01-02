# DefectIssueLinkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**integration_id** | **int** |  | 
**name** | **str** |  | 

## Example

```python
from src.client.generated.models.defect_issue_link_dto import DefectIssueLinkDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectIssueLinkDto from a JSON string
defect_issue_link_dto_instance = DefectIssueLinkDto.from_json(json)
# print the JSON string representation of the object
print(DefectIssueLinkDto.to_json())

# convert the object into a dict
defect_issue_link_dto_dict = defect_issue_link_dto_instance.to_dict()
# create an instance of DefectIssueLinkDto from a dict
defect_issue_link_dto_from_dict = DefectIssueLinkDto.from_dict(defect_issue_link_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


