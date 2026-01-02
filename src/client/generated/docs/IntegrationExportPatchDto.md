# IntegrationExportPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**disable_launch_sync** | **bool** |  | [optional] 
**disable_tc_create** | **bool** |  | [optional] 
**disabled** | **bool** |  | [optional] 
**launch_aql** | **str** |  | [optional] 
**notification_email** | **str** |  | [optional] 
**project_key** | **str** |  | [optional] 
**settings** | **object** |  | [optional] 
**sync_delay_sec** | **int** |  | [optional] 
**tc_aql** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_export_patch_dto import IntegrationExportPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationExportPatchDto from a JSON string
integration_export_patch_dto_instance = IntegrationExportPatchDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationExportPatchDto.to_json())

# convert the object into a dict
integration_export_patch_dto_dict = integration_export_patch_dto_instance.to_dict()
# create an instance of IntegrationExportPatchDto from a dict
integration_export_patch_dto_from_dict = IntegrationExportPatchDto.from_dict(integration_export_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


