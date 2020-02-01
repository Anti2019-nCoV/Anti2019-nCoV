#!/usr/bin/python
# @Time  : 2/1/20
# @Author: liyong
from logzero import logger
from web.models.databases import User, CompanyUser, CheckInRecordModel, StatusEnum, RoleTypeEnum
from web.apps.base.status import StatusCode
from web.utils.date2json import to_json
from web.apps.user.libs.response import auth_failed, validate_error, param_missing, permission_deny
from web.apps.user.libs import utils
from datetime import datetime
from operator import itemgetter
from itertools import groupby


async def check_in(self, **kwargs):
    """员工签到"""
    keys = ['province', 'city', 'address', 'latitude', 'longitude', 'status']
    val = validate_error(keys, **kwargs)
    if not val.get('status'):
        return val
    user = self.current_user
    if not user:
        return auth_failed()
    try:
        province = kwargs.get('province')
        city = kwargs.get('city')
        district = kwargs.get('district')
        status = kwargs.get('status')
        CheckInRecordModel.add(
            userId=user.id,
            province=province,
            city=city,
            district=district,
            address=kwargs.get('address'),
            latitude=kwargs.get('latitude'),
            longitude=kwargs.get('longitude'),
            status=status
        )
        user.update(
            checkedTime=datetime.now(),
            checkedAddr=f'{province},{city},{district}',
            checkedStatus=status
        )  # 更新用户表的签到状态
        return {'status': True, 'msg': '签到成功', "code": StatusCode.success.value}
    except Exception as e:
        logger.error(f"Check In Error: {str(e)}")
        self.db.rollback()
        return {'status': False, 'msg': '签到失败', "code": StatusCode.db_error.value}


async def get_check_in_records(self, page=1, page_size=10):
    """查询个人签到轨迹"""
    user = self.current_user
    if not user:
        return auth_failed()
    rows = CheckInRecordModel.by_user_id(user.id, page, page_size)

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": to_json(rows)}


async def get_statistics_checked(self, enterprise_id=None, by_type='province'):
    """统计签到数据"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return param_missing('enterpriseId')
    company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not company_user:    # 该企业下的所有用户均可查看
        return permission_deny()
    checked = []
    raw_checked_data = User.by_enterprise_id_checked_today(enterprise_id)    # 根据企业搜索用户
    if not raw_checked_data:
        return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": checked}
    checked_data = []
    for ch in raw_checked_data:
        row = ch.to_dict()
        addr = row['checkedAddr'].split(',')
        if by_type == 'province':     # 是否根据城市统计
            row['checkedAddr'] = ''.join(s for k, s in enumerate(addr) if k < 1)
        elif by_type == 'city':     # 是否根据城市统计
            row['checkedAddr'] = ''.join(s for k, s in enumerate(addr) if k < 2)
        else:
            row['checkedAddr'] = ''.join(s for s in addr)
        checked_data.append(row)

    checked_data.sort(key=itemgetter('checkedAddr'))  # 按省排序
    for checked_address, items in groupby(checked_data, key=itemgetter('checkedAddr')):   # 按省分割
        isolated_count = 0
        suspected_count = 0
        confirmed_count = 0
        items = list(items)
        items.sort(key=itemgetter('checkedStatus'))  # 按健康状态分割
        logger.debug(f'items sort by {checked_address}: {items}')
        for status, sub_items in groupby(items, key=itemgetter('checkedStatus')):
            length = utils.get_length(sub_items)
            if status == StatusEnum.isolated:
                isolated_count = length
            elif status == StatusEnum.suspected:
                suspected_count = length
            elif status == StatusEnum.confirmed:
                confirmed_count = length

        checked_count = utils.get_length(items)  # 打卡数量
        checked.append({
            'checked_address': checked_address, 'checked_count': checked_count, 'isolated_count': isolated_count,
            'suspected_count': suspected_count, 'confirmed_count': confirmed_count
        })

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": checked}


async def get_statistics_unchecked(self, page=1, page_size=10,  enterprise_id=None):
    """统计未签到数据"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return param_missing('enterpriseId')
    company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not company_user or company_user.role_type == RoleTypeEnum.member:   # 该企业的管理员可查看
        return permission_deny()
    unchecked = []
    unchecked_data = User.by_enterprise_id_unchecked_today(enterprise_id, page, page_size)    # 根据企业搜索用户
    for item in unchecked_data:
        unchecked.append({
            "userName": item.userName,
            "employeeId": item.employeeId,
            "userPhone": item.userPhone,
            "avatarPic": item.avatarPic,
            "checkedTime": item.checkedTime,
            "checkedAddr": item.checkedAddr,
            "checkedStatus": item.checkedStatus
        })
    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": unchecked}


async def get_statistics_total(self, enterprise_id=None):
    """统计该企业所有用户个数"""
    user = self.current_user
    if not user:
        return auth_failed()
    if not enterprise_id:
        return param_missing('enterpriseId')
    company_user = CompanyUser.by_company_user_id(user.id, enterprise_id)
    if not company_user:    # 该企业下的所有用户均可查看
        return permission_deny()

    total_count = CompanyUser.count_by_company_id(enterprise_id)

    checked_data = User.by_enterprise_id_checked_today(enterprise_id)  # 根据企业搜索用户
    checked_count = len(checked_data)
    isolated_count = User.count_status_checked_today(enterprise_id, StatusEnum.isolated)
    suspected_count = User.count_status_checked_today(enterprise_id, StatusEnum.suspected)
    confirmed_count = User.count_status_checked_today(enterprise_id, StatusEnum.confirmed)

    reuslt = {
        'total_count': total_count,
        'checked_count': checked_count,
        'unchecked_count': total_count - checked_count,
        'isolated_count': isolated_count,
        'suspected_count': suspected_count,
        'confirmed_count': confirmed_count
    }

    return {"status": True, "code": StatusCode.success.value, "msg": "获取成功", "data": reuslt}
