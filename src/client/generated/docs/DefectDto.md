# DefectDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**closed** | **bool** |  | [optional] 
**created_date** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**description_html** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**issue** | [**IssueDto**](IssueDto.md) |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.defect_dto import DefectDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectDto from a JSON string
defect_dto_instance = DefectDto.from_json(json)
# print the JSON string representation of the object
print(DefectDto.to_json())

# convert the object into a dict
defect_dto_dict = defect_dto_instance.to_dict()
# create an instance of DefectDto from a dict
defect_dto_from_dict = DefectDto.from_dict(defect_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


