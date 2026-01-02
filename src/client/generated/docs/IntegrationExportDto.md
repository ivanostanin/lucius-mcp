# IntegrationExportDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_date** | **int** |  | [optional] 
**disable_launch_sync** | **bool** |  | [optional] 
**disable_tc_create** | **bool** |  | [optional] 
**disabled** | **bool** |  | [optional] 
**id** | **int** |  | [optional] 
**integration_id** | **int** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**launch_aql** | **str** |  | [optional] 
**notification_email** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**project_key** | **str** |  | [optional] 
**settings** | **object** |  | [optional] 
**sync_delay_sec** | **int** |  | [optional] 
**tc_aql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_export_dto import IntegrationExportDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationExportDto from a JSON string
integration_export_dto_instance = IntegrationExportDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationExportDto.to_json())

# convert the object into a dict
integration_export_dto_dict = integration_export_dto_instance.to_dict()
# create an instance of IntegrationExportDto from a dict
integration_export_dto_from_dict = IntegrationExportDto.from_dict(integration_export_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


