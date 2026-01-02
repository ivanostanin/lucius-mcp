# DefectRowDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**issue** | [**IssueDto**](IssueDto.md) |  | [optional] 
**name** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_row_dto import DefectRowDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectRowDto from a JSON string
defect_row_dto_instance = DefectRowDto.from_json(json)
# print the JSON string representation of the object
print(DefectRowDto.to_json())

# convert the object into a dict
defect_row_dto_dict = defect_row_dto_instance.to_dict()
# create an instance of DefectRowDto from a dict
defect_row_dto_from_dict = DefectRowDto.from_dict(defect_row_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


