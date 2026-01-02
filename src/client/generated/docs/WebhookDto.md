# WebhookDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** |  | [optional] 
**created_date** | **int** |  | [optional] 
**enabled** | **bool** |  | [optional] 
**endpoint** | **str** |  | [optional] 
**id** | **int** |  | [optional] 
**last_modified_by** | **str** |  | [optional] 
**last_modified_date** | **int** |  | [optional] 
**name** | **str** |  | [optional] 
**project_id** | **int** |  | [optional] 
**settings** | [**DefaultWebhookSettings**](DefaultWebhookSettings.md) |  | [optional] 
**with_error** | **bool** |  | [optional] 

## Example

```python
from src.client.generated.models.webhook_dto import WebhookDto

# TODO update the JSON string below
json = "{}"
# create an instance of WebhookDto from a JSON string
webhook_dto_instance = WebhookDto.from_json(json)
# print the JSON string representation of the object
print(WebhookDto.to_json())

# convert the object into a dict
webhook_dto_dict = webhook_dto_instance.to_dict()
# create an instance of WebhookDto from a dict
webhook_dto_from_dict = WebhookDto.from_dict(webhook_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


