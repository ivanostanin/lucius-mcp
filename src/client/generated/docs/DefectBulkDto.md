# DefectBulkDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **int** |  | 
**selection** | [**ListSelectionDto**](ListSelectionDto.md) |  | 

## Example

```python
from src.client.generated.models.defect_bulk_dto import DefectBulkDto

# TODO update the JSON string below
json = "{}"
# create an instance of DefectBulkDto from a JSON string
defect_bulk_dto_instance = DefectBulkDto.from_json(json)
# print the JSON string representation of the object
print(DefectBulkDto.to_json())

# convert the object into a dict
defect_bulk_dto_dict = defect_bulk_dto_instance.to_dict()
# create an instance of DefectBulkDto from a dict
defect_bulk_dto_from_dict = DefectBulkDto.from_dict(defect_bulk_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


