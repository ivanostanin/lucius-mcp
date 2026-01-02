# DefectMatcherCreateDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**defect_id** | **int** |  | 
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_matcher_create_dto import DefectMatcherCreateDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectMatcherCreateDto from a JSON string
defect_matcher_create_dto_instance = DefectMatcherCreateDto.from_json(json)
# print the JSON string representation of the object
print(DefectMatcherCreateDto.to_json())

# convert the object into a dict
defect_matcher_create_dto_dict = defect_matcher_create_dto_instance.to_dict()
# create an instance of DefectMatcherCreateDto from a dict
defect_matcher_create_dto_from_dict = DefectMatcherCreateDto.from_dict(defect_matcher_create_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


