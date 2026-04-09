import json
with open('/a0/settings.json','r') as f:
    d=json.load(f)

# NVIDIA direct API configuration
d['chat_model_provider']='nvidia'
d['chat_model_name']='meta/llama-3.3-70b-instruct'
d['chat_model_api_base']='https://integrate.api.nvidia.com/v1'
d['chat_model_ctx_length']=8000

d['util_model_provider']='nvidia'
d['util_model_name']='meta/llama-3.3-70b-instruct'
d['util_model_api_base']='https://integrate.api.nvidia.com/v1'
d['util_model_ctx_length']=8000

d['browser_model_provider']='nvidia'
d['browser_model_name']='meta/llama-3.3-70b-instruct'
d['browser_model_api_base']='https://integrate.api.nvidia.com/v1'
d['browser_model_ctx_length']=8000

with open('/a0/settings.json','w') as f:
    json.dump(d,f,indent=2)
print('OK - NVIDIA direct configured')
