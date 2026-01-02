# DefectMatcherDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**defect_id** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**message_regex** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**trace_regex** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_matcher_dto import DefectMatcherDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectMatcherDto from a JSON string
defect_matcher_dto_instance = DefectMatcherDto.from_json(json)
# print the JSON string representation of the object
print(DefectMatcherDto.to_json())

# convert the object into a dict
defect_matcher_dto_dict = defect_matcher_dto_instance.to_dict()
# create an instance of DefectMatcherDto from a dict
defect_matcher_dto_from_dict = DefectMatcherDto.from_dict(defect_matcher_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


