# PageIntegrationWebhookLogDto


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[IntegrationWebhookLogDto]**](IntegrationWebhookLogDto.md) |  | [optional] 
**empty** | **bool** |  | [optional] 
**first** | **bool** |  | [optional] 
**last** | **bool** |  | [optional] 
**number** | **int** |  | [optional] 
**number_of_elements** | **int** |  | [optional] 
**pageable** | [**Pageable**](Pageable.md) |  | [optional] 
**size** | **int** |  | [optional] 
**sort** | [**PageAccessGroupDtoSort**](PageAccessGroupDtoSort.md) |  | [optional] 
**total_elements** | **int** |  | [optional] 
**total_pages** | **int** |  | [optional] 

## Example

```python
from src.client.generated.models.page_integration_webhook_log_dto import PageIntegrationWebhookLogDto

# TODO update the JSON string below
json = "{}"
# create an instance of PageIntegrationWebhookLogDto from a JSON string
page_integration_webhook_log_dto_instance = PageIntegrationWebhookLogDto.from_json(json)
# print the JSON string representation of the object
print(PageIntegrationWebhookLogDto.to_json())

# convert the object into a dict
page_integration_webhook_log_dto_dict = page_integration_webhook_log_dto_instance.to_dict()
# create an instance of PageIntegrationWebhookLogDto from a dict
page_integration_webhook_log_dto_from_dict = PageIntegrationWebhookLogDto.from_dict(page_integration_webhook_log_dto_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


