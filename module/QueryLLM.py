import requests
import json
import types
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import models,hunyuan_client

class tencentLLM:
    def __init__(self, secret_id:str, secret_key:str, ):
        # self.api_key = api_key
        self.secret_id = secret_id
        self.secret_key = secret_key
        
        # 实例化认证对象
        self.cred = credential.Credential(self.secret_id,self.secret_key)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        self.httpProfile = HttpProfile()
        self.httpProfile.endpoint = "hunyuan.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        self.clientProfile = ClientProfile()
        self.clientProfile.httpProfile = self.httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        self.client = hunyuan_client.HunyuanClient(self.cred, "", self.clientProfile)

    def query(self,params) -> str:
        try:
            # 实例化请求对象
            req = models.ChatCompletionsRequest()
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个ChatCompletionsResponse的实例
            resp = self.client.ChatCompletions(req)

            if isinstance(resp, types.GeneratorType):  # 流式响应
                result = ""
                for event in resp:
                    if event:
                        # 流式相应返回的是字典类型，用下标访问
                        # event是字典，event['data']是他妈的字符串
                        result += json.loads(event['data'])['Choices'][0]['Delta']['Content']
                return result
            else:  # 非流式响应
                #非流式响应返回的是ChatCompletionsResponse对象，用（.）访问属性
                return resp.Choices[0].Message.Content
        except TencentCloudSDKException as err:
            print(err)