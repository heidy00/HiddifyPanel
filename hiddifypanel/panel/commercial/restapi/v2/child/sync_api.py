from hiddifypanel.models import Domain, DomainType,Proxy,StrConfig,BoolConfig
from hiddifypanel.panel.commercial.restapi.v2.admin.user_api import UserSchema
import requests
from flask.views import MethodView
from apiflask import abort
from flask import current_app as app


from hiddifypanel.panel import hiddify
from hiddifypanel.models import hconfig
from hiddifypanel.models.config_enum import ConfigEnum
from hiddifypanel.panel.commercial.restapi.v2.parent.sync_api import SyncSchema,SyncDataSchema


class SyncApi(MethodView):
    decorators = [hiddify.super_admin]
    def put(self):
        p_link = hconfig(ConfigEnum.parent_panel)
        if not p_link:
            abort(400,"The parent link is not set")

        # make proper panel api link
        p_link = p_link.removesuffix('/') + '/api/v2/parent/sync/'

        # get panel data to use in api call
        payload = self.__get_panel_data_for_api()
        
        # send request to parent
        res = requests.put(p_link, json=payload)
        if res.status_code != 200:
            abort(400,res.text)
            
        # parse parent response to get users
        res = res.json()
        hiddify.set_db_from_json(res,set_admins=True,set_users=True)
        return {'message':'ok'},200
    
    def __get_panel_data_for_api(self) -> dict:
        res = SyncSchema()
        res.unique_id = hconfig(ConfigEnum.unique_id)
        res.panel_data = SyncDataSchema()
        res.panel_data.domains = [domain.to_schema() for domain in Domain.query.all()]
        res.panel_data.proxies = [proxy.to_schema() for proxy in Proxy.query.all()]
        res.panel_data.str_configs = [str_config.to_schema() for str_config in StrConfig.query.all()]
        res.panel_data.bool_configs = [bool_config.to_schema() for bool_config in BoolConfig.query.all()]

        return res.dump(res)