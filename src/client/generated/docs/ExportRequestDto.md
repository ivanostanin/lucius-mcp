# ExportRequestDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**description** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**shared** | **bool** |  | [optional] 
**status** | [**ExportStatus**](ExportStatus.md) |  | [optional] 
**storage_key** | **str** |  | [optional] 
**type** | [**ExportType**](ExportType.md) |  | [optional] 

## Example

```python
from src.client.generated.models.export_request_dto import ExportRequestDto

# TODO update the JSON string below
json = "{}"
# create an instance of ExportRequestDto from a JSON string
export_request_dto_instance = ExportRequestDto.from_json(json)
# print the JSON string representation of the object
print(ExportRequestDto.to_json())

# convert the object into a dict
export_request_dto_dict = export_request_dto_instance.to_dict()
# create an instance of ExportRequestDto from a dict
export_request_dto_from_dict = ExportRequestDto.from_dict(export_request_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


