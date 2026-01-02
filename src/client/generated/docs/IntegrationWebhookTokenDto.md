# IntegrationWebhookTokenDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**disabled** | **bool** |  | [optional] 
**first_eight** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**token** | **str** |  | [optional] 

## Example

```python
from src.client.generated.models.integration_webhook_token_dto import IntegrationWebhookTokenDto

# TODO update the JSON string below
json = "{}"
# create an instance of IntegrationWebhookTokenDto from a JSON string
integration_webhook_token_dto_instance = IntegrationWebhookTokenDto.from_json(json)
# print the JSON string representation of the object
print(IntegrationWebhookTokenDto.to_json())

# convert the object into a dict
integration_webhook_token_dto_dict = integration_webhook_token_dto_instance.to_dict()
# create an instance of IntegrationWebhookTokenDto from a dict
integration_webhook_token_dto_from_dict = IntegrationWebhookTokenDto.from_dict(integration_webhook_token_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


