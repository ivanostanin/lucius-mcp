# IntegrationWebhookPatchDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**disabled** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_webhook_patch_dto import IntegrationWebhookPatchDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationWebhookPatchDto from a JSON string
integration_webhook_patch_dto_instance = IntegrationWebhookPatchDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationWebhookPatchDto.to_json())

# convert the object into a dict
integration_webhook_patch_dto_dict = integration_webhook_patch_dto_instance.to_dict()
# create an instance of IntegrationWebhookPatchDto from a dict
integration_webhook_patch_dto_from_dict = IntegrationWebhookPatchDto.from_dict(integration_webhook_patch_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


