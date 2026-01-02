# IntegrationWebhookLogDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **str** |  | [optional] 
**content_type** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**webhook_id** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_webhook_log_dto import IntegrationWebhookLogDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationWebhookLogDto from a JSON string
integration_webhook_log_dto_instance = IntegrationWebhookLogDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationWebhookLogDto.to_json())

# convert the object into a dict
integration_webhook_log_dto_dict = integration_webhook_log_dto_instance.to_dict()
# create an instance of IntegrationWebhookLogDto from a dict
integration_webhook_log_dto_from_dict = IntegrationWebhookLogDto.from_dict(integration_webhook_log_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


