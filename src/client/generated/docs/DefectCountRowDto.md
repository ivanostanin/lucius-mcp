# DefectCountRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**count** | **int** |  | [optional] 
**id** | **int** |  | [optional] 
**issue** | [**IssueDto**](IssueDto.md) |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_count_row_dto import DefectCountRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectCountRowDto from a JSON string
defect_count_row_dto_instance = DefectCountRowDto.from_json(json)
# print the JSON string representation of the object
print(DefectCountRowDto.to_json())

# convert the object into a dict
defect_count_row_dto_dict = defect_count_row_dto_instance.to_dict()
# create an instance of DefectCountRowDto from a dict
defect_count_row_dto_from_dict = DefectCountRowDto.from_dict(defect_count_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


